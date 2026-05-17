import { auth } from '@/lib/firebase';
import { type z } from 'zod';
import type { ActualizarPerfil } from './zod-schemas';
import { UsuarioSchema, ApiErrorSchema, HealthSchema } from './zod-schemas';

// ── Config ──────────────────────────────────────────────────
const API_BASE_URL = import.meta.env.VITE_API_URL ?? '/api/v1';
const DEFAULT_TIMEOUT = 10_000; // 10s

// ── Error personalizado ─────────────────────────────────────
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

// ── Cliente base ────────────────────────────────────────────
async function request<T>(
  path: string,
  options: RequestInit = {},
  schema?: z.ZodType<T>,
): Promise<T> {
  // Obtener token JWT de Firebase
  const token = await auth.currentUser?.getIdToken(false);

  const headers: HeadersInit = {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.body instanceof FormData
      ? {}
      : { 'Content-Type': 'application/json' }),
    ...options.headers,
  };

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
      signal: controller.signal,
    });

    if (!response.ok) {
      let detail = `HTTP ${response.status}`;
      try {
        const body = await response.json();
        const parsed = ApiErrorSchema.safeParse(body);
        if (parsed.success) detail = parsed.data.detail;
      } catch { /* ignore parse errors */ }
      throw new ApiError(
        `Error en la petición: ${response.status}`,
        response.status,
        detail,
      );
    }

    // 204 No Content
    if (response.status === 204) return undefined as T;

    const data = await response.json();

    if (schema) {
      const parsed = schema.safeParse(data);
      if (!parsed.success) {
        console.error('[API] Zod validation error:', parsed.error.issues);
        throw new ApiError('Error de validación de datos', 500);
      }
      return parsed.data;
    }

    return data as T;
  } finally {
    clearTimeout(timeoutId);
  }
}

// ── Métodos helpers ─────────────────────────────────────────
function get<T>(path: string, schema?: z.ZodType<T>) {
  return request<T>(path, { method: 'GET' }, schema);
}

function post<T>(path: string, body?: unknown, schema?: z.ZodType<T>) {
  return request<T>(
    path,
    { method: 'POST', body: body ? JSON.stringify(body) : undefined },
    schema,
  );
}

function patch<T>(path: string, body?: unknown, schema?: z.ZodType<T>) {
  return request<T>(
    path,
    { method: 'PATCH', body: body ? JSON.stringify(body) : undefined },
    schema,
  );
}

function del<T = void>(path: string) {
  return request<T>(path, { method: 'DELETE' });
}

// ── API pública ─────────────────────────────────────────────
export const api = {
  // Health
  health: () => get('/health', HealthSchema),

  // Usuarios
  getMe: () => get('/usuarios/me', UsuarioSchema),
  updateMe: (data: ActualizarPerfil) =>
    patch('/usuarios/me', data, UsuarioSchema),

  // Genérico (para futuros endpoints)
  get,
  post,
  patch,
  delete: del,
};

export type ApiClient = typeof api;
