# 9. Database Schema

Per the architecture decisions, PrismIQ uses **file-based storage** rather than a traditional database.

## 9.1 Source Dataset Schema (dynamic_pricing.xlsx)

```sql
-- Conceptual schema (actual storage is Excel)

TABLE dynamic_pricing (
    -- Row identifier (implicit)
    row_id              INTEGER PRIMARY KEY,
    
    -- Supply & Demand
    Number_of_Riders    INTEGER NOT NULL,      -- Range: 10-100
    Number_of_Drivers   INTEGER NOT NULL,      -- Range: 5-80
    
    -- Location & Time
    Location_Category   VARCHAR(20) NOT NULL,  -- Urban|Suburban|Rural
    Time_of_Booking     VARCHAR(10) NOT NULL,  -- Morning|Afternoon|Evening|Night
    
    -- Customer Profile
    Customer_Loyalty_Status VARCHAR(10) NOT NULL,  -- Bronze|Silver|Gold|Platinum
    
    -- Vehicle
    Vehicle_Type        VARCHAR(10) NOT NULL,  -- Economy|Premium
    
    -- External Factors
    Historical_Cost_of_Ride DECIMAL(6,2) NOT NULL,  -- Range: ~8-50
    Expected_Ride_Duration  INTEGER NOT NULL,      -- Minutes: 10-60
    
    -- Target Variable
    Adjusted_Ride_Cost  DECIMAL(6,2) NOT NULL  -- Dynamic price target
);

-- Derived features (calculated at runtime)
-- supply_demand_ratio = Number_of_Drivers / Number_of_Riders
-- is_surge = supply_demand_ratio < 0.5
-- segment_id = f"{Location_Category}_{Customer_Loyalty_Status}_{Vehicle_Type}"
```

## 9.2 Serialized Models Schema

```yaml
# backend/data/models/model_metadata.yaml

models:
  price_predictor:
    file: price_predictor.joblib
    type: XGBRegressor
    version: "1.0.0"
    trained_at: "2024-01-15T10:30:00Z"
    features:
      - supply_demand_ratio
      - location_encoded
      - time_encoded
      - loyalty_encoded
      - vehicle_encoded
      - historical_cost
      - expected_duration
    metrics:
      rmse: 2.34
      mae: 1.89
      r2: 0.923
    
  demand_model:
    file: demand_model.joblib
    type: ElasticityModel
    version: "1.0.0"
    segments:
      - Urban_Premium
      - Urban_Economy
      - Suburban_Premium
      - Suburban_Economy
      - Rural_Premium
      - Rural_Economy
    
  segmenter:
    file: segmenter.joblib
    type: KMeans
    version: "1.0.0"
    n_clusters: 6
    features:
      - location_encoded
      - loyalty_encoded
      - vehicle_encoded
```

## 9.3 Scenario Storage Schema (JSON)

```json
// backend/data/scenarios/{scenario_id}.json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Downtown Rush Hour Premium",
  "description": "Peak demand scenario for premium vehicles",
  "createdAt": "2024-01-20T14:30:00Z",
  "updatedAt": "2024-01-20T14:30:00Z",
  "context": {
    "location": "Urban",
    "timestamp": "2024-01-20T17:30:00Z",
    "timeOfDay": "Evening",
    "riders": 85,
    "drivers": 25,
    "supplyDemandRatio": 0.29,
    "customerSegment": "Urban_Gold_Premium",
    "loyaltyTier": "Gold",
    "vehicleType": "Premium"
  },
  "result": {
    "recommendedPrice": 42.50,
    "basePrice": 28.00,
    "multiplier": 1.52,
    "confidence": 0.89,
    "explanation": {
      "narrative": "High surge pricing recommended due to...",
      "topFactors": [...]
    }
  },
  "tags": ["rush-hour", "premium", "high-demand"],
  "isFavorite": true
}
```

---
