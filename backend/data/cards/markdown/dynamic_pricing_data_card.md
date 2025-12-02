# Data Card: Dynamic Pricing Dataset

**Version:** 1.0.0  
**Generated:** 2025-12-02T13:11:04.830571+00:00

---

## Data Source

- **Origin:** Kaggle Dynamic Pricing Dataset (synthetic)
- **Collection Date:** 2024

### Preprocessing Steps

- Loaded from Excel format (dynamic_pricing.xlsx)
- Computed supply_demand_ratio as Number_of_Drivers / Number_of_Riders
- Verified no missing values across all columns
- Validated data types and value ranges
- Generated segment labels using K-Means clustering

---

## Dataset Statistics

- **Rows:** 1,000
- **Columns:** 11
- **Missing Values:** 0
- **Numeric Features:** 7
- **Categorical Features:** 4

---

## Features

| Feature | Type | Description | Range/Values | Distribution |
|---------|------|-------------|--------------|--------------|
| Number_of_Riders | int64 | Number of customers requesting rides in the area | 20.00 - 100.00 | continuous |
| Number_of_Drivers | int64 | Number of available drivers in the area | 5.00 - 89.00 | continuous |
| Location_Category | object | Type of geographic location | Urban, Rural, Suburban | categorical |
| Customer_Loyalty_Status | object | Customer loyalty tier based on ride history | Silver, Regular, Gold | categorical |
| Number_of_Past_Rides | int64 | Total historical rides by the customer | 0.00 - 100.00 | continuous |
| Average_Ratings | float64 | Customer's average rating from drivers | 3.50 - 5.00 | continuous |
| Time_of_Booking | object | Time period when ride was booked | Night, Afternoon, Morning, Evening | categorical |
| Vehicle_Type | object | Type of vehicle requested | Premium, Economy | categorical |
| Expected_Ride_Duration | int64 | Estimated trip duration in minutes | 10.00 - 180.00 | continuous |
| Historical_Cost_of_Ride | float64 | Historical average cost for similar rides | 25.99 - 836.12 | continuous |
| supply_demand_ratio | float64 | Ratio of available drivers to requesting riders | 0.06 - 0.90 | continuous |

---

## Intended Use

Training and evaluation of demand prediction models for PrismIQ dynamic pricing demonstration. This dataset is intended for educational and prototyping purposes. Production systems should validate against real-world data before deployment.

---

## Known Biases

- Synthetic data may not reflect real-world demand patterns
- Premium vehicles overrepresented (52% vs 48% Economy)
- Geographic categories are simplified (Urban/Suburban/Rural only)
- Time of booking is bucketed, losing granular temporal patterns
- Customer loyalty distribution is relatively balanced, may not match reality
- No seasonal or weather-related features included

---

## Limitations

- Sample size of 1,000 rows limits statistical power for rare scenarios
- No external validation against real ride-sharing data
- Synthetic nature means patterns may not generalize to production
- Missing features: weather, events, competitor pricing, traffic conditions
- No longitudinal data - cannot capture customer behavior over time
- Geographic scope is abstract, not tied to real locations
