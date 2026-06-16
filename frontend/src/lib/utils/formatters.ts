/**
 * Format a number as currency (USD).
 * Examples: formatCurrency(1234.56) => "$1,234.56"
 */
export function formatCurrency(
  value: number,
  options?: { currency?: string; locale?: string; minimumFractionDigits?: number; maximumFractionDigits?: number }
): string {
  const {
    currency = "USD",
    locale = "en-US",
    minimumFractionDigits = 2,
    maximumFractionDigits = 2,
  } = options ?? {};

  return new Intl.NumberFormat(locale, {
    style: "currency",
    currency,
    minimumFractionDigits,
    maximumFractionDigits,
  }).format(value);
}

/**
 * Format a large number in abbreviated form.
 * Examples: 1_200_000_000_000 => "$1.2T", 500_000_000_000 => "$500B", 100_000_000 => "$100M"
 */
export function formatLargeNumber(value: number, options?: { currency?: string; decimals?: number }): string {
  const { currency = "$", decimals = 2 } = options ?? {};

  if (value >= 1_000_000_000_000) {
    return `${currency}${(value / 1_000_000_000_000).toFixed(decimals)}T`;
  }
  if (value >= 1_000_000_000) {
    return `${currency}${(value / 1_000_000_000).toFixed(decimals)}B`;
  }
  if (value >= 1_000_000) {
    return `${currency}${(value / 1_000_000).toFixed(decimals)}M`;
  }
  if (value >= 1_000) {
    return `${currency}${(value / 1_000).toFixed(decimals)}K`;
  }
  return `${currency}${value.toFixed(decimals)}`;
}

/**
 * Format a percentage value with sign.
 * Examples: formatPercentage(5.23) => "+5.23%", formatPercentage(-2.15) => "-2.15%"
 */
export function formatPercentage(value: number, decimals: number = 2): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(decimals)}%`;
}

/**
 * Format a date string to a readable format.
 * Example: formatDate("2024-01-15T10:30:00Z") => "Jan 15, 2024"
 */
export function formatDate(date: string | Date, options?: Intl.DateTimeFormatOptions): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    ...options,
  });
}

/**
 * Format a date string to include time.
 * Example: formatDateTime("2024-01-15T10:30:00Z") => "Jan 15, 2024, 10:30 AM"
 */
export function formatDateTime(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  return d.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

/**
 * Format a time-ago string from a date.
 * Example: formatTimeAgo("2024-01-15T10:00:00Z") => "2 hours ago"
 */
export function formatTimeAgo(date: string | Date): string {
  const d = typeof date === "string" ? new Date(date) : date;
  const now = Date.now();
  const diffMs = now - d.getTime();
  const diffSeconds = Math.floor(diffMs / 1000);
  const diffMinutes = Math.floor(diffSeconds / 60);
  const diffHours = Math.floor(diffMinutes / 60);
  const diffDays = Math.floor(diffHours / 24);
  const diffWeeks = Math.floor(diffDays / 7);
  const diffMonths = Math.floor(diffDays / 30);
  const diffYears = Math.floor(diffDays / 365);

  if (diffSeconds < 60) return "just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  if (diffDays < 7) return `${diffDays}d ago`;
  if (diffWeeks < 4) return `${diffWeeks}w ago`;
  if (diffMonths < 12) return `${diffMonths}mo ago`;
  return `${diffYears}y ago`;
}

/**
 * Format a number with commas.
 * Example: formatNumber(1234567) => "1,234,567"
 */
export function formatNumber(value: number, decimals: number = 0): string {
  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
}

/**
 * Format a compact number (e.g., 1.2K, 3.4M).
 */
export function formatCompactNumber(value: number): string {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 2,
  }).format(value);
}
