/**
 * Raw color values for props that can't use Tailwind classes
 * (icon `color`, ActivityIndicator, placeholderTextColor, …).
 * Keep in sync with tailwind.config.js.
 */
export const colors = {
  background: "#090b09",
  foreground: "#f4f7f5",
  card: "#181b18",
  elevated: "#151816",
  primary: "#16a34a",
  secondary: "#1f231f",
  muted: "#1f231f",
  mutedForeground: "#9aa39c",
  border: "#323834",
  input: "#323834",
  ring: "#22c55e",
  destructive: "#ef4444",
  faint: "#6b746e",
  successSoft: "#86efac",
  green300: "#86efac",
  green400: "#4ade80",
  green500: "#22c55e",
  amber300: "#fcd34d",
  red300: "#fca5a5",
  red400: "#f87171"
} as const;
