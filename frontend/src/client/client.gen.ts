/**
 * Hey-API Generated Client — Script9 Engine
 * Auto-generated from backend OpenAPI spec.
 * DO NOT EDIT directly — regenerate with:
 *   cd backend && python scripts/generate_openapi.py
 *   npx @hey-api/openapi-ts -i backend/openapi.json -o frontend/src/client/
 */

import type { CancelablePromise } from '@hey-api/client-fetch';
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

// ── Client ───────────────────────────────────────────────────────────────────

export const client = createClient({
  baseUrl: import.meta.env.VITE_API_URL ?? '/api/v1',
});

// ── API Methods ──────────────────────────────────────────────────────────────

export class UsuariosService {
  /**
   * GET /api/v1/usuarios/me
   * Returns the authenticated user's profile.
   */
  static getMe(): CancelablePromise<Usuario> {
    return client.get('/usuarios/me', {
      responseSchema: undefined, // types only — Zod validation happens in api-client.ts
    });
  }

  /**
   * PATCH /api/v1/usuarios/me
   * Updates the authenticated user's profile.
   */
  static updateMe(data: UsuarioUpdate): CancelablePromise<Usuario> {
    return client.patch('/usuarios/me', {
      body: data,
    });
  }
}

export class StripeService {
  /**
   * POST /api/v1/stripe/checkout
   * Creates a Stripe Checkout session.
   */
  static checkout(data: CheckoutRequest): CancelablePromise<CheckoutResult> {
    return client.post('/stripe/checkout', {
      body: data,
    });
  }

  /**
   * POST /api/v1/stripe/portal
   * Creates a Stripe Customer Portal session.
   */
  static portal(): CancelablePromise<PortalResult> {
    return client.post('/stripe/portal');
  }
}

export class HealthService {
  /**
   * GET /api/v1/health
   * Health check endpoint.
   */
  static health(): CancelablePromise<HealthResponse> {
    return client.get('/health');
  }
}

// ── Plans ─────────────────────────────────────────────────────────────────────

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

export class PlansService {
  /**
   * GET /api/v1/plans
   * Returns the catalog of available plans from Stripe.
   */
  static getPlans(): CancelablePromise<PlanResponse[]> {
    return client.get('/plans');
  }
}