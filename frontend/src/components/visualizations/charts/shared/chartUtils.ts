/**
 * Shared chart utility functions.
 * Provides formatting, data manipulation, and responsive helpers.
 */

import type { CurvePoint } from '../../types';

/**
 * Find the data point closest to a target price.
 */
export const findClosestPoint = (
  data: CurvePoint[],
  targetPrice: number
): CurvePoint | null => {
  if (data.length === 0) return null;

  return data.reduce((closest, point) =>
    Math.abs(point.price - targetPrice) < Math.abs(closest.price - targetPrice)
      ? point
      : closest
  );
};

/**
 * Find the point with maximum value in the dataset.
 */
export const findMaxPoint = (data: CurvePoint[]): CurvePoint | null => {
  if (data.length === 0) return null;

  return data.reduce((max, point) => (point.value > max.value ? point : max));
};

/**
 * Find the point with minimum value in the dataset.
 */
export const findMinPoint = (data: CurvePoint[]): CurvePoint | null => {
  if (data.length === 0) return null;

  return data.reduce((min, point) => (point.value < min.value ? point : min));
};

/**
 * Clamp a value between min and max bounds.
 */
export const clamp = (value: number, min: number, max: number): number =>
  Math.max(min, Math.min(max, value));

/**
 * Calculate domain with padding for Y-axis.
 */
export const calculateDomainWithPadding = (
  data: CurvePoint[],
  paddingPercent = 0.1
): [number, number] => {
  if (data.length === 0) return [0, 100];

  const values = data.map((d) => d.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min;
  const padding = range * paddingPercent;

  return [Math.max(0, min - padding), max + padding];
};

/**
 * Generate tick values for a given domain.
 */
export const generateTicks = (
  min: number,
  max: number,
  count = 5
): number[] => {
  const step = (max - min) / (count - 1);
  return Array.from({ length: count }, (_, i) =>
    Math.round((min + step * i) * 100) / 100
  );
};

/**
 * Sort and slice data for feature importance charts.
 */
export const prepareFeatureData = <
  T extends { importance: number; displayName?: string; name?: string },
>(
  data: T[],
  limit = 6
): T[] =>
  [...data].sort((a, b) => b.importance - a.importance).slice(0, limit);

