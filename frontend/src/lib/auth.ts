export function saveToken(token: string) {
  if (typeof window !== 'undefined') {
    localStorage.setItem('token', token);
  }
}

export function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('token');
}

export function removeToken() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('token');
  }
}

export function isLoggedIn(): boolean {
  return !!getToken();
}

export function getGitHubLoginUrl(): string {
  const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
  return `${apiBase}/auth/github/login`;
}
