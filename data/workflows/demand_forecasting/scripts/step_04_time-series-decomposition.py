#!/usr/bin/env python3
"""Step 4: Time Series Decomposition — Analyze demand trends by SKU."""
import argparse, os, json
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser(); p.add_argument("--data_dir", default="../data"); p.add_argument("--output_dir", default=".")
    args = p.parse_args(); os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 60); print("STEP 4: Time Series Decomposition"); print("=" * 60)

    df = pd.read_parquet(os.path.join(args.output_dir, "cleaned_data.parquet"))
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["year_month"] = df["order_date"].dt.to_period("M")

    # Monthly demand by SKU
    monthly = df.groupby(["year_month", "sku_id"])["quantity"].sum().reset_index()
    monthly["year_month"] = monthly["year_month"].astype(str)

    # Trend analysis for top SKUs
    top_skus = df.groupby("sku_id")["quantity"].sum().nlargest(9).index.tolist()
    fig, axes = plt.subplots(3, 3, figsize=(14, 10))
    for i, sku in enumerate(top_skus):
        sku_data = monthly[monthly["sku_id"] == sku].copy()
        sku_data = sku_data.sort_values("year_month")
        r, c = i // 3, i % 3
        axes[r, c].plot(range(len(sku_data)), sku_data["quantity"].values, "o-", color="#3498db", lw=1.5, markersize=4)
        axes[r, c].set_title(f"{sku}", fontsize=9)
        axes[r, c].set_xticks([])
    plt.suptitle("Monthly Demand — Top 9 SKUs", fontweight="bold")
    plt.tight_layout(); fig.savefig(os.path.join(args.output_dir, "step04_decomposition.png"), dpi=120); plt.close()

    # Seasonal indices
    df["month"] = df["order_date"].dt.month
    seasonal = df.groupby("month")["quantity"].mean()
    seasonal_idx = (seasonal / seasonal.mean()).round(2)
    print(f"\n📊 Seasonal indices: {seasonal_idx.to_dict()}")
    print(f"   Peak month: {seasonal_idx.idxmax()} ({seasonal_idx.max():.2f})")
    print(f"   Trough month: {seasonal_idx.idxmin()} ({seasonal_idx.min():.2f})")

    with open(os.path.join(args.output_dir, "seasonal_indices.json"), "w") as f: json.dump(seasonal_idx.to_dict(), f, default=str, indent=2)
    monthly.to_parquet(os.path.join(args.output_dir, "monthly_demand.parquet"), index=False)
    print("✅ Step 4 complete")
if __name__ == "__main__": main()
