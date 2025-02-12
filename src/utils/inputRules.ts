export function required(value?: string | number) {
  return !!`${value}`.trim() || "This field is required.";
}
