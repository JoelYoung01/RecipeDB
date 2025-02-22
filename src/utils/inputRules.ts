export function required(value?: string | number) {
  return !!`${value}`.trim() || "This field is required.";
}

export function isNumber(value?: string | number) {
  return !Number.isNaN(Number(value)) || "Value must be a valid number";
}
