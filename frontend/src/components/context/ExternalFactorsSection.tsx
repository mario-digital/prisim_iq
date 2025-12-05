'use client';

import { useState, useEffect, type FC } from 'react';
import {
  Cloud,
  Sun,
  CloudRain,
  Snowflake,
  Fuel,
  Calendar,
  TrendingUp,
  TrendingDown,
  Minus,
  RefreshCw,
  AlertCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { cn } from '@/lib/utils';

interface WeatherData {
  condition: string;
  temperature_f: number;
  demand_modifier: number;
  source: string;
}

interface FuelData {
  price_per_gallon: number;
  change_percent: number;
  source: string;
}

interface EventData {
  name: string;
  type: string;
  venue: string;
  start_time: string;
  surge_modifier: number;
  radius_miles: number;
}

interface ExternalContext {
  fuel: FuelData | null;
  weather: WeatherData | null;
  events: EventData[];
  last_updated: string;
}

interface ExternalContextResponse {
  context: ExternalContext;
  cache_status: Record<string, { age_seconds: number | null; is_fresh: boolean }>;
  explanation: string;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const getWeatherIcon = (condition: string) => {
  const c = condition.toLowerCase();
  if (c.includes('rain')) return <CloudRain className="h-4 w-4 text-blue-400" />;
  if (c.includes('snow')) return <Snowflake className="h-4 w-4 text-cyan-300" />;
  if (c.includes('cloud')) return <Cloud className="h-4 w-4 text-slate-400" />;
  return <Sun className="h-4 w-4 text-amber-400" />;
};

const getTrendIcon = (change: number) => {
  if (change > 1) return <TrendingUp className="h-3 w-3 text-rose-400" />;
  if (change < -1) return <TrendingDown className="h-3 w-3 text-emerald-400" />;
  return <Minus className="h-3 w-3 text-slate-400" />;
};

export const ExternalFactorsSection: FC = () => {
  const [data, setData] = useState<ExternalContextResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Toggle states for which factors to consider
  const [useWeather, setUseWeather] = useState(true);
  const [useFuel, setUseFuel] = useState(true);
  const [useEvents, setUseEvents] = useState(true);

  const fetchExternalData = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/external/context`);
      if (!res.ok) throw new Error('Failed to fetch external data');
      const json = await res.json();
      setData(json);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchExternalData();
  }, []);

  const fuel = data?.context?.fuel;
  const weather = data?.context?.weather;
  const events = data?.context?.events || [];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Cloud className="h-4 w-4 text-muted-foreground" />
          <h3 className="text-sm font-semibold">External Factors</h3>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={fetchExternalData}
          disabled={loading}
          className="h-7 px-2"
        >
          <RefreshCw className={cn("h-3 w-3", loading && "animate-spin")} />
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-2 text-xs text-destructive bg-destructive/10 rounded-md p-2">
          <AlertCircle className="h-3 w-3" />
          {error}
        </div>
      )}

      {/* Weather */}
      <div className={cn(
        "rounded-lg p-3 border transition-all duration-200",
        useWeather 
          ? "bg-card border-border" 
          : "bg-muted/30 border-transparent opacity-60"
      )}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            {weather ? getWeatherIcon(weather.condition) : <Cloud className="h-4 w-4 text-muted-foreground" />}
            <span className="text-xs font-medium">Weather</span>
          </div>
          <Switch
            checked={useWeather}
            onCheckedChange={setUseWeather}
            className="scale-75"
          />
        </div>
        {weather ? (
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold capitalize">{weather.condition}</span>
              <span className="text-xs text-muted-foreground">{weather.temperature_f}°F</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <span>Demand modifier:</span>
              <span className={cn(
                "font-medium",
                weather.demand_modifier > 1 ? "text-orange-400" : "text-slate-400"
              )}>
                {weather.demand_modifier.toFixed(2)}x
              </span>
            </div>
          </div>
        ) : (
          <div className="text-xs text-muted-foreground">No weather data</div>
        )}
      </div>

      {/* Fuel Prices */}
      <div className={cn(
        "rounded-lg p-3 border transition-all duration-200",
        useFuel 
          ? "bg-card border-border" 
          : "bg-muted/30 border-transparent opacity-60"
      )}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Fuel className="h-4 w-4 text-amber-500" />
            <span className="text-xs font-medium">Fuel Prices</span>
          </div>
          <Switch
            checked={useFuel}
            onCheckedChange={setUseFuel}
            className="scale-75"
          />
        </div>
        {fuel ? (
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-sm font-semibold">${fuel.price_per_gallon.toFixed(2)}/gal</span>
              <div className="flex items-center gap-1">
                {getTrendIcon(fuel.change_percent)}
                <span className={cn(
                  "text-xs font-medium",
                  fuel.change_percent > 0 ? "text-rose-400" : 
                  fuel.change_percent < 0 ? "text-emerald-400" : "text-slate-400"
                )}>
                  {fuel.change_percent > 0 ? '+' : ''}{fuel.change_percent.toFixed(1)}%
                </span>
              </div>
            </div>
            <div className="text-xs text-muted-foreground">
              Source: {fuel.source}
            </div>
          </div>
        ) : (
          <div className="text-xs text-muted-foreground">No fuel data</div>
        )}
      </div>

      {/* Events */}
      <div className={cn(
        "rounded-lg p-3 border transition-all duration-200",
        useEvents 
          ? "bg-card border-border" 
          : "bg-muted/30 border-transparent opacity-60"
      )}>
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-purple-400" />
            <span className="text-xs font-medium">Local Events</span>
          </div>
          <Switch
            checked={useEvents}
            onCheckedChange={setUseEvents}
            className="scale-75"
          />
        </div>
        {events.length > 0 ? (
          <div className="space-y-3">
            {events.map((event, i) => (
              <div key={i} className="space-y-1">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-xs font-medium leading-tight">{event.name}</span>
                  <span className="text-[10px] font-medium text-orange-400 whitespace-nowrap">
                    +{((event.surge_modifier - 1) * 100).toFixed(0)}% surge
                  </span>
                </div>
                <div className="text-[10px] text-muted-foreground space-y-0.5">
                  <div className="truncate">{event.venue}</div>
                  {event.start_time && (
                    <div>
                      {new Date(event.start_time).toLocaleTimeString([], { 
                        hour: 'numeric', 
                        minute: '2-digit',
                        hour12: true 
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-xs text-muted-foreground">No events nearby</div>
        )}
      </div>

      {/* Data freshness indicator */}
      {data?.cache_status && (
        <div className="text-[10px] text-muted-foreground/60 text-center">
          {Object.entries(data.cache_status).map(([key, status]) => (
            <span key={key} className="mr-2">
              {key}: {status.is_fresh ? '✓' : '○'}
            </span>
          ))}
        </div>
      )}
    </div>
  );
};

