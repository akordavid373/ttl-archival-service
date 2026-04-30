import { format, parseISO } from "date-fns";
import { SupportedLanguage } from "./i18n";

// Locale mappings for date-fns
const dateLocales = {
  en: "en-US",
  ar: "ar-SA",
  he: "he-IL",
  es: "es-ES",
  fr: "fr-FR",
};

// Number formatting options per locale
const numberFormatOptions: Record<SupportedLanguage, Intl.NumberFormatOptions> =
  {
    en: {
      style: "decimal",
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
    },
    ar: {
      style: "decimal",
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
      useGrouping: true,
    },
    he: {
      style: "decimal",
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
      useGrouping: true,
    },
    es: {
      style: "decimal",
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
      useGrouping: true,
    },
    fr: {
      style: "decimal",
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
      useGrouping: true,
    },
  };

// Currency formatting options per locale
const currencyFormatOptions: Record<
  SupportedLanguage,
  Intl.NumberFormatOptions
> = {
  en: {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
  },
  ar: {
    style: "currency",
    currency: "SAR",
    minimumFractionDigits: 2,
  },
  he: {
    style: "currency",
    currency: "ILS",
    minimumFractionDigits: 2,
  },
  es: {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
  },
  fr: {
    style: "currency",
    currency: "EUR",
    minimumFractionDigits: 2,
  },
};

// Date formatting patterns per locale
const dateFormatPatterns: Record<SupportedLanguage, string> = {
  en: "MMM dd, yyyy",
  ar: "dd MMMM, yyyy",
  he: "dd MMMM, yyyy",
  es: "dd MMM, yyyy",
  fr: "dd MMM yyyy",
};

// Time formatting patterns per locale
const timeFormatPatterns: Record<SupportedLanguage, string> = {
  en: "h:mm a",
  ar: "HH:mm",
  he: "HH:mm",
  es: "HH:mm",
  fr: "HH:mm",
};

// DateTime formatting patterns per locale
const dateTimeFormatPatterns: Record<SupportedLanguage, string> = {
  en: "MMM dd, yyyy h:mm a",
  ar: "dd MMMM, yyyy HH:mm",
  he: "dd MMMM, yyyy HH:mm",
  es: "dd MMM, yyyy HH:mm",
  fr: "dd MMM yyyy HH:mm",
};

/**
 * Format a number according to the locale
 */
export const formatNumber = (
  value: number,
  locale: SupportedLanguage = "en",
  options?: Intl.NumberFormatOptions,
): string => {
  const formatOptions = { ...numberFormatOptions[locale], ...options };
  return new Intl.NumberFormat(dateLocales[locale], formatOptions).format(
    value,
  );
};

/**
 * Format a currency amount according to the locale
 */
export const formatCurrency = (
  value: number,
  locale: SupportedLanguage = "en",
  currency?: string,
): string => {
  const formatOptions = { ...currencyFormatOptions[locale] };
  if (currency) {
    formatOptions.currency = currency;
  }
  return new Intl.NumberFormat(dateLocales[locale], formatOptions).format(
    value,
  );
};

/**
 * Format a percentage according to the locale
 */
export const formatPercentage = (
  value: number,
  locale: SupportedLanguage = "en",
  options?: Intl.NumberFormatOptions,
): string => {
  const formatOptions = {
    style: "percent" as const,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
    ...options,
  };
  return new Intl.NumberFormat(dateLocales[locale], formatOptions).format(
    value,
  );
};

/**
 * Format file size according to the locale
 */
export const formatFileSize = (
  bytes: number,
  locale: SupportedLanguage = "en",
): string => {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${formatNumber(size, locale, { maximumFractionDigits: 1 })} ${units[unitIndex]}`;
};

/**
 * Format a date according to the locale
 */
export const formatDate = (
  date: string | Date,
  locale: SupportedLanguage = "en",
  pattern?: string,
): string => {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  const formatPattern = pattern || dateFormatPatterns[locale];

  try {
    return format(dateObj, formatPattern);
  } catch (error) {
    console.error("Date formatting error:", error);
    return dateObj.toLocaleDateString(dateLocales[locale]);
  }
};

/**
 * Format a time according to the locale
 */
export const formatTime = (
  date: string | Date,
  locale: SupportedLanguage = "en",
  pattern?: string,
): string => {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  const formatPattern = pattern || timeFormatPatterns[locale];

  try {
    return format(dateObj, formatPattern);
  } catch (error) {
    console.error("Time formatting error:", error);
    return dateObj.toLocaleTimeString(dateLocales[locale]);
  }
};

/**
 * Format a datetime according to the locale
 */
export const formatDateTime = (
  date: string | Date,
  locale: SupportedLanguage = "en",
  pattern?: string,
): string => {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  const formatPattern = pattern || dateTimeFormatPatterns[locale];

  try {
    return format(dateObj, formatPattern);
  } catch (error) {
    console.error("DateTime formatting error:", error);
    return dateObj.toLocaleString(dateLocales[locale]);
  }
};

/**
 * Format a relative date (e.g., "2 hours ago")
 */
export const formatRelativeTime = (
  date: string | Date,
  locale: SupportedLanguage = "en",
): string => {
  const dateObj = typeof date === "string" ? parseISO(date) : date;
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - dateObj.getTime()) / 1000);

  const rtf = new Intl.RelativeTimeFormat(dateLocales[locale], {
    numeric: "auto",
  });

  if (diffInSeconds < 60) {
    return rtf.format(-diffInSeconds, "second");
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return rtf.format(-minutes, "minute");
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return rtf.format(-hours, "hour");
  } else if (diffInSeconds < 2592000) {
    const days = Math.floor(diffInSeconds / 86400);
    return rtf.format(-days, "day");
  } else if (diffInSeconds < 31536000) {
    const months = Math.floor(diffInSeconds / 2592000);
    return rtf.format(-months, "month");
  } else {
    const years = Math.floor(diffInSeconds / 31536000);
    return rtf.format(-years, "year");
  }
};
