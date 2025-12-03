import { describe, it, expect } from 'bun:test';
import {
    MarketContextSchema,
    LocationCategory,
    CustomerLoyaltyStatus,
    TimeOfBooking,
    VehicleType,
    getSupplyDemandRatio,
} from '../market';

describe('MarketContextSchema', () => {
    const validContext = {
        number_of_riders: 50,
        number_of_drivers: 25,
        location_category: 'Urban',
        customer_loyalty_status: 'Gold',
        number_of_past_rides: 10,
        average_ratings: 4.5,
        time_of_booking: 'Evening',
        vehicle_type: 'Premium',
        expected_ride_duration: 30,
        historical_cost_of_ride: 35.0,
    };

    describe('valid inputs', () => {
        it('validates correct input', () => {
            const result = MarketContextSchema.safeParse(validContext);
            expect(result.success).toBe(true);
            if (result.success) {
                expect(result.data.number_of_riders).toBe(50);
            }
        });

        it('accepts optional tier_prices as null', () => {
            const withNull = { ...validContext, tier_prices: null };
            expect(() => MarketContextSchema.parse(withNull)).not.toThrow();
        });

        it('accepts optional tier_prices with values', () => {
            const withPrices = {
                ...validContext,
                tier_prices: { new: 100.0, exchange: 80.0 },
            };
            const result = MarketContextSchema.parse(withPrices);
            expect(result.tier_prices).toEqual({ new: 100.0, exchange: 80.0 });
        });

        it('accepts minimum valid values', () => {
            const minValues = {
                ...validContext,
                number_of_riders: 1,
                number_of_drivers: 1,
                number_of_past_rides: 0,
                average_ratings: 1.0,
                expected_ride_duration: 1,
                historical_cost_of_ride: 0,
            };
            expect(() => MarketContextSchema.parse(minValues)).not.toThrow();
        });

        it('accepts maximum valid values', () => {
            const maxValues = {
                ...validContext,
                number_of_riders: 100,
                number_of_drivers: 100,
                average_ratings: 5.0,
            };
            expect(() => MarketContextSchema.parse(maxValues)).not.toThrow();
        });
    });

    describe('invalid inputs - numeric constraints', () => {
        it('rejects number_of_riders > 100', () => {
            const invalid = { ...validContext, number_of_riders: 200 };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects number_of_riders < 1', () => {
            const invalid = { ...validContext, number_of_riders: 0 };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects number_of_drivers > 100', () => {
            const invalid = { ...validContext, number_of_drivers: 150 };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects number_of_drivers < 1', () => {
            const invalid = { ...validContext, number_of_drivers: 0 };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects average_ratings > 5.0', () => {
            const invalid = { ...validContext, average_ratings: 5.5 };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects average_ratings < 1.0', () => {
            const invalid = { ...validContext, average_ratings: 0.5 };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects negative number_of_past_rides', () => {
            const invalid = { ...validContext, number_of_past_rides: -1 };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects expected_ride_duration < 1', () => {
            const invalid = { ...validContext, expected_ride_duration: 0 };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects negative historical_cost_of_ride', () => {
            const invalid = { ...validContext, historical_cost_of_ride: -10 };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects non-integer number_of_riders', () => {
            const invalid = { ...validContext, number_of_riders: 50.5 };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });
    });

    describe('invalid inputs - enum values', () => {
        it('rejects invalid location_category', () => {
            const invalid = { ...validContext, location_category: 'Downtown' };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects invalid customer_loyalty_status', () => {
            const invalid = { ...validContext, customer_loyalty_status: 'Diamond' };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects invalid time_of_booking', () => {
            const invalid = { ...validContext, time_of_booking: 'Midnight' };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });

        it('rejects invalid vehicle_type', () => {
            const invalid = { ...validContext, vehicle_type: 'Luxury' };
            expect(() => MarketContextSchema.parse(invalid)).toThrow();
        });
    });

    describe('invalid inputs - missing fields', () => {
        it('rejects missing required fields', () => {
            const incomplete = {
                number_of_riders: 50,
                number_of_drivers: 25,
            };
            expect(() => MarketContextSchema.parse(incomplete)).toThrow();
        });
    });
});

describe('Enum schemas', () => {
    describe('LocationCategory', () => {
        it('accepts valid values', () => {
            expect(LocationCategory.parse('Urban')).toBe('Urban');
            expect(LocationCategory.parse('Suburban')).toBe('Suburban');
            expect(LocationCategory.parse('Rural')).toBe('Rural');
        });

        it('rejects invalid values', () => {
            expect(() => LocationCategory.parse('Metropolitan')).toThrow();
        });
    });

    describe('CustomerLoyaltyStatus', () => {
        it('accepts valid values', () => {
            expect(CustomerLoyaltyStatus.parse('Bronze')).toBe('Bronze');
            expect(CustomerLoyaltyStatus.parse('Silver')).toBe('Silver');
            expect(CustomerLoyaltyStatus.parse('Gold')).toBe('Gold');
            expect(CustomerLoyaltyStatus.parse('Platinum')).toBe('Platinum');
        });

        it('rejects invalid values', () => {
            expect(() => CustomerLoyaltyStatus.parse('Diamond')).toThrow();
        });
    });

    describe('TimeOfBooking', () => {
        it('accepts valid values', () => {
            expect(TimeOfBooking.parse('Morning')).toBe('Morning');
            expect(TimeOfBooking.parse('Afternoon')).toBe('Afternoon');
            expect(TimeOfBooking.parse('Evening')).toBe('Evening');
            expect(TimeOfBooking.parse('Night')).toBe('Night');
        });

        it('rejects invalid values', () => {
            expect(() => TimeOfBooking.parse('Midnight')).toThrow();
        });
    });

    describe('VehicleType', () => {
        it('accepts valid values', () => {
            expect(VehicleType.parse('Economy')).toBe('Economy');
            expect(VehicleType.parse('Premium')).toBe('Premium');
        });

        it('rejects invalid values', () => {
            expect(() => VehicleType.parse('Luxury')).toThrow();
        });
    });
});

describe('getSupplyDemandRatio', () => {
    it('calculates ratio correctly', () => {
        const context = {
            number_of_riders: 50,
            number_of_drivers: 25,
            location_category: 'Urban' as const,
            customer_loyalty_status: 'Gold' as const,
            number_of_past_rides: 10,
            average_ratings: 4.5,
            time_of_booking: 'Evening' as const,
            vehicle_type: 'Premium' as const,
            expected_ride_duration: 30,
            historical_cost_of_ride: 35.0,
        };
        expect(getSupplyDemandRatio(context)).toBe(0.5);
    });

    it('handles edge cases', () => {
        const context = {
            number_of_riders: 1,
            number_of_drivers: 100,
            location_category: 'Urban' as const,
            customer_loyalty_status: 'Gold' as const,
            number_of_past_rides: 0,
            average_ratings: 4.5,
            time_of_booking: 'Evening' as const,
            vehicle_type: 'Premium' as const,
            expected_ride_duration: 30,
            historical_cost_of_ride: 35.0,
        };
        expect(getSupplyDemandRatio(context)).toBe(100);
    });
});

