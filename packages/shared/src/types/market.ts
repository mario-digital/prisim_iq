/**
 * Market context types for pricing optimization.
 */

/**
 * Customer segment classification.
 */
export type CustomerSegment = 
  | 'price_sensitive'
  | 'value_seeker'
  | 'premium'
  | 'enterprise';

/**
 * Market conditions that influence pricing.
 */
export interface MarketContext {
  /** Customer segment classification */
  customerSegment: CustomerSegment;
  
  /** Current market demand level (0-1) */
  demandLevel: number;
  
  /** Competitor's price for similar product */
  competitorPrice: number;
  
  /** Customer's historical purchase value */
  customerLifetimeValue: number;
  
  /** Units in available inventory */
  inventoryLevel: number;
  
  /** Day of week (0=Sunday, 6=Saturday) */
  dayOfWeek: number;
  
  /** Hour of day (0-23) */
  hourOfDay: number;
  
  /** Season identifier */
  season: 'spring' | 'summer' | 'fall' | 'winter';
  
  /** Whether there's an active promotion */
  isPromotionActive: boolean;
  
  /** Geographic region */
  region?: string;
  
  /** Product category */
  productCategory?: string;
  
  /** Base price before optimization */
  basePrice: number;
}

/**
 * Market context with optional fields for partial updates.
 */
export type PartialMarketContext = Partial<MarketContext>;

