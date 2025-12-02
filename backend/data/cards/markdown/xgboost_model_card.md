# Model Card: XGBoost Demand Predictor

**Version:** 1.0.0  
**Generated:** 2025-12-02T13:11:04.829591+00:00

---

## Model Details

- **Architecture:** XGBoost Gradient Boosting Regressor
- **Framework:** XGBoost 2.1 / scikit-learn 1.5
- **Training Date:** 2024-12-01
- **Output:** Demand probability [0.0, 1.0] representing likelihood of ride acceptance at given price

### Hyperparameters

| Parameter | Value |
|---|---|
| learning_rate | 0.100000 |
| max_depth | 7 |
| n_estimators | 200 |

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

**Primary Use:** Predict customer demand probability for dynamic ride pricing optimization

**Target Users:**

- Pricing Analysts - reviewing and adjusting pricing strategies
- Data Scientists - model monitoring and improvement
- Product Managers - understanding demand patterns
- Business Stakeholders - revenue optimization decisions

**Out of Scope:**

- Real-time surge pricing without human oversight
- Individual customer targeting based on personal characteristics
- Price discrimination based on protected attributes
- Extrapolation to markets outside training data geography
- Predictions for vehicle types not in training data

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
| R² Score | 0.9859 |
| MAE | 0.0130 |
| RMSE | 0.0250 |
| Test Set Size | 2,000 |

### Feature Importance

| Feature | Importance |
|---|---|
| historical_cost_of_ride | 0.405666 |
| price | 0.220741 |
| time_of_booking | 0.088604 |
| location_category | 0.075667 |
| segment | 0.070744 |
| supply_demand_ratio | 0.050997 |
| expected_ride_duration | 0.033342 |
| vehicle_type | 0.027558 |
| number_of_drivers | 0.009915 |
| customer_loyalty_status | 0.009327 |
| average_ratings | 0.003476 |
| number_of_past_rides | 0.002466 |
| number_of_riders | 0.001498 |

---

## Ethical Considerations

### Fairness

- Model may exhibit different performance across customer segments
- Price sensitivity varies by loyalty status - monitor for discriminatory outcomes
- Geographic location features could encode socioeconomic biases
- Regular fairness audits recommended across protected characteristics

### Privacy

- Model trained on aggregated ride data without PII
- Individual customer IDs not used as features
- Predictions should not be used to identify individual customers

### Transparency

- SHAP values available for individual prediction explanations
- Feature importance scores documented in this card
- Decision traces logged for audit purposes
- Model predictions include confidence intervals

---

## Limitations

- Trained on synthetic demand data generated from elasticity curves
- Performance may degrade for extreme price points outside training range
- Assumes stable market conditions - may not generalize during special events
- Limited to vehicle types present in training data (Economy, Premium)
- Geographic scope limited to Urban, Suburban, and Rural location categories
- Temporal patterns based on time_of_booking buckets, not continuous time
