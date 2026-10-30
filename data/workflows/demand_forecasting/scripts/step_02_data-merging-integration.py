#!/usr/bin/env python3
"""Step 2: Data Merging & Integration — Merge inventory, orders, suppliers."""
import argparse, os, json
import pandas as pd, numpy as np

def main():
    p = argparse.ArgumentParser(); p.add_argument("--data_dir", default="../data"); p.add_argument("--output_dir", default=".")
    args = p.parse_args(); os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 60); print("STEP 2: Data Merging & Integration"); print("=" * 60)

    inv = pd.read_csv(os.path.join(args.data_dir, "inventory.csv"))
    with open(os.path.join(args.data_dir, "sales_orders.json")) as f: orders = pd.DataFrame(json.load(f))
    supp = pd.read_excel(os.path.join(args.data_dir, "suppliers.xlsx"))

    # Merge orders ← inventory for product details
    merged = orders.merge(inv, on="sku_id", how="left", suffixes=("", "_inv"))
    drop = [c for c in merged.columns if c.endswith("_inv")]; merged = merged.drop(columns=drop) if drop else merged
    # Merge ← suppliers
    merged = merged.merge(supp, left_on="supplier", right_on="supplier_name", how="left", suffixes=("", "_sup"))
    drop2 = [c for c in merged.columns if c.endswith("_sup")] + ["supplier_name"]
    merged = merged.drop(columns=[c for c in drop2 if c in merged.columns])

    profit = merged["unit_price"] - merged["unit_cost"]
    merged["profit_margin"] = (profit / merged["unit_price"].clip(lower=0.01) * 100).clip(0, 200)

    print(f"\n📊 Merged: {len(merged)} orders × {len(merged.columns)} cols")
    print(f"   SKU match rate: {merged['product_name'].notna().mean()*100:.0f}%")
    print(f"   Supplier match rate: {merged['supplier'].notna().mean()*100:.0f}%")

    merged.to_parquet(os.path.join(args.output_dir, "merged_data.parquet"), index=False)
    with open(os.path.join(args.output_dir, "merge_summary.json"), "w") as f: json.dump({"rows": len(merged), "cols": len(merged.columns)}, f, default=str)
    print("✅ Step 2 complete")
if __name__ == "__main__": main()
