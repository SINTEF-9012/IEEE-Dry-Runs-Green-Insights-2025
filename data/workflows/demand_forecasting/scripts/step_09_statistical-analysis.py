#!/usr/bin/env python3
"""Step 9-10: Inventory Visualization + Statistical Analysis."""
import argparse, os, json
import pandas as pd, numpy as np
from scipy import stats
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser(); p.add_argument("--data_dir", default="../data"); p.add_argument("--output_dir", default=".")
    args = p.parse_args(); os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 60); print("STEPS 9-10: Inventory Viz + Statistical Analysis"); print("=" * 60)

    df = pd.read_parquet(os.path.join(args.output_dir, "feature_engineered.parquet"))

    # Inventory health dashboard
    inv = pd.read_csv(os.path.join(args.data_dir, "inventory.csv"))
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Stock level vs reorder point
    inv["stock_status"] = np.where(inv["current_stock"] <= inv["safety_stock"], "Critical",
                            np.where(inv["current_stock"] <= inv["reorder_point"], "Low", "Healthy"))
    status_counts = inv["stock_status"].value_counts()
    colors = {"Critical": "#e74c3c", "Low": "#f39c12", "Healthy": "#2ecc71"}
    axes[0].bar(status_counts.index, status_counts.values, color=[colors.get(s, "gray") for s in status_counts.index], edgecolor="white")
    axes[0].set_title(f"Inventory Status ({len(inv)} SKUs)"); axes[0].set_ylabel("SKU Count")

    # Lead time vs stock
    axes[1].scatter(inv["lead_time_days"], inv["current_stock"], c=inv["is_seasonal"], cmap="coolwarm", s=60, edgecolors="white")
    axes[1].set_title("Lead Time vs Current Stock"); axes[1].set_xlabel("Lead Time (days)"); axes[1].set_ylabel("Current Stock")
    plt.tight_layout(); fig.savefig(os.path.join(args.output_dir, "step09_inventory_health.png"), dpi=120); plt.close()

    # Statistical tests
    results = []
    df["order_date"] = pd.to_datetime(df["order_date"]); df["quarter_num"] = df["order_date"].dt.quarter
    quarters = [df[df["quarter_num"] == q]["quantity"] for q in range(1, 5)]
    if all(len(q) > 0 for q in quarters):
        f_stat, p_val = stats.f_oneway(*quarters)
        results.append({"test": "ANOVA: quantity by quarter", "statistic": round(f_stat, 3), "p_value": round(p_val, 6), "significant": p_val < 0.05})
        print(f"📊 ANOVA (quarterly demand): F={f_stat:.2f}, p={p_val:.4f}")

    regions = df["region"].unique()
    if len(regions) >= 2:
        r1, r2 = df[df["region"] == regions[0]]["quantity"], df[df["region"] == regions[1]]["quantity"]
        t_stat, p_val = stats.ttest_ind(r1, r2)
        results.append({"test": f"T-test: {regions[0]} vs {regions[1]}", "statistic": round(t_stat, 3), "p_value": round(p_val, 6), "significant": p_val < 0.05})
        print(f"📊 T-test ({regions[0]} vs {regions[1]}): t={t_stat:.2f}, p={p_val:.4f}")

    # Correlation: lead time vs stock
    r, p = stats.pearsonr(inv["lead_time_days"], inv["current_stock"])
    results.append({"test": "Pearson: lead_time vs stock", "statistic": round(r, 3), "p_value": round(p, 6), "significant": p < 0.05})
    print(f"📊 Lead time vs stock: r={r:.3f}, p={p:.4f}")

    clean = []; 
    for r in results: clean.append({k: (bool(v) if isinstance(v, (np.bool_,)) else float(v) if isinstance(v, (np.floating, np.integer)) else v) for k, v in r.items()})
    with open(os.path.join(args.output_dir, "statistical_tests.json"), "w") as f: json.dump(clean, f, default=str, indent=2)
    print(f"\n📋 {sum(1 for r in results if r['significant'])}/{len(results)} tests significant"); print("✅ Steps 9-10 complete")
if __name__ == "__main__": main()
