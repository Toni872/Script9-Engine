# Handoff: Migración de Tempos a script9-billing

## ¿Qué pasó?

Se creó `script9-billing`, un módulo compartido de facturación Stripe para todo el
ecosistema Script9. Tempos va a reemplazar su `billing.controller.ts` actual por este
módulo.

## Instalación

En el backend de Tempos (Node/Express):

```bash
npm install @script9/billing
# o si es paquete local:
npm install ./packages/script9-billing
```

> **Nota:** El módulo está hecho en Python. Para Node.js, necesitamos portarlo o
> usar un wrapper HTTP. La alternativa más limpia: que Tempos consuma el módulo
> como API HTTP (Script9 Engine expone los endpoints, Tempos llama a ellos).
>
> **Opción recomendada:** Mantener Tempos con su propia lógica de Stripe por ahora,
> usando el mismo patrón pero NO el mismo código. La centralización está en las
> claves de Stripe y las URLs de retorno, no en el código.

## Lo que NO cambia en Tempos

- ✅ Sigue teniendo su propio backend
- ✅ Sigue recibiendo webhooks directamente de Stripe
- ✅ Sigue manejando su propia DB (activar premium)
- ✅ Los endpoints son los mismos: `POST /api/v1/billing/create-checkout-session`
  `POST /api/v1/billing/create-portal-session`
  `POST /api/v1/billing/webhook`

## Lo que SÍ cambia en Tempos

### 1. Lookup keys (NO price_id)

**Antes:**
```ts
const { price_id } = req.body;
// Buscar price_id directo
```

**Ahora:**
```ts
const { lookup_key } = req.body; // "starter_monthly"
// Stripe resuelve el price_id automáticamente
const prices = await stripe.prices.list({
  lookup_keys: [lookup_key],
  expand: ["data.product"],
});
const priceId = prices.data[0].id;
```

### 2. Metadata con appName

**Antes:** (opcional)
```ts
metadata: { userId: user.uid }
```

**Ahora:**
```ts
metadata: {
  userId: user.uid,
  appName: "Tempos"  // ← NUEVO: identifica la app origen
}
```

### 3. URLs de retorno al hub

**Antes:**
```ts
success_url: `${temposUrl}/success`,
cancel_url: `${temposUrl}/pricing`,
```

**Ahora:**
```ts
const script9Url = "https://www.script-9.com";
success_url: `${script9Url}/pago-exitoso?app=tempos`,
cancel_url: `${script9Url}/dashboard`,
return_url: `${script9Url}/dashboard`,
```

### 4. automatic_tax

**Antes:** (no existía)

**Ahora:**
```ts
automatic_tax: { enabled: true },
```

### 5. customer.subscription.created

Agregar manejo del evento `customer.subscription.created` en el webhook (además de
`checkout.session.completed`, `updated`, `deleted`).

## Resumen de cambios en billing.controller.ts

```diff
- const { price_id } = req.body;
+ const { lookup_key } = req.body;

- const priceId = req.body.price_id;
+ const prices = await stripe.prices.list({ lookup_keys: [lookup_key] });
+ const priceId = prices.data[0].id;

+ metadata: { userId: user.uid, appName: "Tempos" },

- success_url: `${process.env.FRONTEND_URL}/success`,
+ success_url: `https://www.script-9.com/pago-exitoso?app=tempos`,

- cancel_url: `${process.env.FRONTEND_URL}/pricing`,
+ cancel_url: `https://www.script-9.com/dashboard`,

+ automatic_tax: { enabled: true },
```

## Variables de entorno (lo que se puede limpiar)

Tempos ya no necesita estas vars si usan lookup keys:
- `STRIPE_STARTER_PRICE_ID` → ❌ Eliminar (usa lookup_key)
- `STRIPE_PROFESSIONAL_PRICE_ID` → ❌ Eliminar
- `STRIPE_ENTERPRISE_PRICE_ID` → ❌ Eliminar
- `SCRIPT9_URL` → ✅ Mantener (o hardcodear como `https://www.script-9.com`)
- `FRONTEND_URL` → ✅ Mantener (para CORS, no para URLs de Stripe)

## End-to-end flow verificado

```
Usuario → Tempos Frontend
  → POST /api/v1/billing/create-checkout-session { lookup_key: "starter_monthly" }
  → Stripe Checkout (metadata: userId + appName: "tempos")
  → Redirige a script-9.com/pago-exitoso?app=tempos
  → Webhook Stripe → Tempos Backend → activa premium en DB de Tempos
  → Customer Portal → script-9.com/dashboard
```
