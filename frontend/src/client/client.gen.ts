/**
 * Hey-API Generated Client — Script9 Engine
 * Auto-generated from backend OpenAPI spec.
 * DO NOT EDIT directly — regenerate with:
 *   cd backend && python scripts/generate_openapi.py
 *   npx @hey-api/openapi-ts -i backend/openapi.json -o frontend/src/client/
 */

import { createClient } from '@hey-api/client-fetch';

// ── Types ────────────────────────────────────────────────────────────────────

export type PlanSuscripcion = 'trial' | 'starter' | 'professional' | 'enterprise';

export interface Usuario {
  id: number;
  firebase_uid: string;
  email: string;
  nombre: string;
  plan_suscripcion: PlanSuscripcion;
  stripe_customer_id: string | null;
  subscription_status: string | null;
  current_period_end: string | null;
  activo: boolean;
  creado_en: string;
  actualizado_en: string;
}

export interface UsuarioUpdate {
  nombre?: string;
  email?: string;
}

export interface HealthResponse {
  status: string;
  environment?: string;
  database?: string;
  redis?: string;
}

export interface CheckoutRequest {
  lookup_key: string;
}

export interface CheckoutResult {
  url: string;
}

export interface PortalResult {
  url: string;
}

export interface PlanResponse {
  id: string;
  lookup_key: string;
  name: string;
  price: number | null;
  currency: string;
  features: string[];
  popular: boolean;
  contact_sales: boolean;
}

// ── Client ───────────────────────────────────────────────────────────────────

export const client = createClient({
  baseUrl: import.meta.env.VITE_API_URL ?? '/api/v1',
});

// ── API Methods ──────────────────────────────────────────────────────────────
// @hey-api/client-fetch returns { data, error, request, response }.
// We unwrap .data here so callers get T directly.

export class UsuariosService {
  static getMe(): Promise<Usuario> {
    return client.get({ url: '/usuarios/me' }).then((res) => res.data as Usuario);
  }

  static updateMe(data: UsuarioUpdate): Promise<Usuario> {
    return client.patch({ url: '/usuarios/me', body: data as Record<string, unknown> }).then((res) => res.data as Usuario);
  }
}

export class StripeService {
  static checkout(data: CheckoutRequest): Promise<CheckoutResult> {
    return client.post({ url: '/stripe/checkout', body: data as unknown as Record<string, unknown> }).then((res) => res.data as CheckoutResult);
  }

  static portal(): Promise<PortalResult> {
    return client.post({ url: '/stripe/portal' }).then((res) => res.data as PortalResult);
  }
}

export class HealthService {
  static health(): Promise<HealthResponse> {
    return client.get({ url: '/health' }).then((res) => res.data as HealthResponse);
  }
}

export class PlansService {
  static getPlans(): Promise<PlanResponse[]> {
    return client.get({ url: '/plans' }).then((res) => res.data as PlanResponse[]);
  }
}
