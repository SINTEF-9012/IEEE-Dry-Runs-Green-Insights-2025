#!/usr/bin/env python3
"""Step 1: Data Loading & Profiling — Load inventory, sales orders, and supplier data."""
import argparse, os, json
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser(); p.add_argument("--data_dir", default="../data"); p.add_argument("--output_dir", default=".")
    args = p.parse_args(); os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 60); print("STEP 1: Data Loading & Profiling"); print("=" * 60)

    inv = pd.read_csv(os.path.join(args.data_dir, "inventory.csv"))
    with open(os.path.join(args.data_dir, "sales_orders.json")) as f: orders = pd.DataFrame(json.load(f))
    supp = pd.read_excel(os.path.join(args.data_dir, "suppliers.xlsx"))

    for name, df in [("inventory", inv), ("sales_orders", orders), ("suppliers", supp)]:
        print(f"\n📊 {name.upper()}: {len(df)} rows × {len(df.columns)} cols | Nulls: {df.isnull().sum().sum()}")

    orders["order_date"] = pd.to_datetime(orders["order_date"])
    print(f"\n📅 Orders date range: {orders['order_date'].min().date()} to {orders['order_date'].max().date()}")
    print(f"   Unique SKUs in orders: {orders['sku_id'].nunique()} / {inv['sku_id'].nunique()} in inventory")
    print(f"   Avg order value: ${orders['total_amount'].mean():.0f}")
    print(f"   Seasonal SKUs: {inv['is_seasonal'].sum()}/{len(inv)}")

    profiling = {name: {"rows": len(df), "columns": len(df.columns)} for name, df in
                 [("inventory", inv), ("sales_orders", orders), ("suppliers", supp)]}
    with open(os.path.join(args.output_dir, "profiling_summary.json"), "w") as f: json.dump(profiling, f, default=str, indent=2)
    inv.to_parquet(os.path.join(args.output_dir, "raw_inventory.parquet"), index=False)
    orders.to_parquet(os.path.join(args.output_dir, "raw_orders.parquet"), index=False)
    supp.to_parquet(os.path.join(args.output_dir, "raw_suppliers.parquet"), index=False)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    inv.groupby("category")["current_stock"].sum().plot(kind="barh", ax=axes[0], color="#3498db", edgecolor="white")
    axes[0].set_title("Total Stock by Category")
    orders.groupby("region")["total_amount"].sum().plot(kind="barh", ax=axes[1], color="#e74c3c", edgecolor="white")
    axes[1].set_title("Total Revenue by Region")
    plt.tight_layout(); fig.savefig(os.path.join(args.output_dir, "step01_profiling.png"), dpi=100); plt.close()
    print("\n✅ Step 1 complete")
if __name__ == "__main__": main()
