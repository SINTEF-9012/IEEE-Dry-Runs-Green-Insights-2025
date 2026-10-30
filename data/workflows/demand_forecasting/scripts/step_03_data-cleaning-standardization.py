#!/usr/bin/env python3
"""Step 3: Data Cleaning & Standardization."""
import argparse, os, json
import pandas as pd, numpy as np

def main():
    p = argparse.ArgumentParser(); p.add_argument("--data_dir", default="../data"); p.add_argument("--output_dir", default=".")
    args = p.parse_args(); os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 60); print("STEP 3: Data Cleaning & Standardization"); print("=" * 60)

    df = pd.read_parquet(os.path.join(args.output_dir, "merged_data.parquet"))
    before_nulls = df.isnull().sum().sum()

    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']: df[col] = df[col].fillna(df[col].median())
        elif df[col].dtype == 'object': df[col] = df[col].fillna("Unknown")

    for col in df.columns:
        if df[col].dtype == 'object': df[col] = df[col].astype(str).str.strip()
    for col in df.select_dtypes(include=['float64', 'int64']).columns:
        if col in ['sku_id', 'order_id'] or df[col].nunique() < 5: continue
        p99 = df[col].quantile(0.99)
        if (df[col] > p99).sum() > 0: df[col] = df[col].clip(upper=p99)

    print(f"   Nulls: {before_nulls} → {df.isnull().sum().sum()}")
    df.to_parquet(os.path.join(args.output_dir, "cleaned_data.parquet"), index=False)
    print("✅ Step 3 complete")
if __name__ == "__main__": main()
