/**
 * API Client — wraps the Hey-API generated client with Firebase JWT injection.
 * Preserves the existing API surface (api.getMe(), api.updateMe(), etc.)
 */

import { auth } from '@/lib/firebase';
import { client, UsuariosService, StripeService, HealthService, PlansService } from '@/client/client.gen';
import type { Usuario, UsuarioUpdate, CheckoutRequest, CheckoutResult, HealthResponse, PlanResponse } from '@/client/client.gen';

// ── Config ───────────────────────────────────────────────────────────────────
const DEFAULT_TIMEOUT = 10_000; // 10s

// ── Error personalizado ─────────────────────────────────────────────────────
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

// ── Wrapper with JWT injection ───────────────────────────────────────────────
/**
 * Wraps the Hey-API client methods with Firebase JWT auth injection.
 * The underlying client uses fetch, so we intercept to add the Authorization header.
 */
const createAuthProxy = <T extends object>(service: T): T => {
  return new Proxy(service, {
    get(target, prop) {
      const original = (target as any)[prop];
      if (typeof original !== 'function') return original;

      return async (...args: any[]) => {
        const token = await auth.currentUser?.getIdToken(false);
        if (token) {
          client.setConfig?.({
            headers: { Authorization: `Bearer ${token}` },
          });
        }
        return original.apply(target, args);
      };
    },
  });
};

const usuariosService = createAuthProxy(UsuariosService);
const stripeService = createAuthProxy(StripeService);
const healthService = createAuthProxy(HealthService);
const plansService = createAuthProxy(PlansService);

// ── API pública ──────────────────────────────────────────────────────────────
export const api = {
  // Health
  health: () =>
    healthService.health().then((res) => res as HealthResponse),

  // Usuarios
  getMe: () =>
    usuariosService.getMe().then((res) => res as Usuario),

  updateMe: (data: UsuarioUpdate) =>
    usuariosService.updateMe(data).then((res) => res as Usuario),

  // Plans
  getPlans: () =>
    plansService.getPlans().then((res) => res as PlanResponse[]),

  // Stripe
  createCheckout: (lookupKey: string) =>
    stripeService
      .checkout({ lookup_key: lookupKey })
      .then((res) => ({ url: (res as CheckoutResult).url })),

  createPortal: () =>
    stripeService.portal().then((res) => ({ url: (res as PortalResult).url })),
};

export type ApiClient = typeof api;