export interface RelativeTime {
  /** Numeric magnitude, or "now" when the unit is empty. */
  value: string;
  /** Single-token unit, so the two can be set at different sizes. */
  unit: string;
}

/**
 * Elapsed time on one continuous scale, so a column of these stays aligned.
 * Deliberately never falls back to a calendar date.
 */
export function splitRelativeTime(dateString: string): RelativeTime {
  const diffMs = Date.now() - new Date(dateString).getTime();

  const minutes = Math.floor(diffMs / 60000);
  if (minutes < 1) return { value: 'now', unit: '' };
  if (minutes < 60) return { value: String(minutes), unit: 'm' };

  const hours = Math.floor(diffMs / 3600000);
  if (hours < 24) return { value: String(hours), unit: 'h' };

  const days = Math.floor(diffMs / 86400000);
  if (days < 7) return { value: String(days), unit: 'd' };
  if (days < 35) return { value: String(Math.floor(days / 7)), unit: 'w' };
  if (days < 365) return { value: String(Math.floor(days / 30)), unit: 'mo' };

  return { value: String(Math.floor(days / 365)), unit: 'y' };
}

export function formatRelativeTime(dateString: string): string {
  const { value, unit } = splitRelativeTime(dateString);
  return unit === '' ? 'just now' : `${value}${unit} ago`;
}
