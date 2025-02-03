export function formatDate(
  dateString?: string,
  excludeCurrentYear = false,
  includeTime = false
): string {
  if (!dateString) return "";

  const isoNoTzRegex = /^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d{3})?)$/;
  if (isoNoTzRegex.test(dateString)) {
    // All iso date times are assumed to be in UTC, since SQLite can't store TZ
    dateString += "Z";
  }

  const date = new Date(dateString);
  const today = new Date();

  const sameYear = date.getFullYear() === today.getFullYear();

  const options: Intl.DateTimeFormatOptions = {
    year: sameYear && excludeCurrentYear ? undefined : "numeric",
    month: "short",
    day: "numeric"
  };

  if (includeTime) {
    options.hour = "2-digit";
    options.minute = "2-digit";
  }

  return date.toLocaleDateString(undefined, options);
}
