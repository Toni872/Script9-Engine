import { z } from 'zod';

// ── Planes de suscripción ───────────────────────────────────
export const PlanSuscripcionSchema = z.enum([
  'trial',
  'starter',
  'professional',
  'enterprise',
]);

// ── Usuario (respuesta del backend) ─────────────────────────
export const UsuarioSchema = z.object({
  id: z.number(),
  firebase_uid: z.string(),
  email: z.string().email(),
  nombre: z.string(),
  plan_suscripcion: PlanSuscripcionSchema.default('trial'),
  stripe_customer_id: z.string().nullable().optional(),
  activo: z.boolean().default(true),
  creado_en: z.string(),
  actualizado_en: z.string(),
});
export type Usuario = z.infer<typeof UsuarioSchema>;

// ── Actualizar perfil (PATCH /me) ───────────────────────────
export const ActualizarPerfilSchema = z.object({
  nombre: z.string().min(2, 'El nombre debe tener al menos 2 caracteres').max(100).optional(),
  email: z.string().email('Email inválido').optional(),
});
export type ActualizarPerfil = z.infer<typeof ActualizarPerfilSchema>;

// ── Error API ────────────────────────────────────────────────
export const ApiErrorSchema = z.object({
  detail: z.string(),
});
export type ApiError = z.infer<typeof ApiErrorSchema>;

// ── Health Check ─────────────────────────────────────────────
export const HealthSchema = z.object({
  status: z.string(),
  environment: z.string().optional(),
  database: z.string().optional(),
  redis: z.string().optional(),
});
export type HealthResponse = z.infer<typeof HealthSchema>;
