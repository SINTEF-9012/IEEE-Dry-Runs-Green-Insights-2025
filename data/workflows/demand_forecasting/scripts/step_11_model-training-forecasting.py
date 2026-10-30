#!/usr/bin/env python3
"""Step 11-13: Demand Forecasting Models — Statistical, ML, and Ensemble."""
import argparse, os, json, pickle
import pandas as pd, numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

def main():
    p = argparse.ArgumentParser(); p.add_argument("--data_dir", default="../data"); p.add_argument("--output_dir", default=".")
    args = p.parse_args(); os.makedirs(args.output_dir, exist_ok=True)
    print("=" * 60); print("STEPS 11-13: Demand Forecasting Models"); print("=" * 60)

    df = pd.read_parquet(os.path.join(args.output_dir, "feature_engineered.parquet"))

    # Aggregate daily demand for forecasting
    daily = df.groupby("order_date")["quantity"].sum().reset_index()
    daily["day_num"] = range(len(daily))
    daily["week_num"] = daily["day_num"] // 7

    # Create features
    for lag in [1, 7, 14, 30]:
        daily[f"lag_{lag}"] = daily["quantity"].shift(lag)
    daily["rolling_7"] = daily["quantity"].rolling(7).mean()
    daily["rolling_30"] = daily["quantity"].rolling(30).mean()
    daily = daily.dropna()

    if len(daily) < 30:
        print("⚠️ Insufficient data for forecasting"); return

    X = daily[["day_num", "week_num", "lag_1", "lag_7", "lag_14", "lag_30", "rolling_7", "rolling_30"]]
    y = daily["quantity"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
    scaler = StandardScaler(); X_train_s = scaler.fit_transform(X_train); X_test_s = scaler.transform(X_test)

    models_registry = []

    # Linear Regression (baseline)
    lr = LinearRegression(); lr.fit(X_train_s, y_train)
    lr_pred = lr.predict(X_test_s)
    models_registry.append(eval_model("LinearRegression", lr_pred, y_test)); print(f"   LR: MAE={models_registry[-1]['mae']:.1f}, R²={models_registry[-1]['r2']:.3f}")

    # Ridge
    ridge = Ridge(alpha=1.0); ridge.fit(X_train_s, y_train)
    ridge_pred = ridge.predict(X_test_s)
    models_registry.append(eval_model("Ridge", ridge_pred, y_test)); print(f"   Ridge: MAE={models_registry[-1]['mae']:.1f}, R²={models_registry[-1]['r2']:.3f}")

    # Random Forest
    rf = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42, n_jobs=-1)
    rf.fit(X_train_s, y_train); rf_pred = rf.predict(X_test_s)
    models_registry.append(eval_model("RandomForest", rf_pred, y_test)); print(f"   RF: MAE={models_registry[-1]['mae']:.1f}, R²={models_registry[-1]['r2']:.3f}")

    # XGBoost
    try:
        import xgboost as xgb
        xgb_model = xgb.XGBRegressor(n_estimators=200, max_depth=6, random_state=42, verbosity=0)
        xgb_model.fit(X_train_s, y_train); xgb_pred = xgb_model.predict(X_test_s)
        models_registry.append(eval_model("XGBoost", xgb_pred, y_test)); print(f"   XGB: MAE={models_registry[-1]['mae']:.1f}, R²={models_registry[-1]['r2']:.3f}")
    except ImportError: pass

    # Best model
    best = min(models_registry, key=lambda x: x["mae"])
    print(f"\n🏆 Best: {best['model']} (MAE={best['mae']:.1f}, R²={best['r2']:.3f})")

    # Forecast plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(y_test.values, label="Actual", color="#3498db", lw=2)
    axes[0].plot(rf_pred, label="RF Predicted", color="#e74c3c", lw=1.5, alpha=0.8)
    axes[0].set_title("Demand Forecast: Actual vs Predicted"); axes[0].legend()

    # Feature importance
    if hasattr(rf, "feature_importances_"):
        imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values()
        imp.plot(kind="barh", ax=axes[1], color="#2ecc71", edgecolor="white")
        axes[1].set_title("Feature Importances (Random Forest)")

    plt.tight_layout(); fig.savefig(os.path.join(args.output_dir, "step11_forecast.png"), dpi=120); plt.close()

    with open(os.path.join(args.output_dir, "forecast_models.json"), "w") as f: json.dump(models_registry, f, default=str, indent=2)
    with open(os.path.join(args.output_dir, "best_forecast_model.pkl"), "wb") as f: pickle.dump(rf, f)
    print("✅ Steps 11-13 complete")
if __name__ == "__main__":
    def eval_model(name, pred, actual):
        return {"model": name, "mae": round(mean_absolute_error(actual, pred), 1),
                "rmse": round(np.sqrt(mean_squared_error(actual, pred)), 1),
                "r2": round(r2_score(actual, pred), 3)}
    main()
