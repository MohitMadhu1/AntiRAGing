const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

function getAuthHeaders(): Record<string, string> {
  if (typeof window === 'undefined') return {};
  const token = localStorage.getItem('token');
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
}

export async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { ...getAuthHeaders() },
  });
  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  return res.json();
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
    },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  return res.json();
}

export async function getJobs() {
  return await apiGet('/jobs/');
}

export async function getUserRepos() {
  return await apiGet('/github/repos');
}

export function createSSEConnection(path: string, onMessage: (data: Record<string, unknown>) => void, signal?: AbortSignal) {
  const url = `${API_BASE}${path}`;

  const fetchSSE = async () => {
    try {
      const res = await fetch(url, { signal });
    const reader = res.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) return;

    let buffer = '';
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop() || '';

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          try {
            const data = JSON.parse(line.slice(6));
            onMessage(data);
          } catch {
            // ignore parse errors
          }
        }
      }
    }
    } catch (err: unknown) {
      if ((err as Error).name !== 'AbortError') {
        console.error('SSE Error:', err);
      }
    }
  };

  fetchSSE();
}
