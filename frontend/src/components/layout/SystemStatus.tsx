'use client';

import { useEffect, type FC } from 'react';
import { cn } from '@/lib/utils';
import { useStatusStore, type HealthStatus } from '@/stores/statusStore';
import { apiUrl } from '@/lib/api';

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
 * Polls the /health endpoint periodically.
 * Displays: [READY] 🟢, [DEGRADED] 🟡, or [ERROR] 🔴
 */
export const SystemStatus: FC = () => {
  const { health, setHealthCheck } = useStatusStore();
  const config = STATUS_CONFIG[health];

  useEffect(() => {
    let mounted = true;

    const checkHealth = async () => {
      try {
        const response = await fetch(apiUrl('/health'), {
          method: 'GET',
          headers: { 'Accept': 'application/json' },
        });

        if (!mounted) return;

        if (response.ok) {
          const data = await response.json();
          setHealthCheck(data.status as HealthStatus);
        } else {
          setHealthCheck('degraded');
        }
      } catch {
        if (mounted) {
          setHealthCheck('unhealthy');
        }
      }
    };

    // Initial check
    checkHealth();

    // Set up polling
    const interval = setInterval(checkHealth, HEALTH_POLL_INTERVAL);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, [setHealthCheck]);

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


