/**
 * API Client — wraps the Hey-API generated client with Firebase JWT injection.
 * Preserves the existing API surface (api.getMe(), api.updateMe(), etc.)
 */

import { auth } from '@/lib/firebase';
import { client, UsuariosService, StripeService, HealthService, PlansService } from '@/client/client.gen';
import type { UsuarioUpdate } from '@/client/client.gen';

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
  health: () => healthService.health(),

  // Usuarios
  getMe: () => usuariosService.getMe(),
  updateMe: (data: UsuarioUpdate) => usuariosService.updateMe(data),

  // Plans
  getPlans: () => plansService.getPlans(),

  // Stripe
  createCheckout: (lookupKey: string) =>
    stripeService.checkout({ lookup_key: lookupKey }),

  createPortal: () => stripeService.portal(),
};

export type ApiClient = typeof api;

// ── Auth helper for hooks ──────────────────────────────────────────────────
export async function getAuthHeader(): Promise<string> {
  const token = await auth.currentUser?.getIdToken(true);
  return token ? `Bearer ${token}` : '';
}
