import { TOKEN_STORAGE_KEY } from "@/stores/session";
import { ApiError } from "./api";
import { parseApiErrorBody } from "./errors";

export type SseHandler<T> = (event: T) => void;

/** POST and consume a text/event-stream body as JSON `data:` frames. */
export async function postSse<T extends { status?: string }>(
  url: string,
  body: object | undefined,
  onEvent: SseHandler<T>,
  signal?: AbortSignal
): Promise<void> {
  const access_token = localStorage.getItem(TOKEN_STORAGE_KEY);
  let fullUrl = url;
  if (!fullUrl.includes("http")) {
    fullUrl = `${import.meta.env.VITE_API_URL}${url.startsWith("/") ? "" : "/"}${url}`;
  }

  const response = await fetch(fullUrl, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "text/event-stream",
      ...(access_token ? { Authorization: `Bearer ${access_token}` } : {})
    },
    body: JSON.stringify(body ?? {}),
    signal
  });

  if (!response.ok) {
    let body: unknown = null;
    try {
      body = await response.json();
    } catch {
      body = null;
    }
    const parsed = parseApiErrorBody(body);
    throw new ApiError(parsed.userMessage, response, {
      userMessage: parsed.userMessage,
      detail: parsed.detail,
      code: parsed.code
    });
  }

  if (!response.body) {
    throw new Error("No response body for SSE stream");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let done = false;

  while (!done) {
    const result = await reader.read();
    done = result.done;
    if (done) break;
    buffer += decoder.decode(result.value, { stream: true });
    const chunks = buffer.split("\n\n");
    buffer = chunks.pop() ?? "";
    for (const chunk of chunks) {
      const lines = chunk.split("\n");
      for (const line of lines) {
        if (!line.startsWith("data:")) continue;
        const raw = line.slice(5).trim();
        if (!raw) continue;
        try {
          const parsed = JSON.parse(raw) as T;
          onEvent(parsed);
        } catch {
          // ignore malformed frames
        }
      }
    }
  }
}
