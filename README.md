# F1 Podium Prediction Tool for DSI Capstone Project

**GOAL**:
Create a tool that will accurately predict podium finishers using Data Analysis methods and Machine Learning.

---

## Overview

This tool predicts **top 3 finishers** in Formula 1 races using a **Decision Tree classifier** trained on historical race data (2009-2022). The model uses driver and constructor historical performance, qualifying position, and weather-conditional statistics to predict podium probability.

**Model Performance:**
- Train AUC: 0.968
- Test AUC: 0.946 (2023 season)
- Features: 11 historical performance metrics

**How it works:**
1. Loads race data with driver/constructor historical stats
2. Calculates podium probability for each driver
3. Ranks drivers by probability and predicts top 3
4. Compares predictions to actual results

---

## Data Pipeline

### Phase 1: Data Cleaning (`notebooks/data_cleansing.ipynb`)

Consolidates 15 CSV files (races, results, drivers, constructors, qualifying, standings, weather, circuits) into a single race-driver dataset.

**Process:**
- Filters data to 2006+ (2006-2008 for 3-year lookback feature calculation)
- Merges races, drivers, constructors, qualifying, standings, weather, circuits
- Creates `is_podium` binary target (1 if position ≤ 3)
- Handles missing values (grid positions, weather, rookie driver standings)
- Splits into train (2009-2022) and test (2023)

**Output:**
- `data/processed/race_driver_records_train.csv`
- `data/processed/race_driver_records_test.csv`

### Phase 2: Feature Engineering (`notebooks/feature_engineering.ipynb`)

Creates performance features from historical data to prevent data leakage; all features use strictly pre-race data, and I chose not to use data from races in the same year so that the test set was entirely independent from the train set.

**Features created:**
- **Driver podium %**: year -1, -2, -3 percentages
- **Constructor podium %**: year -1, -2, -3 percentages
- **Average positions**: driver/constructor year -1, -2, -3
- **Qualifying consistency**: standard deviation over 1, 2, 3 years
- **Weather categorization**: dry/wet/variable/unknown
- **Weather-conditional performance**: driver avg position in dry/wet conditions (3-year)

**Strategy:**
- Year -1 means "previous completed calendar year" — no current season data
- Missing values handled with conservative defaults (rookies, new teams)
- Final dataset: 2009-2022 train, 2023 test with full 3-year features

**Output:**
- `data/processed/race_driver_records_train_fe.csv` (5,857 records, 70 columns)
- `data/processed/race_driver_records_test_fe.csv` (240 records, 70 columns)

### Phase 3-4: Model Training (`notebooks/ml_comparison.ipynb`)

Compared 5 ML methods: Naive Bayes, Decision Tree, Random Forest, SVM, XGBoost.

**Winner: Decision Tree**
- Best test AUC (0.946) with minimal overfitting (Δ0.022)
- Hyperparameters: `max_depth=10`, `min_samples_split=20`, `min_samples_leaf=10`
- Outperformed ensemble methods (Random Forest, XGBoost) on this dataset

**Model artifacts saved:**
- `models/dt_model.pkl`: trained Decision Tree
- `models/scaler.pkl`: StandardScaler (not used by DT, kept for pipeline compatibility)
- `models/features.pkl`: 11 feature names

---

## Deployment: Streamlit

**Why Streamlit:**
- **Easy setup**: single Python script, no complex server config
- **Sleek interface**: interactive predictions with color-coded results
- **Fast iteration**: live reload during development
- **Built-in features**: file upload, dataframes, charts without custom HTML/CSS

**Features:**
- Upload custom CSV or use default 2023 test data
- Predicts podium probability for each driver per race
- Displays top 3 predictions vs actual results (green = correct, red = incorrect)
- Confusion matrix visualization

**Run:**
```bash
streamlit run streamlit/f1_predictor_streamlit.py --server.headless true --server.port 8501
```

---

## Importing Your Own Data

### Required Columns

CSV must include these 11 model features plus display columns:

**Model features:**
- `year`, `round`, `grid_position`
- `driver_podium_pct_y2`, `driver_avg_pos_y2`, `driver_podium_pct_y3`
- `constructor_races_y1`, `constructor_podium_pct_y2`, `constructor_podium_pct_y3`
- `driver_avg_pos_dry_3y`, `driver_avg_pos_wet_3y`

**Display/evaluation:**
- `driver_name`: driver's full name
- `name`: race name
- `is_podium`: actual result (1 = top 3, 0 = outside podium)

### Data Source: Jolpica F1 API

Ergast API is deprecated. Use **Jolpica F1** (Ergast-compatible endpoints):

**Base URL:** `http://api.jolpi.ca/ergast/f1/`

**Key endpoints:**
```bash
http://api.jolpi.ca/ergast/f1/2026.json                      # Race schedule
http://api.jolpi.ca/ergast/f1/2026/1/results.json            # Results by round
http://api.jolpi.ca/ergast/f1/2026/1/qualifying.json         # Qualifying
```

See `fetch_2026_for_streamlit.py` in the `extras` folder for implementation.

### New vs. Returning Drivers

**Returning drivers:** Use their 2023 stats as baseline for historical features.

**New drivers (no F1 history):** Use conservative defaults:
- Podium rates: `0.1` (10%)
- Average positions: `10` (mid-field)

**Constructor changes:** If team rebranded, use previous team's stats. 

### Limitations

- Model trained on 2009-2022, tested on 2023 (AUC: 0.946). **2026 introduced major regulation changes** — historical patterns may not apply. Predictions less reliable than 2023 test set. Retraining on 2024-2025 data would improve accuracy.
- I did not explore telemetry data or same-year races that may have improved model accuracy.
- Weather categorisation is coarse (dry / wet / variable). There is no distinction between monsoon rain in Singapore and drizzle in Silverstone.
- Different pit crews perform to different standards. I did not consider pit crew strength as a variable here, but over the course of a race it can have a significant impact.

### Usage

**Fetch 2026 data:**
```bash
python3 fetch_2026_for_streamlit.py
```

**Run Streamlit:**
```bash
streamlit run streamlit/f1_predictor_streamlit.py --server.headless true --server.port 8501
```

Uncheck "Use data provided" if you wish to upload your own CSV. 
