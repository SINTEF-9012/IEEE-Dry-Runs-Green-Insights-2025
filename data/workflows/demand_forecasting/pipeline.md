# Supply Chain: Demand Forecasting & Inventory Optimization

## Metadata
| Field | Value |
|---|---|
| **Pipeline ID** | `demand_forecasting` |
| **Domain** | Supply Chain / Retail |
| **Total Steps** | 10 |
| **Input Files** | 3 |
| **Pipeline Type** | ML Pipeline (End-to-End) |

---

## Executive Summary

Forecasts product demand across multiple SKUs and locations using 
historical sales, inventory levels, supplier lead times, and seasonal patterns. Optimizes 
inventory reorder points to minimize stockouts while reducing carrying costs.

---

## Business Context & Need

Supply chain inefficiencies cost retailers 5-10% of revenue annually. 
Overstocks tie up working capital (20-30% carrying cost), while stockouts lose sales and 
customer trust. Accurate demand forecasting reduces inventory levels by 20-30%, cuts stockouts 
by 50%, and improves cash flow by freeing up millions in working capital. For a mid-size 
retailer with $50M inventory, a 25% optimization saves $2.5M+ annually.

---

## Data Sources

- **`inventory.csv`** — Input data file
- **`sales_orders.json`** — Input data file
- **`suppliers.xlsx`** — Input data file

---

## Pipeline Architecture

```
  Input Data ──▶ [Step 1: Data Loading & Profiling]
                  │
                  ▼
               [Step 2: Data Merging & Integration]
                  │
                  ▼
               [Step 3: Data Cleaning & Standardizatio]
                  │
                  ▼
               [Step 4: Time Series Decomposition]
                  │
                  ▼
               [Step 5: Feature Engineering: Temporal]
                  │
                  ▼
               [Step 6: Feature Engineering: Cross-Dom]
                  │
                  ▼
               [Step 7: Exploratory Data Analysis]
                  │
                  ▼
               [Step 8: Data Visualization: Demand Pat]
                  │
                  ▼
               [Step 9: Data Visualization: Inventory ]
                  │
                  ▼
               [Step 10: Statistical Analysis]
                  │
                  ▼
               [Step 11: Model Training: Statistical Ba]
                  │
                  ▼
               [Step 12: Model Training: ML Approaches]
                  │
                  ▼
               [Step 13: Model Training: Deep Learning]
                  │
                  ▼
               [Step 14: Inventory Optimization]
                  │
                  ▼
               [Step 15: Scenario Simulation & Risk Ana]
                  │
                  ▼
               [Step 16: Final Synthesis & Operations P] ──▶ Final Output
```

---

## Step Details

### Step 1: Data Loading & Profiling

**Description:** Load inventory CSV, sales_orders JSON, suppliers Excel. Profile: SKU count, order volume by month/region, inventory turnover, supplier distribution. Check for data gaps (SKUs with no sales, orders with invalid SKUs).

**Script:** `scripts/step_01_data-loading-profiling.py`

---

### Step 2: Data Merging & Integration

**Description:** Merge sales with inventory on SKU to get product details. Merge inventory with suppliers on supplier_id to get lead times and reliability. Build a unified supply_chain_master table. Flag SKUs with missing supplier or sales data.

**Script:** `scripts/step_02_data-merging-integration.py`

---

### Step 3: Data Cleaning & Standardization

**Description:** Standardize regions and shipping methods. Handle missing fulfillment_days with median by shipping method. Convert date columns. Remove duplicate orders. Normalize product categories. Create data_quality_report.json.

**Script:** `scripts/step_03_data-cleaning-standardization.py`

---

### Step 4: Time Series Decomposition

**Description:** Aggregate daily order quantities by SKU. Decompose time series into trend, seasonal, and residual components using STL decomposition. Identify SKUs with strong seasonality, trends, or volatility. Flag intermittent demand patterns.

**Script:** `scripts/step_04_time-series-decomposition.py`

---

### Step 5: Feature Engineering: Temporal

**Description:** Create temporal features: day_of_week, month, quarter, is_weekend, is_holiday, days_since_restock, rolling_mean_7d, rolling_mean_30d, lag_1d, lag_7d, lag_30d, price_change_pct, promotion_flag.

**Script:** `scripts/step_05_feature-engineering--temporal.py`

---

### Step 6: Feature Engineering: Cross-Domain

**Description:** Create supply-side features: supplier_lead_time, supplier_reliability, current_stock_level, days_of_supply (stock/daily_demand), stockout_risk, reorder_urgency. Create market features: region_demand_index, category_trend.

**Script:** `scripts/step_06_feature-engineering--cross-domain.py`

---

### Step 7: Exploratory Data Analysis

**Description:** Analyze demand patterns: top/bottom 10 SKUs by volume and volatility, ABC classification (A=top 80%, B=next 15%, C=bottom 5% of revenue), seasonal indices by product category, regional demand variation.

**Script:** `scripts/step_07_exploratory-data-analysis.py`

---

### Step 8: Data Visualization: Demand Patterns

**Description:** Create dashboard: (1) Total demand time series with trend line, (2) Seasonal heatmap (month × category), (3) SKU demand distribution histogram, (4) Regional demand treemap, (5) Top 10 vs Bottom 10 demand bar chart.

**Script:** `scripts/step_08_data-visualization--demand-patterns.py`

---

### Step 9: Data Visualization: Inventory Health

**Description:** Visualize inventory metrics: (1) Inventory turnover by category gauge chart, (2) Stockout risk distribution, (3) Days of supply histogram with reorder threshold, (4) Supplier performance scatter (reliability vs lead time), (5) Inventory value by location stacked bar.

**Script:** `scripts/step_09_data-visualization--inventory-health.py`

---

### Step 10: Statistical Analysis

**Description:** Correlation analysis: demand vs price, demand vs day_of_week, demand vs season. ANOVA: demand by region, demand by category. Time series stationarity tests (ADF, KPSS). Calculate forecastability metric (coefficient of variation).

**Script:** `scripts/step_10_statistical-analysis.py`

---

### Step 11: Model Training: Statistical Baselines

**Description:** Train statistical forecasting models per SKU: Simple Moving Average, Exponential Smoothing (Holt-Winters), SARIMA with auto_arima parameter selection. Evaluate with walk-forward validation. Compute SMAPE, MASE, RMSE per SKU.

**Script:** `scripts/step_11_model-training--statistical-baselines.py`

---

### Step 12: Model Training: ML Approaches

**Description:** Train ML models: RandomForestRegressor, XGBoost, LightGBM with temporal features. Use TimeSeriesSplit (5 splits). Compare against statistical baselines. Train a global model (all SKUs) vs per-SKU models. Evaluate forecast accuracy at 7, 14, 30-day horizons.

**Script:** `scripts/step_12_model-training--ml-approaches.py`

---

### Step 13: Model Training: Deep Learning

**Description:** Train LSTM neural network with lookback=30 days. Architecture: 2 LSTM layers (64, 32 units) + Dropout(0.2) + Dense(1). Train with early stopping. Compare with ML models. Evaluate forecast stability and computational requirements.

**Script:** `scripts/step_13_model-training--deep-learning.py`

---

### Step 14: Inventory Optimization

**Description:** Using demand forecasts, calculate optimal reorder points with safety stock: ROP = d̄L + zσ√L. Apply newsvendor model for perishable goods. Compute economic order quantity (EOQ). Simulate inventory scenarios: current vs optimized policies over 90 days.

**Script:** `scripts/step_14_inventory-optimization.py`

---

### Step 15: Scenario Simulation & Risk Analysis

**Description:** Run Monte Carlo simulation (1000 iterations) for demand uncertainty. Simulate supply disruption scenarios (supplier delays, demand spikes). Calculate expected stockout costs and inventory carrying costs. Identify high-risk SKUs.

**Script:** `scripts/step_15_scenario-simulation-risk-analysis.py`

---

### Step 16: Final Synthesis & Operations Playbook

**Description:** Compile final report: Forecast Accuracy Summary by horizon and category, 
Inventory Optimization Results (expected reduction in stockouts, carrying cost savings), 
SKU Risk Matrix (high-value/high-volatility quadrant), Recommended Reorder Parameters per SKU, 
Supplier Performance Scorecard, Implementation Roadmap with ERP integration plan, 
Monitoring Dashboard spec (forecast vs actual tracking, model retraining triggers).

**Script:** `scripts/step_16_final-synthesis-operations-playbook.py`

---


## How to Run

### Local Execution
```bash
cd custom_pipelines/demand_forecasting
pip install pandas numpy matplotlib seaborn scikit-learn xgboost lightgbm optuna shap

# Run steps sequentially
python scripts/step_01_data-loading-profiling.py --data_dir data/ --output_dir output/
python scripts/step_02_data-merging-integration.py --data_dir data/ --output_dir output/
python scripts/step_03_data-cleaning-standardization.py --data_dir data/ --output_dir output/
python scripts/step_04_time-series-decomposition.py --data_dir data/ --output_dir output/
python scripts/step_05_feature-engineering--temporal.py --data_dir data/ --output_dir output/
python scripts/step_06_feature-engineering--cross-domain.py --data_dir data/ --output_dir output/
python scripts/step_07_exploratory-data-analysis.py --data_dir data/ --output_dir output/
python scripts/step_08_data-visualization--demand-patterns.py --data_dir data/ --output_dir output/
python scripts/step_09_data-visualization--inventory-health.py --data_dir data/ --output_dir output/
python scripts/step_10_statistical-analysis.py --data_dir data/ --output_dir output/
python scripts/step_11_model-training--statistical-baselines.py --data_dir data/ --output_dir output/
python scripts/step_12_model-training--ml-approaches.py --data_dir data/ --output_dir output/
python scripts/step_13_model-training--deep-learning.py --data_dir data/ --output_dir output/
python scripts/step_14_inventory-optimization.py --data_dir data/ --output_dir output/
python scripts/step_15_scenario-simulation-risk-analysis.py --data_dir data/ --output_dir output/
python scripts/step_16_final-synthesis-operations-playbook.py --data_dir data/ --output_dir output/
```

### Argo Workflow
```bash
argo submit custom_pipelines/demand_forecasting/pipeline.yaml
argo watch @latest
argo logs @latest
```
