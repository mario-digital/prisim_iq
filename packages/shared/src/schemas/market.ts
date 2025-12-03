/**
 * Market context schemas for pricing and segmentation.
 * Source: backend/src/schemas/market.py
 */
import { z } from 'zod';

// Enum schemas matching backend Literal types
export const LocationCategory = z.enum(['Urban', 'Suburban', 'Rural']);
export const CustomerLoyaltyStatus = z.enum(['Bronze', 'Silver', 'Gold', 'Platinum']);
export const TimeOfBooking = z.enum(['Morning', 'Afternoon', 'Evening', 'Night']);
export const VehicleType = z.enum(['Economy', 'Premium']);

/**
 * Market context for segmentation and pricing optimization.
 * Source: backend/src/schemas/market.py::MarketContext
 */
export const MarketContextSchema = z.object({
  number_of_riders: z
    .number()
    .int()
    .min(1)
    .max(100)
    .describe('Demand indicator - number of riders requesting rides'),
  number_of_drivers: z
    .number()
    .int()
    .min(1)
    .max(100)
    .describe('Supply indicator - number of available drivers'),
  location_category: LocationCategory.describe('Geographic location category'),
  customer_loyalty_status: CustomerLoyaltyStatus.describe('Customer loyalty tier'),
  number_of_past_rides: z
    .number()
    .int()
    .min(0)
    .describe("Customer's historical ride count"),
  average_ratings: z.number().min(1.0).max(5.0).describe('Average customer rating (1.0-5.0)'),
  time_of_booking: TimeOfBooking.describe('Time period of the booking'),
  vehicle_type: VehicleType.describe('Type of vehicle requested'),
  expected_ride_duration: z
    .number()
    .int()
    .min(1)
    .describe('Expected ride duration in minutes'),
  historical_cost_of_ride: z.number().min(0).describe('Baseline/historical price for this route'),
  tier_prices: z
    .record(z.string(), z.number())
    .nullable()
    .optional()
    .describe('Optional explicit tier prices (keys: new, exchange, repair, usm)'),
});

export type MarketContext = z.infer<typeof MarketContextSchema>;

// Type exports for enum values
export type LocationCategoryType = z.infer<typeof LocationCategory>;
export type CustomerLoyaltyStatusType = z.infer<typeof CustomerLoyaltyStatus>;
export type TimeOfBookingType = z.infer<typeof TimeOfBooking>;
export type VehicleTypeType = z.infer<typeof VehicleType>;

/**
 * Helper function to compute supply/demand ratio (matches backend @computed_field).
 * This is a client-side helper, not part of the schema validation.
 */
export function getSupplyDemandRatio(context: MarketContext): number {
  return context.number_of_drivers / context.number_of_riders;
}

