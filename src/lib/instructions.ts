/** Split recipe instructions into visual steps (newline-delimited paragraphs). */
export function splitInstructionSteps(instructions: string): string[] {
  return instructions
    .replace(/\r\n/g, "\n")
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);
}
