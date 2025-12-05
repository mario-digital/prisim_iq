'use client';

import { useEffect, type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStatusStore, type HealthStatus } from '@/stores/statusStore';
import { fetchValidated } from '@/lib/api-client';
import { HealthResponseSchema, ModelsStatusResponseSchema } from '@prismiq/shared/schemas';

interface StatusConfig {
  label: string;
  dotClass: string;
  textClass: string;
  glowClass: string;
}

const STATUS_CONFIG: Record<HealthStatus, StatusConfig> = {
  healthy: {
    label: 'Online',
    dotClass: 'bg-emerald-500 dark:bg-emerald-400',
    textClass: 'text-emerald-600 dark:text-emerald-400',
    glowClass: 'shadow-emerald-500/50 dark:shadow-emerald-400/50',
  },
  degraded: {
    label: 'Degraded',
    dotClass: 'bg-amber-500 dark:bg-amber-400',
    textClass: 'text-amber-600 dark:text-amber-400',
    glowClass: 'shadow-amber-500/50 dark:shadow-amber-400/50',
  },
  unhealthy: {
    label: 'Offline',
    dotClass: 'bg-rose-500 dark:bg-rose-400',
    textClass: 'text-rose-600 dark:text-rose-400',
    glowClass: 'shadow-rose-500/50 dark:shadow-rose-400/50',
  },
};

const HEALTH_POLL_INTERVAL = 30000; // 30 seconds

/**
 * System status indicator showing API health.
 * Polls the /health and /models/status endpoints periodically.
 * Modern, minimal design with animated status dot.
 */
export const SystemStatus: FC = () => {
  const { health, setHealthCheck, setModelsReady } = useStatusStore();
  const config = STATUS_CONFIG[health];

  useEffect(() => {
    let mounted = true;

    const checkHealth = async () => {
      try {
        // Use validated fetch with shared schema
        const data = await fetchValidated('health', HealthResponseSchema);
        if (mounted) {
          setHealthCheck(data.status);
        }
      } catch {
        if (mounted) {
          setHealthCheck('unhealthy');
        }
      }
    };

    const checkModelsStatus = async () => {
      try {
        // Fetch models status from backend
        const data = await fetchValidated('models/status', ModelsStatusResponseSchema);
        if (mounted) {
          setModelsReady(data.ready, data.total);
        }
      } catch {
        // Silent fail - models status is nice-to-have, not critical
        console.warn('[SystemStatus] Failed to fetch models status');
      }
    };

    // Initial checks
    checkHealth();
    checkModelsStatus();

    // Set up polling
    const healthInterval = setInterval(checkHealth, HEALTH_POLL_INTERVAL);
    const modelsInterval = setInterval(checkModelsStatus, HEALTH_POLL_INTERVAL);

    return () => {
      mounted = false;
      clearInterval(healthInterval);
      clearInterval(modelsInterval);
    };
  }, [setHealthCheck, setModelsReady]);

  return (
    <div
      className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-card/50 border border-border/30"
      title={`System status: ${config.label}`}
    >
      {/* Animated status dot */}
      <span className="relative flex h-2 w-2">
        <span
          className={cn(
            'absolute inline-flex h-full w-full rounded-full opacity-75 animate-ping',
            config.dotClass
          )}
        />
        <span
          className={cn(
            'relative inline-flex h-2 w-2 rounded-full shadow-sm',
            config.dotClass,
            config.glowClass
          )}
        />
      </span>
      <span className={cn('text-xs font-medium', config.textClass)}>
        {config.label}
      </span>
    </div>
  );
};
