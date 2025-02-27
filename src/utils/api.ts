import { TOKEN_STORAGE_KEY } from "@/stores/session";

export class ApiError extends Error {
  public status: number;
  public ok: boolean;

  constructor(message: string, response: Response) {
    super(message || response.statusText);
    this.status = response.status;
    this.ok = response.ok;
  }
}

export async function doFetch(url: string, options?: RequestInit) {
  const access_token = localStorage.getItem(TOKEN_STORAGE_KEY);
  const headers: HeadersInit = {};
  if (access_token) {
    headers.Authorization = `Bearer ${access_token}`;
  }

  if (!url.includes("http")) {
    url = `${import.meta.env.VITE_API_URL}${url.startsWith("/") ? "" : "/"}${url}`;
  }

  const builtOptions = {
    ...options,
    headers: {
      ...options?.headers,
      ...headers
    }
  };

  const response = await fetch(url, builtOptions);

  if (!response.ok) {
    const json = await response.json();
    const content = json?.detail || (await response.text());
    const message = `(${response.status}) ${content || response.statusText}`;
    throw new ApiError(message, response);
  }

  if (response.status === 204) return;

  return await response.json();
}

export async function get<T = any>(url: string): Promise<T> {
  return doFetch(url);
}

export async function post<T = any>(
  url: string,
  body?: object,
  headers?: Record<string, string>
): Promise<T> {
  const options = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...headers
    },
    body: JSON.stringify(body)
  };

  return doFetch(url, options);
}

export async function put<T = any>(
  url: string,
  body?: object,
  headers?: Record<string, string>
): Promise<T> {
  const options = {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
      ...headers
    },
    body: JSON.stringify(body)
  };

  return doFetch(url, options);
}

export async function patch<T = any>(
  url: string,
  body?: object,
  headers?: Record<string, string>
): Promise<T> {
  const options = {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
      ...headers
    },
    body: JSON.stringify(body)
  };

  return doFetch(url, options);
}

export async function del(url: string): Promise<any> {
  const options = {
    method: "DELETE"
  };
  return doFetch(url, options);
}

export async function postFile<T = any>(url: string, file: FormData): Promise<T> {
  const options = {
    method: "POST",
    body: file
  };

  return doFetch(url, options);
}
