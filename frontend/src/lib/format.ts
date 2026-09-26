export function formatDate(value?: string | null) {
  if (!value) return "Not available";
  return new Date(value).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

export function formatDuration(seconds?: number | null) {
  if (seconds == null) return "--:--";
  const minutes = Math.floor(Math.max(0, seconds) / 60);
  const rest = Math.max(0, seconds) % 60;
  return `${minutes}:${String(rest).padStart(2, "0")}`;
}

export function imageUrl(path?: string) {
  if (!path) return "";
  if (path.startsWith("http") || path.startsWith("/")) return path;
  return `/static/${path}`;
}
