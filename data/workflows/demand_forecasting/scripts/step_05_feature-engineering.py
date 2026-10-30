#!/usr/bin/env python3
"""Step 5-6: Feature Engineering — Temporal and cross-domain features."""
import argparse, os, json
import pandas as pd, numpy as np

def main():
    p = argparse.ArgumentParser(); p.add_argument("--data_dir", default="../data"); p.add_argument("--output_dir", default=".")
    args = p.parse_args(); os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 60); print("STEP 5-6: Feature Engineering"); print("=" * 60)

    df = pd.read_parquet(os.path.join(args.output_dir, "cleaned_data.parquet"))
    df["order_date"] = pd.to_datetime(df["order_date"])
    init_cols = len(df.columns)
    features = []

    # Temporal features
    df["year"] = df["order_date"].dt.year
    df["month"] = df["order_date"].dt.month
    df["quarter"] = df["order_date"].dt.quarter
    df["day_of_week"] = df["order_date"].dt.dayofweek
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)
    df["is_month_end"] = (df["order_date"].dt.day > 25).astype(int)
    features += ["year", "month", "quarter", "day_of_week", "is_weekend", "is_month_end"]

    # Cross-domain features
    df["revenue_per_unit"] = df["total_amount"] / df["quantity"].clip(lower=1)
    df["stock_velocity"] = np.where(df["lead_time_days"] > 0, df["current_stock"] / df["lead_time_days"], 0)
    df["stock_coverage_days"] = np.where(df["quantity"] > 0, df["current_stock"] / (df["quantity"] / 30), 0).clip(0, 365)
    df["needs_reorder"] = (df["current_stock"] <= df["reorder_point"]).astype(int)
    features += ["revenue_per_unit", "stock_velocity", "stock_coverage_days", "needs_reorder"]

    # Lag features (overall daily demand)
    daily = df.groupby("order_date")["quantity"].sum().reset_index().sort_values("order_date")
    daily["demand_lag_7"] = daily["quantity"].shift(7)
    daily["demand_lag_30"] = daily["quantity"].shift(30)
    daily["demand_rolling_7"] = daily["quantity"].rolling(7).mean()
    daily["demand_rolling_30"] = daily["quantity"].rolling(30).mean()
    df = df.merge(daily[["order_date", "demand_lag_7", "demand_lag_30", "demand_rolling_7", "demand_rolling_30"]], on="order_date", how="left")
    features += ["demand_lag_7", "demand_lag_30", "demand_rolling_7", "demand_rolling_30"]

    df.to_parquet(os.path.join(args.output_dir, "feature_engineered.parquet"), index=False)
    print(f"\n🔧 Created {len(features)} features: {', '.join(features[:5])}... +{len(features)-5} more")
    print(f"   Final: {len(df.columns)} columns"); print("✅ Steps 5-6 complete")
if __name__ == "__main__": main()
