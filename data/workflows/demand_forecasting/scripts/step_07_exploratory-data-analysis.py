#!/usr/bin/env python3
"""Step 7-8: EDA + Demand Pattern Visualizations."""
import argparse, os, json
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser(); p.add_argument("--data_dir", default="../data"); p.add_argument("--output_dir", default=".")
    args = p.parse_args(); os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 60); print("STEPS 7-8: EDA & Demand Pattern Visualization"); print("=" * 60)

    df = pd.read_parquet(os.path.join(args.output_dir, "feature_engineered.parquet"))
    df["order_date"] = pd.to_datetime(df["order_date"])

    # EDA
    print(f"\n📊 Demand by category:")
    for cat in df["category"].value_counts().index:
        cat_df = df[df["category"] == cat]; print(f"   {cat}: {cat_df['quantity'].sum():,} units, ${cat_df['total_amount'].sum():,.0f}")

    # Visualizations
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.suptitle("Demand & Inventory Analysis Dashboard", fontweight="bold", fontsize=16)

    # 1. Monthly total quantity trend
    monthly = df.groupby(df["order_date"].dt.to_period("M"))["quantity"].sum()
    axes[0, 0].plot(range(len(monthly)), monthly.values, "o-", color="#3498db", lw=2, markersize=4)
    axes[0, 0].set_title("Monthly Demand Trend"); axes[0, 0].set_xticks([])

    # 2. Revenue by category
    df.groupby("category")["total_amount"].sum().sort_values().plot(kind="barh", ax=axes[0, 1], color="#2ecc71", edgecolor="white")
    axes[0, 1].set_title("Total Revenue by Category")

    # 3. Seasonal heatmap (month × category)
    if df["category"].nunique() <= 8:
        heatmap = df.pivot_table(values="quantity", index="category", columns="month", aggfunc="mean")
        if not heatmap.empty:
            im = axes[0, 2].imshow(heatmap.values, aspect="auto", cmap="YlOrRd")
            axes[0, 2].set_xticks(range(12)); axes[0, 2].set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'])
            axes[0, 2].set_yticks(range(len(heatmap))); axes[0, 2].set_yticklabels(heatmap.index)
            axes[0, 2].set_title("Demand Heatmap: Category × Month"); plt.colorbar(im, ax=axes[0, 2])

    # 4. Stock vs demand scatter
    axes[1, 0].scatter(df["current_stock"], df["quantity"], c=df["is_seasonal"], cmap="coolwarm", alpha=0.3, s=10, edgecolors="none")
    axes[1, 0].set_title("Current Stock vs Order Quantity"); axes[1, 0].set_xlabel("Current Stock"); axes[1, 0].set_ylabel("Order Qty")

    # 5. Region revenue
    df.groupby("region")["total_amount"].sum().sort_values().plot(kind="bar", ax=axes[1, 1], color="#9b59b6", edgecolor="white")
    axes[1, 1].set_title("Revenue by Region"); axes[1, 1].tick_params(rotation=30)

    # 6. Profit margin distribution
    if "profit_margin" in df.columns:
        axes[1, 2].hist(df["profit_margin"].clip(0, 100), bins=40, color="#e67e22", edgecolor="white")
        axes[1, 2].set_title("Profit Margin Distribution"); axes[1, 2].set_xlabel("Margin (%)")

    plt.tight_layout(); fig.savefig(os.path.join(args.output_dir, "step07_demand_patterns.png"), dpi=120, bbox_inches="tight"); plt.close()
    print("📊 Dashboard generated"); print("✅ Steps 7-8 complete")
if __name__ == "__main__": main()
