# Model Card: Decision Tree Demand Predictor

**Version:** 1.0.0  
**Generated:** 2025-12-02T13:11:04.830107+00:00

---

## Model Details

- **Architecture:** Decision Tree Regressor
- **Framework:** scikit-learn 1.5
- **Training Date:** 2024-12-01
- **Output:** Demand probability [0.0, 1.0] representing likelihood of ride acceptance at given price

### Hyperparameters

| Parameter | Value |
|---|---|
| max_depth | 10 |

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
| R² Score | 0.8986 |
| MAE | 0.0463 |
| RMSE | 0.0670 |
| Test Set Size | 2,000 |

### Feature Importance

| Feature | Importance |
|---|---|
| price | 0.509498 |
| historical_cost_of_ride | 0.398396 |
| time_of_booking | 0.028690 |
| supply_demand_ratio | 0.022708 |
| location_category | 0.013643 |
| segment | 0.011739 |
| vehicle_type | 0.005164 |
| number_of_drivers | 0.004244 |
| expected_ride_duration | 0.001619 |
| average_ratings | 0.001592 |
| number_of_past_rides | 0.001313 |
| number_of_riders | 0.001093 |
| customer_loyalty_status | 0.000302 |

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

- Lower accuracy than XGBoost ensemble (R² 0.90 vs 0.99)
- Prone to overfitting without depth constraints
- Sharp decision boundaries may not reflect smooth demand curves
- Less robust to outliers compared to ensemble methods
- Same data scope limitations as XGBoost model
