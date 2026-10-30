#!/usr/bin/env python3
"""Generate synthetic demand-forecasting data scaled to a target size, written to bigdata/.

Reads data/ to learn realistic value ranges and per-record byte cost, then scales
the SKU catalog, supplier list, and order volume to approximate the requested size.
"""
import argparse
import json
import os
import random
import re
from datetime import date, timedelta

import numpy as np
import pandas as pd

CATEGORIES = ["Office", "Apparel", "Sports", "Beauty", "Electronics", "Home Goods", "Automotive", "Food"]
REGIONS = ["East", "West", "North", "South", "Central"]
COUNTRIES = ["USA", "Mexico", "China", "Vietnam"]
PAYMENT_TERMS = ["Prepaid", "Net 30", "Net 60"]
SUPPLIER_ADJECTIVES = ["Prime", "Global", "Pacific", "Fast", "Metro", "Summit", "Quality", "Eco",
                       "Apex", "Nova", "Vertex", "Atlas", "Horizon", "Cascade", "Meridian", "Ridge"]
SUPPLIER_NOUNS = ["Distributors", "Supply Co", "Trading", "Ship Inc", "Wholesale", "Logistics", "Parts Ltd", "Source"]
SEASONAL_MULTIPLIER = {11: 1.6, 12: 2.0, 1: 0.7}

MIN_ORDERS = 100
MIN_SKUS = 10
MIN_SUPPLIERS = 3

SIZE_RE = re.compile(r"^([\d.]+)\s*(KB|MB|GB)?$", re.IGNORECASE)


def parse_size(text: str) -> int:
    match = SIZE_RE.match(text.strip())
    if not match:
        raise ValueError(f"Unrecognized size '{text}'. Use e.g. 500MB, 2GB, or a plain number of MB.")
    value, unit = match.groups()
    multiplier = {"KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3, None: 1024 ** 2}[unit.upper() if unit else None]
    return int(float(value) * multiplier)


def measure_baseline(data_dir: str) -> dict:
    inv_path = os.path.join(data_dir, "inventory.csv")
    orders_path = os.path.join(data_dir, "sales_orders.json")
    supp_path = os.path.join(data_dir, "suppliers.xlsx")

    with open(orders_path) as f:
        orders = json.load(f)
    order_dates = [o["order_date"] for o in orders]

    return {
        "inventory_rows": len(pd.read_csv(inv_path)),
        "inventory_bytes": os.path.getsize(inv_path),
        "order_rows": len(orders),
        "order_bytes": os.path.getsize(orders_path),
        "order_date_span_days": (date.fromisoformat(max(order_dates)) - date.fromisoformat(min(order_dates))).days + 1,
        "supplier_rows": len(pd.read_excel(supp_path)),
        "supplier_bytes": os.path.getsize(supp_path),
    }


def generate_supplier_names(count: int, rng: random.Random) -> list[str]:
    names = set()
    while len(names) < count:
        names.add(f"{rng.choice(SUPPLIER_ADJECTIVES)} {rng.choice(SUPPLIER_NOUNS)}")
    return sorted(names)


def generate_suppliers(count: int, rng: random.Random) -> pd.DataFrame:
    names = generate_supplier_names(count, rng)
    return pd.DataFrame({
        "supplier_name": names,
        "rating": [round(rng.uniform(2.0, 5.0), 1) for _ in names],
        "on_time_delivery_pct": [round(rng.uniform(70.0, 98.0), 1) for _ in names],
        "avg_lead_time_days": [rng.randint(3, 21) for _ in names],
        "minimum_order_qty": [rng.randint(10, 100) for _ in names],
        "country": [rng.choice(COUNTRIES) for _ in names],
        "payment_terms": [rng.choice(PAYMENT_TERMS) for _ in names],
    })


def generate_inventory(count: int, supplier_names: list[str], rng: random.Random) -> pd.DataFrame:
    sku_digits = max(4, len(str(count)))
    rows = []
    for i in range(1, count + 1):
        category = rng.choice(CATEGORIES)
        unit_cost = round(rng.uniform(5.99, 199.56), 2)
        unit_price = round(unit_cost * rng.uniform(1.8, 3.2), 2)
        rows.append({
            "sku_id": f"SKU_{i:0{sku_digits}d}",
            "product_name": f"{category} Item {i}",
            "category": category,
            "unit_cost": unit_cost,
            "unit_price": unit_price,
            "supplier": rng.choice(supplier_names),
            "lead_time_days": rng.randint(3, 30),
            "reorder_point": rng.randint(28, 194),
            "safety_stock": rng.randint(11, 49),
            "current_stock": rng.randint(36, 510),
            "is_seasonal": rng.choice([0, 1]),
        })
    return pd.DataFrame(rows)


def generate_orders(count: int, inventory: pd.DataFrame, days_per_order_per_sku: float,
                     rng: random.Random, np_rng: np.random.Generator) -> list[dict]:
    # Keep order density (orders/day/SKU) roughly constant as the catalog grows.
    orders_per_sku = count / max(1, len(inventory))
    days = max(365, round(orders_per_sku * days_per_order_per_sku))
    end = date(2024, 12, 31)
    start = end - timedelta(days=days - 1)
    span = (end - start).days

    sku_ids = inventory["sku_id"].tolist()
    prices = dict(zip(inventory["sku_id"], inventory["unit_price"]))
    seasonal = dict(zip(inventory["sku_id"], inventory["is_seasonal"]))
    quantities = np_rng.lognormal(mean=5.07, sigma=0.8, size=count)

    order_digits = max(6, len(str(count)))
    orders = []
    for i in range(1, count + 1):
        sku_id = rng.choice(sku_ids)
        order_date = start + timedelta(days=rng.randint(0, span))
        qty = max(1, int(quantities[i - 1]))
        if seasonal.get(sku_id) and order_date.month in SEASONAL_MULTIPLIER:
            qty = max(1, int(qty * SEASONAL_MULTIPLIER[order_date.month]))
        unit_price = prices[sku_id]
        orders.append({
            "order_id": f"ORD_{i:0{order_digits}d}",
            "sku_id": sku_id,
            "order_date": order_date.isoformat(),
            "quantity": qty,
            "unit_price": unit_price,
            "total_amount": round(qty * unit_price, 2),
            "region": rng.choice(REGIONS),
        })
    return orders


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("size", help="Target synthetic dataset size, e.g. 50MB, 2GB, or a plain number of MB")
    parser.add_argument("--data-dir", default=os.path.join(os.path.dirname(__file__), "data"),
                         help="Source dataset used to derive value ranges and per-record size (default: ./data)")
    parser.add_argument("--output-dir", default=os.path.join(os.path.dirname(__file__), "bigdata"),
                         help="Directory to write synthetic data into (default: ./bigdata)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    target_bytes = parse_size(args.size)
    baseline = measure_baseline(args.data_dir)
    base_total = baseline["inventory_bytes"] + baseline["order_bytes"] + baseline["supplier_bytes"]
    scale = target_bytes / base_total

    num_orders = max(MIN_ORDERS, round(baseline["order_rows"] * scale))
    num_skus = max(MIN_SKUS, round(baseline["inventory_rows"] * scale ** 0.5))
    num_suppliers = max(MIN_SUPPLIERS, round(baseline["supplier_rows"] * scale ** 0.25))

    rng = random.Random(args.seed)
    np_rng = np.random.default_rng(args.seed)

    days_per_order_per_sku = baseline["order_date_span_days"] * baseline["inventory_rows"] / baseline["order_rows"]

    suppliers = generate_suppliers(num_suppliers, rng)
    inventory = generate_inventory(num_skus, suppliers["supplier_name"].tolist(), rng)
    orders = generate_orders(num_orders, inventory, days_per_order_per_sku, rng, np_rng)

    os.makedirs(args.output_dir, exist_ok=True)
    inventory_path = os.path.join(args.output_dir, "inventory.csv")
    orders_path = os.path.join(args.output_dir, "sales_orders.json")
    suppliers_path = os.path.join(args.output_dir, "suppliers.xlsx")

    inventory.to_csv(inventory_path, index=False)
    with open(orders_path, "w") as f:
        json.dump(orders, f)
    suppliers.to_excel(suppliers_path, index=False)

    total_bytes = sum(os.path.getsize(p) for p in (inventory_path, orders_path, suppliers_path))
    print(f"SKUs: {num_skus:,} | Orders: {num_orders:,} | Suppliers: {num_suppliers:,}")
    print(f"Target size: {target_bytes / 1024 ** 2:.1f} MB | Actual size: {total_bytes / 1024 ** 2:.1f} MB")
    print(f"Written to {args.output_dir}/")


if __name__ == "__main__":
    main()
