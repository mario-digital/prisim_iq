# Model Card: Linear Regression Baseline

**Version:** 1.0.0  
**Generated:** 2025-12-02T13:11:04.830333+00:00

---

## Model Details

- **Architecture:** Ordinary Least Squares Linear Regression
- **Framework:** scikit-learn 1.5
- **Training Date:** 2024-12-01
- **Output:** Demand probability [0.0, 1.0] - may exceed bounds, clip in production

### Hyperparameters

*None*

### Input Features

- number_of_riders
- number_of_drivers
- location_category
- customer_loyalty_status
- number_of_past_rides
- average_ratings
- time_of_booking
- vehicle_type
- expected_ride_duration
- historical_cost_of_ride
- supply_demand_ratio
- segment
- price

---

## Intended Use

**Primary Use:** Baseline model for comparison - NOT recommended for production use

**Target Users:**

- Data Scientists - model comparison and benchmarking
- Researchers - understanding linear relationships in data

**Out of Scope:**

- Production demand prediction (use XGBoost instead)
- Any use case where accuracy is critical
- Real-time pricing decisions

---

## Training Data

- **Dataset:** PrismIQ Synthetic Training Data
- **Size:** 8,000 samples
- **Target Variable:** demand
- **Train/Test Split:** 80/20 stratified by segment

---

## Performance Metrics

| Metric | Value |
|--------|-------|
| R² Score | 0.5764 |
| MAE | 0.0988 |
| RMSE | 0.1369 |
| Test Set Size | 2,000 |

### Model Coefficients

| Feature | Coefficient |
|---|---|
| number_of_riders | 0.000082 |
| number_of_drivers | -0.000176 |
| location_category | 0.053031 |
| customer_loyalty_status | 0.007856 |
| number_of_past_rides | 0.000000 |
| average_ratings | -0.005829 |
| time_of_booking | -0.020341 |
| vehicle_type | 0.000331 |
| expected_ride_duration | 0.000050 |
| historical_cost_of_ride | 0.000816 |
| supply_demand_ratio | 0.173518 |
| segment | -0.010197 |
| price | -0.000629 |
| intercept | 0.246779 |

---

## Ethical Considerations

### Fairness

- Linear assumptions may not capture non-linear fairness issues
- Coefficient interpretation enables bias detection

### Privacy

- Same privacy considerations as other models

### Transparency

- Fully interpretable through coefficient analysis
- Each coefficient represents direct feature impact on demand
- Intercept represents baseline demand when all features are zero

---

## Limitations

- Significantly lower accuracy than tree-based models (R² 0.58 vs 0.99)
- Assumes linear relationships - demand/price relationship is non-linear
- Predictions may exceed [0, 1] bounds - requires clipping
- Cannot capture feature interactions without manual engineering
- Provided as baseline only - not suitable for production
