#!/usr/bin/env python3
"""Step 14: Inventory Optimization — Safety stock and reorder point calculations."""
import argparse, os, json
import pandas as pd, numpy as np
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser(); p.add_argument("--data_dir", default="../data"); p.add_argument("--output_dir", default=".")
    args = p.parse_args(); os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 60); print("STEP 14: Inventory Optimization"); print("=" * 60)

    df = pd.read_parquet(os.path.join(args.output_dir, "feature_engineered.parquet"))
    df["order_date"] = pd.to_datetime(df["order_date"])

    # Per-SKU optimization
    inv = pd.read_csv(os.path.join(args.data_dir, "inventory.csv"))

    # Calculate daily demand per SKU
    sku_daily_demand = df.groupby("sku_id")["quantity"].sum() / df["order_date"].nunique()
    sku_demand_std = df.groupby("sku_id")["quantity"].std()

    # Merge with inventory
    opt = inv[["sku_id", "product_name", "category", "lead_time_days", "current_stock", "reorder_point", "safety_stock", "unit_cost"]].copy()
    opt["avg_daily_demand"] = opt["sku_id"].map(sku_daily_demand).fillna(0)
    opt["demand_std"] = opt["sku_id"].map(sku_demand_std).fillna(0)

    # Calculate optimal safety stock (z=1.65 for 95% service level)
    z = 1.65
    opt["optimal_safety_stock"] = np.ceil(z * opt["demand_std"] * np.sqrt(opt["lead_time_days"].clip(lower=1))).astype(int)
    opt["optimal_reorder_point"] = (opt["avg_daily_demand"] * opt["lead_time_days"] + opt["optimal_safety_stock"]).astype(int)

    # Flag actions
    opt["action"] = "Hold"
    opt.loc[opt["current_stock"] <= opt["optimal_safety_stock"], "action"] = "⚠️ Reorder Now"
    opt.loc[opt["current_stock"] > 2 * opt["optimal_reorder_point"], "action"] = "📦 Overstocked"

    print(f"\n📊 Inventory Optimization Results:")
    print(f"   SKUs needing reorder: {(opt['action'] == '⚠️ Reorder Now').sum()}")
    print(f"   Overstocked SKUs: {(opt['action'] == '📦 Overstocked').sum()}")
    print(f"   Healthy SKUs: {(opt['action'] == 'Hold').sum()}")

    # Holding cost simulation
    unit_holding_cost = opt["unit_cost"] * 0.25 / 365  # 25% annual holding cost per day
    current_holding = (opt["current_stock"] * unit_holding_cost).sum()
    optimal_holding = (opt["optimal_reorder_point"] * unit_holding_cost).sum()
    savings = current_holding - optimal_holding
    print(f"\n💰 Daily holding cost: ${current_holding:.0f} → ${optimal_holding:.0f} (save ${savings:.0f}/day)")

    # Viz
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(opt["current_stock"], opt["optimal_reorder_point"], c=opt["action"].map({"Hold": "#2ecc71", "⚠️ Reorder Now": "#e74c3c", "📦 Overstocked": "#f39c12"}), s=60)
    max_val = max(opt["current_stock"].max(), opt["optimal_reorder_point"].max()) * 1.1
    ax.plot([0, max_val], [0, max_val], "k--", alpha=0.3)
    ax.set_title("Current Stock vs Optimal Reorder Point"); ax.set_xlabel("Current Stock"); ax.set_ylabel("Optimal Reorder Point")
    plt.tight_layout(); fig.savefig(os.path.join(args.output_dir, "step14_inventory_optimization.png"), dpi=100); plt.close()

    opt.to_csv(os.path.join(args.output_dir, "inventory_optimization.csv"), index=False)
    with open(os.path.join(args.output_dir, "optimization_summary.json"), "w") as f: json.dump({"daily_savings": round(savings, 0), "skus_reorder": int((opt["action"] == "⚠️ Reorder Now").sum()), "skus_overstocked": int((opt["action"] == "📦 Overstocked").sum())}, f, default=str)
    print("✅ Step 14 complete")
if __name__ == "__main__": main()
