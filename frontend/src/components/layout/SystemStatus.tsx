'use client';

import { useEffect, type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStatusStore, type HealthStatus } from '@/stores/statusStore';
import { fetchValidated } from '@/lib/api-client';
import { HealthResponseSchema, ModelsStatusResponseSchema } from '@prismiq/shared/schemas';

interface StatusConfig {
  label: string;
  emoji: string;
  bgClass: string;
  textClass: string;
}

const STATUS_CONFIG: Record<HealthStatus, StatusConfig> = {
  healthy: {
    label: 'READY',
    emoji: '🟢',
    bgClass: 'bg-green-100',
    textClass: 'text-green-700',
  },
  degraded: {
    label: 'DEGRADED',
    emoji: '🟡',
    bgClass: 'bg-yellow-100',
    textClass: 'text-yellow-700',
  },
  unhealthy: {
    label: 'ERROR',
    emoji: '🔴',
    bgClass: 'bg-red-100',
    textClass: 'text-red-700',
  },
};

const HEALTH_POLL_INTERVAL = 30000; // 30 seconds

/**
 * System status indicator showing API health.
 * Polls the /health and /models/status endpoints periodically.
 * Displays: [READY] 🟢, [DEGRADED] 🟡, or [ERROR] 🔴
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
      className={cn(
        'flex items-center gap-1.5 px-2.5 py-1 rounded text-sm font-medium transition-colors',
        config.bgClass,
        config.textClass
      )}
      title={`System status: ${config.label}`}
    >
      <span aria-hidden="true">{config.emoji}</span>
      <span className="font-semibold">[{config.label}]</span>
    </div>
  );
};


