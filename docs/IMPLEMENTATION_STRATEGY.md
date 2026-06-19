# Script9 Engine — Estrategia de Implementación

> Documento de arquitectura estratégica. De la situación actual (scaffold + auth + Stripe) a la "aplicación par excellence" alineada con `www.script-9.com`.
> Lengua: castellano de España. Toda decisión está justificada con `file:line` cuando toca código concreto.

---

## 1. Visión y principios rectores

### Visión (un párrafo)

Script9 Engine es el **hub B2B de automatización de la consultoría Script-9**: un único backend que ofrece identidad, facturación y telemetría a N aplicaciones hermanas (hoy Tempos, mañana las que vengan), con un frontend React que se siente como una extensión natural de `www.script-9.com` — mismo lenguaje visual, misma fluidez de navegación, misma opacidad estratégica sobre precios. El producto final no es "un SaaS más": es la **oficina digital de Antonio**: cada cliente entra con una invitación personal, ve un panel vivo con la actividad que importa, paga una cifra que solo él conoce y usa los servicios que Antonio le ha activado.

### Principios no negociables

1. **Backend primero, frontend como consumidor.** La API (OpenAPI) es la única fuente de verdad. El frontend se regenera desde el schema con Hey-API. No se escribe a mano un cliente paralelo al `api-client.ts:23` actual.
2. **Multi-tenant por defecto.** Cada entidad tiene un discriminador `app` o un esquema segregado. Hoy el código asume un único tenant (`script9`); el salto a N tenants debe ser retrocompatible — sin reescritura.
3. **Precio invisible.** Nada de tarifas públicas. La página `/pricing` desaparece como vitrina de números y se convierte en una landing "Hablemos". La cifra la decide Antonio en privado; el sistema la materializa en una `Cotizacion` y un `price_id` por cliente.
4. **Marca única con `script-9.com`.** Mismo React 18 + Vite 6 + TS 5.5 strict + Framer Motion 11 + Tailwind 3, misma paleta emerald/slate, mismas animaciones (cube 3D, glass-blur, aura-glow, tech-grid), misma tipografía Inter + JetBrains Mono. El producto se siente hijo de la web pública, no un primo lejano.
5. **Tests herméticos y suficientes.** Backend: 80 % in-scope mínimo, suite estable. Frontend: vitest para unidades + Playwright para flujos críticos. TDD en los flujos de facturación y en los dos bugs conocidos.
6. **Observabilidad no es opcional.** Structlog en JSON, Sentry en frontend + backend, `/health` con checks reales, request-id en cada log. Si pasa un error en producción, debe verse con contexto.
7. **Nada de "próximamente" visible al usuario.** El dashboard muestra **una métrica real, viva**, desde el día uno de la Fase 1. Si no hay datos, se muestra el estado vacío con copy honesto, nunca un placeholder muerto.

---

## 2. Alcance del producto (qué hace, qué NO hace)

### 2.1. El primer journey end-to-end (mata el "próximamente")

El `Dashboard.tsx:202-204` actual dice literalmente: *"No hay actividad reciente — próximamente con métricas y fichajes."* Eso se va. La métrica viva de la Fase 1 es **"Leads capturados esta semana"**, y el flow que la genera es la **columna vertebral** del producto v1.

**Journey elegido: Captura → Calificación → Enrutamiento → Reunión → Sincronización CRM → Dashboard vivo**

Justificación:
- Es el caso de uso que Antonio ya vende en `script-9.com` (automatización de leads).
- Cubre los seis componentes críticos: formulario público, motor de reglas, calendario, integración externa, evento de dominio, render en vivo.
- Es replicable: el mismo motor sirve después para Tempos u otros.
- Tiene un resultado medible y monetizable: cada lead cualificado es valor de negocio.

**Pasos del journey:**

1. **Captura.** Un visitante llega a un formulario público embebible (`/l/<slug>` o `script-9.com/contacto`). Deja nombre, email, empresa, mensaje. Se crea un `Lead` con `origen`, `slug` y `app` (default `script9`).
2. **Calificación automática.** Al crearse, el `Lead` se puntúa con un motor de reglas declarativo (reglas en `app/services/lead_scoring.py`): tamaño de empresa (dominio email), palabras clave del mensaje, idioma, etc. Score 0-100.
3. **Enrutamiento.** Si score ≥ umbral (configurable por Antonio, p. ej. 70), se crea una `Meeting` propuesta y se envía email al lead con un enlace de scheduling. Si score < umbral, queda en cola para revisión manual.
4. **Scheduling.** El lead elige hueco en `app/services/calendar.py` (integración con Cal.com o Calendly via webhook de entrada). Al confirmar, la `Meeting` pasa a `confirmed` con timestamp.
5. **Sincronización CRM.** Webhook de salida (`/api/v1/webhooks/crm`) empuja `Lead` + `Meeting` a un CRM configurable (HubSpot por defecto, vía API key). El endpoint es idempotente.
6. **Dashboard vivo.** `Lead` y `Meeting` se persisten como `ActivityEvent` (`tipo='lead_captured'`, `tipo='meeting_scheduled'`, `metadata={...}`). El dashboard del usuario autenticado consume `/api/v1/activity/feed?range=7d` y renderiza:
   - **Tarjeta principal (1 número):** "Leads esta semana" con sparkline de 7 puntos.
   - **Lista lateral (5 items):** los últimos 5 eventos con icono (Phosphor), tiempo relativo, acción.

**Punto de fricción eliminado:** el usuario no configura nada. Entra al dashboard y ve datos reales. Si su cuenta tiene 0 leads, ve una CTA: *"Comparte tu primer formulario"* con un enlace corto `script-9.com/l/<slug>` listo para pegar en LinkedIn.

### 2.2. La primera métrica viva

**`Leads esta semana`** (un entero, una tarjeta, un sparkline). Endpoint `GET /api/v1/activity/metric/leads_this_week`:

```json
{ "value": 12, "delta_pct": 33.4, "sparkline": [0,1,2,1,3,2,3] }
```

- `value`: COUNT de `Lead` con `creado_en >= now() - 7d` y `app = 'script9'`.
- `delta_pct`: variación contra los 7 días anteriores.
- `sparkline`: array de 7 enteros, un punto por día.

Una sola query SQL agregada (GROUP BY day) + cálculo en Python. Sin cache en v1: el coste es despreciable. Si se vuelve lenta, cache Redis 5 min.

### 2.3. Lo que NO está en v1 (fronteras explícitas)

- **No es un CRM.** No hay pipelines multi-etapa, ni email marketing. Solo captura + score + reunión.
- **No es un constructor de formularios drag-and-drop.** El formulario es un componente único con campos fijos (nombre, email, empresa, mensaje). Configurable solo el `slug` y el `app`.
- **No es multi-idioma.** Castellano único. Si Tempos u otra app lo necesita, se aísla por `app` y se añade `i18n` en Fase 5.
- **No es un sistema de tickets.** `ActivityEvent` es telemetría de uso, no canal de soporte.
- **No es self-service signup.** La cuenta la crea Antonio con un `invite_token`; el usuario llega, acepta y entra.
- **No hay analítica de producto propia.** Firebase Analytics ya cubre lo que necesita Antonio (`lib/firebase.ts:20`).
- **No hay gestión de usuarios avanzada.** No hay roles, equipos, ni invitaciones a workspace. Una cuenta = un usuario = un dashboard. Los roles vienen en Fase 2.

---

## 3. Estrategia de precio invisible

### 3.1. Por qué y cómo

El `Pricing.tsx:9-51` actual **muestra precios públicos** ($29, $99, "Personalizado"). Eso se demuele. La nueva regla: **el precio es una conversación, no una página**.

### 3.2. El funnel rediseñado

```
script-9.com (web pública)
   │
   ├── "Hablemos"  →  mailto:antonio@script-9.com  o  Calendly de Antonio
   │
   │   (Antonio habla con el cliente, acuerdan precio X)
   │
   ├── Antonio crea el cliente en el back-office:
   │     - Crea el usuario en Firebase Auth
   │     - Crea Cotizacion(id, user_id, precio_eur, plan_interno, fecha)
   │     - En Stripe dashboard, crea Product+Price con el importe exacto
   │     - Comparte el price_id de vuelta al sistema
   │
   ├── Backend: Usuario.cotizacion_id + Cotizacion.stripe_price_id
   │
   ├── Antonio envía "invite link" al cliente:
   │     https://app.script-9.com/aceptar-invitacion?token=<jwt>
   │
   ├── Cliente entra, ve dashboard vacío, ve CTA "Activa tu cuenta"
   │
   └── Botón "Activar cuenta" → POST /api/v1/stripe/checkout
         (cliente NO envía lookup_key; backend lee Cotizacion.stripe_price_id
          del usuario autenticado y crea Checkout Session con ese price_id)
```

### 3.2.1. Cambios concretos

- **Nueva página `/planes`** (sustituye a `/pricing`): una sección con título *"Empieza con Script9 Engine"*, copy honesto, dos botones:
  - **"Hablar con Antonio"** → `mailto:antonio@script-9.com?subject=Interesado%20en%20Script9%20Engine`.
  - **"Ya tengo invitación"** → `/aceptar-invitacion?token=...`.
  - Sin cards, sin tiers, sin números.
- **Eliminación del `lookup_key` en la request del cliente.** El `CheckoutRequest` actual (`script9-billing/models.py:17-28`) acepta `lookup_key` del cliente. **El cliente nunca debe poder elegir el plan.** El nuevo `CheckoutRequest` se queda en `{}` (POST vacío con auth). El backend:
  1. Lee `Usuario.cotizacion_id`; si no hay, devuelve 400 *"Sin cotización asociada, contacta con ventas"*.
  2. Carga la `Cotizacion` y obtiene `stripe_price_id`.
  3. Crea la Checkout Session con ese `price_id` resuelto en el servidor.
- **Modelo de datos nuevo:** tabla `cotizaciones` (id, user_id FK, app, precio_eur numeric, plan_interno str, stripe_price_id str, creado_en, valido_hasta, notas_admin).
- **"Enterprise" eliminado como concepto público.** Enterprise es una cotización grande. No hay columna `plan = 'enterprise'`, no hay UI que lo muestre. El `plan_suscripcion` interno se reduce a tres valores: `trial`, `active` (pagado, sin distinguir tier), `suspended`. El tier interno vive en `Cotizacion.notas_admin` o en un futuro `PlanAssignment`.

### 3.3. Cómo encaja "Enterprise"

Enterprise **no es un plan, es una cotización grande**. Si el precio es > X (umbral interno, p. ej. 1.000 €/mes), el `plan_interno` se etiqueta como `enterprise` en la `Cotizacion`, lo que en el futuro (Fase 5) habilita features premium en el backend. Al cliente le da igual: ve "Activar cuenta" → paga → entra. Sin mención a tiers.

### 3.4. Cómo encajan las apps hermanas (Tempos, futuras)

Cada app tiene su **propia cotización invisible**. El contrato:

- Tempos tiene su propio `app = 'tempos'` en la tabla `cotizaciones`.
- Antonio (o un admin de Tempos) crea cotizaciones con `app = 'tempos'`.
- El `script9-billing` ya soporta `app_name` en metadata (`core.py:103-106`); el hub acepta cotizaciones de cualquier `app`.
- El frontend de Tempos consume los mismos endpoints pero con su propio `firebase_uid`. La cotización correcta se resuelve por `(user_id, app)`.
- La página de éxito (`SuccessPayment.tsx:5-12`) ya tiene el patrón de routing por `?app=tempos`; se mantiene.

**Regla de oro:** cada app ve su propio precio, pero la mecánica (Cotización → Checkout → Webhook → Activación) es **idéntica** y vive en `script9-billing`.

---

## 4. Stack final — confirmación y ajustes

### 4.1. Backend

**Se mantiene** (ya en `pyproject.toml:7-22`):

| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| Framework | FastAPI 0.115 | Async nativo, OpenAPI automático. |
| ORM | SQLAlchemy 2.0 async | Tipos nativos, control fino. |
| Driver | asyncpg 0.30 | Único viable para Postgres async en Python 3.12. |
| Auth | firebase-admin 6.6 | Ya integrado; auto-registro funciona (`auth.py:56-60`). |
| Billing | stripe 11.4 | SDK oficial. |
| Caché | redis 5.2 | Ya hay `mock_redis` en tests (`conftest.py:148`); usar en `/health` y session cache. |
| Settings | pydantic-settings 2.6 | Validado; falta añadir Secret Manager en prod. |
| Pydantic | 2.9 | Coherente. |

**Se activa** (Fase 0, ya declaradas pero no usadas):

- **alembic 1.14** (`pyproject.toml:15`): migraciones como gate de release. Se elimina `Base.metadata.create_all` en `main.py:21-22` en favor de Alembic.
- **structlog 24.4** (`pyproject.toml:20`): logging JSON en `staging`/`production`, consola coloreada en `local`. Init en el `lifespan` de `main.py`.
- **sentry-sdk[fastapi] 2.18** (`pyproject.toml:21`): init en `lifespan` cuando `settings.sentry_dsn` no esté vacío. `traces_sample_rate=0.2` en producción, 1.0 en local/staging.
- **slowapi 0.1** (`pyproject.toml:19`, no activado en `main.py:37-49`): 100 req/min IP global, 30 req/min en `/api/v1/stripe/checkout` y `/api/v1/auth/*`.
- **httpx 0.28** (`pyproject.toml:22`): para webhook de salida al CRM y para test del propio `webhook.py`.

**Cola asíncrona — decisión:** **No se introduce Celery, ARQ ni Dramatiq en v1**. El journey principal cabe en una request síncrona con latencia < 200 ms. La calificación es CPU-cheap. El envío de email usa `BackgroundTasks` de FastAPI (en proceso, sin infra extra). Para scoring pesado o integraciones CRM masivas, se introduce ARQ + Redis en Fase 5 (Redis ya está en `docker-compose.yml:27-38`).

### 4.2. Frontend

**Se mantiene** (`package.json:18-29`):

| Capa | Tecnología | Justificación |
|------|-----------|---------------|
| Build | Vite 6.0 | HMR instantáneo, code-splitting automático. |
| Lenguaje | TypeScript 5.5.4 strict | No negociable. |
| UI | React 18.3.1 | Concurrent rendering, `Suspense` listo. |
| Estado servidor | TanStack Query 5.51 | Caché, revalidación, optimistic updates. |
| Auth | Firebase 10.12 | Mismo proyecto que el backend. |
| Animación | Framer Motion 11.3 | Mismo lenguaje que `script-9.com`. |
| Validación | Zod 3.23 | Runtime + tipos desde un solo schema. |
| Router | React Router 6.25 | Loaders, nested routes, code-split por defecto. |
| Estilos | Tailwind 3.4 | Productivo + tokens centralizados. |
| Iconos | @phosphor-icons/react 2.1 | Coherente con `script-9.com`. |

**Se activa** (Fase 0):

- **@hey-api/openapi-ts 0.52** (`package.json:31`): genera `src/client/` desde `openapi.json`. Script `pnpm gen` encadena `python scripts/generate_openapi.py` + `openapi-ts`.
- **@hey-api/client-fetch 0.4** (`package.json:19`): sustituye al `api-client.ts:23-130` actual como cliente HTTP base. El wrapper se reduce a: (a) inyecta el `Bearer` token, (b) `onError` mapea 401 → redirect `/login`, (c) exporta tipos generados.
- **vitest 2.0** (`package.json:52`): setup con `@testing-library/react 16`, `jsdom 24`, `msw 2.3`. Cobertura mínima 75 % in-scope.
- **@playwright/test 1.45** (`package.json:32`): suite E2E con un único flujo crítico (`auth → dashboard → ver métrica`) y un test de regresión para los 2 bugs conocidos.

**i18n — decisión:** se difiere. Castellano único en v1. Cuando Tempos u otra app necesiten otro idioma, se introduce `react-i18next` con namespaces por `app`. La arquitectura de `appName` ya está implícita en `SuccessPayment.tsx:5-12`.

### 4.3. Infraestructura

**Se mantiene** (`docker-compose.yml`):
- Postgres 16 (`docker-compose.yml:9-25`).
- Redis 7 (`docker-compose.yml:27-38`).
- API en `8081` interno, expuesto en `8082` (`docker-compose.yml:48`).
- Frontend en `5174`.

**Inconsistencias a corregir (Fase 0):**

- `docker-compose.yml:63-65` define `STRIPE_STARTER_PRICE_ID`, `STRIPE_PROFESSIONAL_PRICE_ID`, `STRIPE_ENTERPRISE_PRICE_ID` que **ya no se usan** (el flujo nuevo resuelve el `price_id` desde la `Cotizacion`). Se eliminan.
- `docker-compose.yml:59` y `app/api/v1/stripe.py:36` discrepan en cómo se pasa el `app_name`. Con la nueva estrategia, el `app_name` se resuelve desde el `Usuario` o la `Cotizacion`, nunca del cliente.
- `backend/Dockerfile:1-30` no es multi-stage. Se trae el multi-stage de la guía (paso 12): `builder` + `production` + usuario no-root + gunicorn.
- `backend/Dockerfile.dev` usa Poetry; el `Dockerfile` de producción usa `pip` directo con versiones pineadas (`Dockerfile:6-20`). Solución: el `Dockerfile` de producción usa `pip install -r requirements.txt` generado por `poetry export -f requirements.txt --without-hashes`. Una sola fuente de verdad (`pyproject.toml`).

### 4.4. Observabilidad

- **Sentry** (frontend + backend): una organización, dos proyectos (`script9-engine-api`, `script9-engine-web`). `release` sincronizado con el SHA de git.
- **Logs estructurados**: structlog en backend, JSON a stdout (Cloud Run → Cloud Logging). Frontend: Sentry + shim `console.error` en producción.
- **`/health` ampliado**: el actual `health.py:11-13` solo devuelve `{status, environment}`. Se reescribe para incluir checks reales a Postgres (`SELECT 1`) y Redis (`PING`). 200 si todo ok, 503 si falla. **Es el gate de Cloud Run**.
- **`/metrics` opcional** (Fase 3): endpoint Prometheus-style con `prometheus_client` (no se añade en v1; Sentry + logs son suficientes).

---

## 5. Arquitectura — cómo encajan las piezas

### 5.1. Modelo de dominio (alto nivel)

```
Usuario (id, firebase_uid, email, nombre, cotizacion_id?, activo, creado_en, actualizado_en)
   │
   ├── 1:1 ──► Cotizacion (id, user_id, app, plan_interno, precio_eur, stripe_price_id, valido_hasta, notas)
   │
   ├── 1:N ──► Lead (id, user_id, app, slug, email, nombre, empresa, mensaje, score, creado_en)
   │
   ├── 1:N ──► Meeting (id, user_id, lead_id, scheduled_at, status, external_id)
   │              -- status ∈ {'proposed', 'confirmed', 'cancelled'}
   │
   └── 1:N ──► ActivityEvent (id, user_id, app, tipo, metadata jsonb, creado_en)
                  -- tipo ∈ {'lead_captured', 'meeting_scheduled', 'meeting_confirmed',
                              'crm_synced', 'subscription_activated', ...}
```

**Reglas de cardinalidad:**

- `app` vive en `Cotizacion`, `Lead` y `ActivityEvent`; **no** en `Usuario` (un usuario puede tener cotizaciones en varias apps).
- `Meeting` se ata a `Lead` (no a `Usuario`): una reunión es sobre un lead concreto.
- `ActivityEvent.metadata` es `JSONB` para extensibilidad sin migraciones.

**Migración desde el modelo actual:**

- `Usuario.cotizacion_id?` (nullable): un usuario recién auto-registrado no tiene cotización aún. Se añade en Alembic.
- `Usuario.plan_suscripcion` (campo actual en `models.py:22`): se **depreca** pero no se borra en v1 (Stripe lo necesita para enrutar features). Se mantiene como espejo de `Cotizacion.plan_interno`.
- `Usuario.stripe_customer_id` (`models.py:23`): se mantiene; se obtiene antes del checkout vía `/api/v1/stripe/customer` que crea el Customer en Stripe si no existe.

### 5.2. Capas del backend

```
app/
  api/v1/             ← Transporte. Solo validan, delegan, devuelven.
    router.py
    health.py         (health real, chequea DB + Redis)
    auth.py           (get_current_user — ya en su sitio)
    usuarios.py       (GET/PATCH /me — se queda)
    cotizaciones.py   (NUEVO: GET /me/cotizacion)
    stripe.py         (POST /checkout, /portal, /customer — refactor §3)
    webhooks.py       (POST /stripe + POST /crm — reescritura §5.4)
    leads.py          (NUEVO Fase 1: POST /leads, GET /leads)
    activity.py       (NUEVO Fase 1: GET /activity/feed, /activity/metric/*)
    invitations.py    (NUEVO Fase 1: POST /invitations, GET /accept)
  schemas/            ← DTOs Pydantic v2 (request/response separados)
    usuario.py
    cotizacion.py     (NUEVO)
    lead.py           (NUEVO)
    activity.py       (NUEVO)
    health.py
    stripe.py
  services/           ← Lógica de negocio. Pura (sin FastAPI), testeable directo.
    usuario_service.py
    cotizacion_service.py  (NUEVO)
    lead_scoring.py        (NUEVO — motor de reglas, sin HTTP)
    meeting_service.py     (NUEVO)
    activity_service.py    (NUEVO)
    crm_client.py          (NUEVO — HubSpot/Cal.com/Resend)
    email_service.py       (NUEVO — SMTP/Resend)
    calendar_service.py    (NUEVO — Cal.com)
  models.py           ← SQLAlchemy ORM (se queda)
  database.py         ← engine + session (se queda)
  config.py           ← Settings (se queda, +Secret Manager en prod)
  main.py             ← FastAPI app + lifespan + middleware
  middleware/         ← request_id, logging, error_handlers (NUEVO carpeta)
```

**Contrato entre capas:** los routers importan `services`, los `services` importan `models` y otros `services`, **nunca** un router importa otro router, **nunca** un `service` importa `fastapi`.

### 5.3. Frontend — capas

```
src/
  pages/              ← Rutas de React Router. Componen, no calculan.
    Login.tsx
    Dashboard.tsx     (Fase 1: reescrito para la métrica viva)
    Planes.tsx        (sustituye a Pricing.tsx, sin números)
    AcceptInvite.tsx  (NUEVO Fase 1)
    Settings.tsx
    Profile.tsx
    NotFound.tsx
  features/           ← Lógica de dominio del frontend (NUEVO, antes no existe)
    activity/
      hooks/useLeadsThisWeek.ts
      hooks/useActivityFeed.ts
      components/ActivityCard.tsx
      components/Sparkline.tsx
    leads/
      hooks/useCreateLead.ts
    auth/             (lo que hoy está en hooks/useAuth.tsx, movido aquí)
  components/
    ui/               (Button, Card, Cube3D, ProtectedRoute — ya están)
    layout/           (AppLayout, Navbar — ya están)
  hooks/              ← Hooks cross-cutting
    useDebounce.ts
  lib/
    api-client.ts     (wrapper sobre @hey-api/client-fetch)
    firebase.ts
    query-client.ts
    zod-schemas.ts    (tipos manuales mientras Hey-API no esté conectado)
    errors.ts
  client/             ← Generado por Hey-API. No se toca a mano.
```

**Reglas de imports:** `pages` → `features` → `components/ui` + `hooks` + `lib`. `features` no importan de `pages`. `components/ui` no importan de `features`. Dirección única.

### 5.4. Contrato API como única fuente de verdad

El paso 9 de la guía (`Script9_Engine.md:467-503`) es el que conecta Hey-API. Hoy está declarado en `package.json:19,31` pero **no operativo** (`src/client/` está vacío). Esto es prioritario en Fase 0.

**Pipeline:**

```
backend/app/* (Python)        pydantic → OpenAPI
       │
       ▼ scripts/generate_openapi.py
       │
   openapi.json
       │
       ▼ openapi-ts
       │
   frontend/src/client/        tipos + funciones + SDK
       │
       ▼ import en lib/api-client.ts
       │
   api.* (en todo el frontend)
```

Cada PR que toque un schema backend regenera el cliente; el `git diff` lo demuestra. CI falla si `src/client/` no está sincronizado con `openapi.json`.

### 5.5. Bug crítico oculto en `webhooks.py`

El `webhooks.py:42, 67, 93` actual llama `asyncio.create_task()` desde métodos **síncronos** de `Script9Callbacks` que reciben la `db` session de FastAPI como argumento. **La session se cierra al retornar la request, antes de que la corrutina en background se ejecute.** Esto deja la corrutina con una sesión cerrada que fallará al hacer `db.commit()`. Es un bug latente que todavía no ha saltado porque la lógica de webhooks no se ha ejercitado en producción.

**Fix:** los callbacks deben ser `async def` (la firma en `script9-billing/webhook.py:31-53` ya lo permite; lo que está mal es el wrapper sync en `Script9Callbacks`). Se reescriben los tres métodos como `async def` y el `process_webhook` (`webhook.py:196-203`) los invoca con `await`. La `db` session sigue siendo la misma, pero ahora se garantiza que se usa dentro de su ciclo de vida.

---

## 6. Seguridad

### 6.1. Autenticación

- **Firebase Google sign-in** (ya en `useAuth.tsx:55-64`). Único proveedor en v1; email/password se difiere.
- **JWT verify en cada request protegido** vía `get_current_user` (`auth.py:42`). `check_revoked=True` activado.
- **Refresh-token rotation:** el cliente llama a `auth.currentUser.getIdToken(true)` antes de cada mutación (`api-client.ts:29`); en la primera carga del dashboard se pre-fetchea con `getIdToken(true)` para evitar 401 por expiración.
- **Cookie de sesión:** Firebase usa `LOCAL` persistence; añadir explícitamente `setPersistence(auth, browserLocalPersistence)` en `lib/firebase.ts`.
- **CSRF:** No aplica (auth vía `Bearer` header, no cookies de sesión). Para integraciones con cookies (subdominios hermanos) se introduce un CSRF token en Fase 5.

### 6.2. Datos

- **HTTPS en todos los entornos de producción.** Cloud Run lo fuerza.
- **Secretos en Secret Manager** (no en `.env` commiteado). El `config.py:36` actual usa `env_file=".env"`; en producción el `lifespan` lee de Secret Manager y sobreescribe el setting. La lectura se hace una sola vez al arrancar.
- **DB at-rest encryption:** Cloud SQL lo activa por defecto. En local, `docker-compose.yml:9-25` no encripta (desarrollo, aceptable).
- **PII:** El modelo `Usuario` tiene `email` y `nombre`. La tabla `Lead` tiene `email`, `nombre`, `empresa`, `mensaje`. Ambos se manejan según GDPR (§6.6).

### 6.3. Facturación

- **Webhook signature verified:** `webhook.py:166-178` ya lo hace con `stripe.Webhook.construct_event`. La firma es la **única** auth del endpoint.
- **Idempotencia outbound:** todas las llamadas a Stripe desde el backend llevan `Idempotency-Key` (UUID generado por request). En `core.py:114` y `core.py:140`.
- **`price_id` nunca del cliente:** ver §3.2.1. El cliente hace `POST /api/v1/stripe/checkout` con `{}`; el backend lee la `Cotizacion` del usuario autenticado y resuelve el `price_id` en el servidor. **Si el cliente intenta enviar `lookup_key` o `price_id`, el schema lo rechaza** (Pydantic 422 con `extra='forbid'`).
- **Stripe webhooks secretos separados** por entorno (test vs live). `STRIPE_WEBHOOK_SECRET` distinto en local/staging/prod.

### 6.4. Superficies de ataque

- **Rate limit:**
  - 100 req/min por IP global (slowapi).
  - 30 req/min por IP en `/api/v1/stripe/*` y `/api/v1/auth/*`.
  - 10 req/min por IP en `/api/v1/leads` (POST público, vector de spam).
- **CSP headers** en producción, vía nginx/Cloud Run:
  ```
  default-src 'self';
  img-src 'self' https: data:;
  script-src 'self' https://www.googletagmanager.com;
  style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
  font-src 'self' https://fonts.gstatic.com data:;
  frame-src https://js.stripe.com https://hooks.stripe.com;
  connect-src 'self' https://firestore.googleapis.com
                    https://identitytoolkit.googleapis.com
                    https://www.googleapis.com https://api.stripe.com
  ```
- **CORS estricto:** `main.py:39-45` permite 5 orígenes; se añade `app.script-9.com` y `tempos.script-9.com`. Se elimina `http://localhost:80` (deprecado).
- **HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy:** se añaden en el nginx de Cloud Run (Fase 3).
- **Validación de inputs:** Pydantic 2 con `extra='forbid'` por defecto en todos los schemas nuevos. `UsuarioUpdate` y `CheckoutRequest` se actualizan para rechazar campos extra.

### 6.5. Observabilidad

- **Sentry captura:** todas las `HTTPException 5xx` y todas las `Exception` no controladas. `traces_sample_rate=0.2` en producción. En frontend, `window.onerror` y `unhandledrejection` van a Sentry.
- **Request ID:** middleware asigna un UUID por request, lo inyecta en cada log (structlog contextvar) y en el header de respuesta `X-Request-Id`. Trazado básico: ante un error, se busca el `request_id` en los logs y se ve toda la traza.
- **Logs sin PII:** structlog con un processor que redacta `email`, `password`, `Authorization` antes de emitir. El raw queda sólo si `environment=local`.

### 6.6. Cumplimiento

- **GDPR:**
  - `GET /api/v1/usuarios/me/export` (Fase 3): devuelve JSON con todos los datos del usuario.
  - `DELETE /api/v1/usuarios/me` (Fase 3): anonimiza `email`, `nombre`, borra `firebase_uid` (cuenta Firebase desactivada desde Admin SDK), mantiene `stripe_customer_id` (obligación fiscal española, 4 años).
  - Cookie banner: no hay cookies de tracking propias; Firebase Analytics requiere consentimiento (Fase 3 si entra en mercados EU más allá de España).
- **Residencia de datos:** Cloud SQL en `europe-west1` (Países Bajos). Cloud Run en la misma región.
- **Privacidad y ToS:** viven en `www.script-9.com/privacidad` y `/terminos` (gestionados por marketing). El frontend enlaza a ellos en el footer y en el formulario de invitación.

### 6.7. Auditoría continua

- `pip-audit` (Fase 0, integrado en CI).
- `pnpm audit` (Fase 0, integrado en CI).
- Escaneo de secretos con `gitleaks` en pre-commit (Fase 0).

---

## 7. Rendimiento y UX

### 7.1. "Navegación rápida y fluida" — cómo se entrega

- **Sin full-page reloads.** React Router 6 con `createBrowserRouter`; todas las rutas son `<Link>` o `navigate()`. `window.location.href` solo para redirecciones externas (Stripe Checkout). Hoy `Pricing.tsx:60` y `Settings.tsx:53` hacen `window.location.href`; se sustituyen por `window.open(url, '_self')` o navegación controlada de TanStack Query.
- **Code-split por ruta.** `React.lazy(() => import('./pages/Dashboard'))` + `<Suspense fallback={<DashboardSkeleton/>}>` en `App.tsx:28-32`. Cada página viaja en su propio chunk. El bundle inicial solo carga `Login`, `AppLayout`, `Navbar` y los providers.
- **Instant feedback con TanStack Query:**
  - `staleTime: 5 * 60 * 1000` (ya en `query-client.ts:6`): no se revalida si la query es < 5 min.
  - `optimistic updates` en mutaciones (PATCH /me, POST /leads): la UI se actualiza antes de que el server responda.
  - `prefetchQuery` en hover de `<Link>`: al pasar el ratón sobre un enlace a `/dashboard`, se pre-carga el query de la métrica.
- **Skeleton loaders para > 200 ms.** El actual `Dashboard.tsx:41-53` ya muestra skeletons; se generaliza al resto de páginas.
- **Perceived speed:**
  - `<link rel="preconnect" href="https://firestore.googleapis.com">` en `index.html`.
  - `<link rel="dns-prefetch" href="https://api.stripe.com">`.
  - `font-display: swap` en Inter y JetBrains Mono.
- **Bundle size cap:** initial JS < 200 KB gzipped. Auditoría con `vite-bundle-visualizer` en CI.

### 7.2. Design tokens (codificados una vez, consumidos en todos lados)

El `index.css:6-156` ya tiene variables CSS (`--bg-primary`, `--accent-emerald`, `--glass-blur`, etc.). **Falta unificar las animaciones** con un set de tokens de duración y easing, consumidos por Framer Motion y CSS:

```ts
// src/lib/animation-tokens.ts (NUEVO)
export const motion = {
  duration: { fast: 150, base: 250, slow: 400 },
  ease: {
    out: [0.16, 1, 0.3, 1],     // expo-out, transiciones que terminan
    in:  [0.7, 0, 0.84, 0],     // expo-in, para salidas
    inOut: [0.65, 0, 0.35, 1],  // expo-in-out, para reorganizaciones
  },
};
```

Estos tokens se usan en TODOS los `<motion.*>` del proyecto. `Button.tsx:58` (whileTap) y `Card.tsx:24-28` (initial/animate) ya están alineados; falta extender al resto.

### 7.3. Coherencia con `script-9.com`

- **Glassmorphism**: `index.css:56-59` ya define `.glass-card`. Se aplica en `Card.tsx:30`, `Pricing.tsx:99-101`, `SuccessPayment.tsx:57`. Se mantiene el `backdrop-filter: blur(12px)` y el borde `rgba(255,255,255,0.1)`.
- **3D cube en login**: `Login.tsx:40` ya importa `Cube3D`. Se mantiene la animación `script9-spin` y `script9-float` de `cube3d.css:38-46`. Si `script-9.com` cambia los keyframes, se sincroniza este CSS.
- **Aura-glow + tech-grid**: `index.css:62-72` define ambas. Se aplica en `Login.tsx:28-29` y se replica en el dashboard en Fase 4.
- **Logo**: `Navbar.tsx:30-34` y `Login.tsx:32-35` usan `.logo-script9` con `.script` blanco, `.nine` emerald, `.engine` slate. Coherente con la marca.
- **Tipografía**: `--font-sans: Inter`, `--font-mono: JetBrains Mono` (`index.css:32-33`). Cargadas vía `<link>` en `index.html` (Fase 0) para evitar FOUT.
- **Micro-interacciones**: `whileTap={{ scale: 0.97 }}` en `Button.tsx:58`; `hover:border-emerald-500/30` en `Card.tsx`; `transition-all duration-300` en `Navbar.tsx:24-27`. Si `script-9.com` introduce un nuevo efecto, se documenta aquí y se propaga.

**Regla de oro:** si script-9.com cambia algo visible, el producto lo refleja en la siguiente release. Un único diseño, dos implementaciones sincronizadas.

---

## 8. Multi-Tenant Platform Play

### 8.1. El hub como plataforma de N apps

`script9-billing` (`backend/packages/script9-billing/`) ya tiene la base: `appName` se inyecta en metadata de Stripe (`core.py:103-106`) y se propaga a los webhooks (`webhook.py:90`). El patrón funciona. Lo que falta es formalizar el contrato que cada app hermana debe cumplir.

### 8.2. El contrato de app hermana

Cualquier nueva app (Tempos hoy, las que vengan mañana) debe implementar:

1. **Lookup keys propios en Stripe.** El equipo de la app crea los `Product` + `Price` en su propio Stripe account (o en el account compartido, según decisión) y les pone lookup_keys con el patrón `{app}_{plan}_{period}` (p. ej. `tempos_starter_monthly`). Sin esto, no se pueden resolver precios.
2. **`appName` único.** Cada app declara un string estable (`'tempos'`, `'crm'`, `'lo-que-venga'`). Ese string viaja en metadata de Stripe, en queries de BD, en URLs de retorno.
3. **URLs de retorno al hub.** `success_url: https://www.script-9.com/pago-exitoso?app={appName}`, `cancel_url: https://www.script-9.com/dashboard`. Centralizado: el cliente siempre vuelve a la web pública de Script-9.
4. **Implementación de `StripeCallbacks`.** Cada app aporta su propia clase con la lógica de activar premium en SU base de datos. Ya documentado en `script9-billing/webhook.py:6-15`.
5. **(Opcional) Subdominio propio.** `{appName}.script-9.com` para una landing dedicada. Cloud Run + Cloud DNS + certificado managed. Esto es Fase 5.

### 8.3. Tempos como piloto

Tempos ya tiene el handoff documentado (`HANDFOFF_Tempos.md:1-141`). El patrón está claro:
- Mantiene su propio backend (Node/Express).
- Consume `script9-billing` como contrato de metadata + lookup_keys.
- Redirige a `script-9.com/pago-exitoso?app=tempos` post-pago.

**Validación del patrón:** cuando Tempos procese su primer pago real con el flujo nuevo (precio invisible, cotización por app), el patrón está probado. El resto de apps se incorporan copiando el `HANDFOFF_Tempos.md` y parametrizando.

### 8.4. Checklist de incorporación de nueva app

```
□ Crear proyecto Firebase (o usar el compartido).
□ Crear cuenta Stripe (o sub-account).
□ Crear Products + Prices con lookup_keys {app}_{plan}_{period}.
□ Crear tabla cotizaciones con app={appName}.
□ Crear migración Alembic (añade índice en cotizaciones.user_id + app).
□ Crear Script9Callbacks para la app (activar premium en su DB).
□ Crear success_url con ?app={appName}.
□ Crear landing en {appName}.script-9.com (opcional).
□ Smoke test end-to-end con Stripe test mode.
□ Habilitar la app en el admin de cotizaciones.
```

---

## 9. Roadmap — fases

### Fase 0 — Cierre de deuda técnica (los 7 pasos pendientes)

- **Goal:** dejar el scaffold cerrado, los tests funcionando, las herramientas conectadas.
- **Scope:**
  - Paso 7 (Observabilidad): structlog + Sentry + `/health` real con checks a Postgres/Redis.
  - Paso 9 (Hey-API): script `pnpm gen` operativo, `src/client/` poblado, `api-client.ts` reducido a wrapper.
  - Paso 11 (Frontend tests): vitest + RTL + Playwright configurados; suite mínima (Button, useAuth, useUsuario, flujo E2E de auth).
  - Paso 13 (Alembic): `alembic init`, primera migración autogenerada para `usuarios`, pipeline de upgrade/rollback.
  - Paso 14 (CI/CD): GitHub Actions con jobs de calidad (ruff, mypy, pnpm lint, tsc), tests (backend + frontend), audit (pip-audit, pnpm audit).
  - Paso 15 (Cloud Run): `cloudbuild.yaml`, Secret Manager, primer deploy.
  - **Bugfixes**: `UsuarioUpdate.email` → `EmailStr` (`schemas/usuario.py:30`); defaults en `Usuario.__init__` (`models.py:21,22,29`); `webhooks.py:42,67,93` reescritura a `async def` (§5.5).
- **Out of scope:** nuevas features; refactor de pricing; producto.
- **Outcome:** CI verde; `pnpm gen` regenera el cliente en cada cambio de schema; `alembic upgrade head` deja la BD en estado conocido; `/health` devuelve 200 con checks reales; los 2 `xfail` pasan.
- **Estimate:** 1.5 – 2 semanas a tiempo completo.
- **Dependencies:** ninguna (se puede empezar hoy).

### Fase 1 — Producto MVP: el journey del lead

- **Goal:** matar el "próximamente". El usuario ve datos reales desde el primer login.
- **Scope:**
  - Backend: `Cotizacion` model + migración; `Leads` model + endpoint público; `Meetings` model; `ActivityEvent` model; `invitations` (create + accept); refactor `stripe.py` con `Cotizacion.stripe_price_id`; replace `lookup_key` del request (§3.2.1).
  - Frontend: `Dashboard` reescrito con `LeadsThisWeek` + sparkline + lista de eventos; `Planes.tsx` (sustituye a `Pricing.tsx`); `AcceptInvite.tsx`.
  - Integraciones: Cal.com o Calendly (webhook de entrada para `meeting.confirmed`); Resend (email de invitación + scheduling); HubSpot (webhook de salida idempotente).
- **Out of scope:** más métricas; admin UI para crear cotizaciones (Antonio lo hace a mano vía DB en v1); facturación anual; cancelaciones anticipadas; tests de carga.
- **Outcome:** un cliente real (Antonio crea su `Cotizacion`, manda invite) puede: aceptar invitación → ver dashboard vacío con CTA → activar cuenta → pagar precio oculto → ver `Leads esta semana: 0` (estado vacío honesto) → compartir enlace de formulario → recibir un lead → ver `Leads esta semana: 1` con sparkline `[0,0,0,0,0,0,1]`.
- **Estimate:** 3 – 4 semanas.
- **Dependencies:** Fase 0 completa.

### Fase 2 — Multi-tenant + sister apps hardening

- **Goal:** el patrón de plataforma funciona con N apps, no solo `script9`.
- **Scope:**
  - Tests E2E que prueban el flujo completo en Tempos (con Stripe test mode).
  - Middleware de scope: cada `Lead`, `Meeting`, `ActivityEvent` se filtra por `app` además de por `user_id`.
  - Admin endpoint (CLI o HTTP protegido por `app_metadata.admin=true` en Firebase) para crear/editar `Cotizacion`.
  - Subdominio `{app}.script-9.com` para Tempos, con su propia landing.
  - `Cotizacion.valido_hasta`: aviso automático al cliente 7 días antes de expirar.
- **Out of scope:** onboarding self-service de apps; portal de developers; marketplace de apps.
- **Outcome:** Tempos procesa su primer pago real con precio invisible; una nueva app puede incorporarse en 1 día siguiendo el checklist §8.4.
- **Estimate:** 2 – 3 semanas.
- **Dependencies:** Fase 1 completa; Tempos adaptado.

### Fase 3 — Seguridad, compliance, observabilidad madura

- **Goal:** el producto está listo para clientes enterprise.
- **Scope:**
  - GDPR: `GET /me/export`, `DELETE /me` con anonimización; cookie banner para Firebase Analytics.
  - HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy en nginx de Cloud Run.
  - `/metrics` Prometheus-style.
  - Alertas en Sentry: error rate > 1 %, latency p95 > 500 ms, webhook failures > 5/h.
  - Pentest interno (self-review con OWASP top 10).
- **Out of scope:** SOC2; ISO 27001; HIPAA.
- **Outcome:** el producto pasa un self-auditoría de seguridad sin findings críticos; los datos de un cliente se pueden exportar y borrar en 1 click.
- **Estimate:** 1.5 – 2 semanas.
- **Dependencies:** Fase 2 completa; al menos 3 clientes reales en producción.

### Fase 4 — Performance + UX polish (pixel-perfect con script-9.com)

- **Goal:** la app se siente **idéntica** a la web pública en fluidez y estética.
- **Scope:**
  - Auditoría de animaciones: todas las transiciones siguen los tokens §7.2; 0 inconsistencias con `script-9.com`.
  - Code-split agresivo: cada ruta < 100 KB; initial < 150 KB.
  - LCP < 1.5 s en P75, INP < 200 ms en P75 (medidos con Lighthouse y web-vitals).
  - Code review visual: `Login`, `Dashboard`, `Planes`, `Settings`, `Profile` revisados uno a uno contra `script-9.com` para ajustar espaciados, tamaños de fuente, radios de borde, intensidades de glow.
  - Optimistic updates en todas las mutaciones del usuario.
- **Out of scope:** A/B testing; rediseños; i18n.
- **Outcome:** un usuario que navega entre `script-9.com` y `app.script-9.com` no nota discontinuidad visual ni de fluidez.
- **Estimate:** 1.5 – 2 semanas.
- **Dependencies:** Fase 3 completa; sitio `script-9.com` en estado estable (no en rediseño).

### Fase 5 — Escalar, features avanzadas, siguiente app

- **Goal:** el hub soporta crecimiento sin re-platforming; arranca la segunda app hermana.
- **Scope:**
  - ARQ + Redis para trabajos en background (scoring pesado, syncs CRM masivos, envío de emails en lote).
  - i18n (`react-i18next` con namespaces por `app`).
  - Roles: `admin`, `user`; invitaciones a un workspace compartido (Fase 5+).
  - CSRF tokens para integraciones con cookies.
  - Segunda app hermana (lo que Antonio decida) incorporada siguiendo el checklist §8.4.
  - Plan gratuito limitado (con métricas de uso) — opcional, sólo si Antonio decide.
- **Out of scope:** marketplace público; API pública para terceros; multi-currency.
- **Outcome:** el equipo de Antonio incorpora una nueva app en 1 semana; la plataforma soporta 5+ apps sin degradación de performance.
- **Estimate:** 4 – 6 semanas.
- **Dependencies:** Fases 1-4 completas; métricas de producción que justifiquen la siguiente app.

---

## 10. Definition of Done — por fase

### Fase 0
- [ ] Los 15 pasos de la guía están completos (los 7 pendientes + retoques de los hechos).
- [ ] `pytest --cov=app` ≥ 80 % in-scope, 0 fallos, 0 xfail.
- [ ] `pnpm test --coverage` ≥ 75 % in-scope, 0 fallos.
- [ ] `pnpm gen` regenera `src/client/` sin diff cuando el schema no cambia.
- [ ] `alembic upgrade head` desde una BD vacía deja el schema al día.
- [ ] `docker-compose up` arranca los 4 servicios; `/health` devuelve 200 con `database: ok`, `redis: ok`.
- [ ] `pip-audit` y `pnpm audit` reportan 0 vulnerabilidades críticas/altas.
- [ ] CI en GitHub Actions: jobs `backend-quality`, `backend-tests`, `frontend-quality`, `frontend-tests`, `build-check` pasan en cada PR.
- [ ] `cloudbuild.yaml` desplegable; Secret Manager configurado; primer deploy a Cloud Run exitoso.
- [ ] Los 2 `xfail` conocidos están cerrados (los tests pasan) y la suite no tiene nuevos xfail.

### Fase 1
- [ ] Un usuario real, creado vía invite, puede recorrer el journey completo.
- [ ] El dashboard muestra `Leads esta semana` con sparkline real.
- [ ] La página `/planes` no muestra precios.
- [ ] El endpoint `POST /api/v1/stripe/checkout` rechaza requests con `lookup_key` o `price_id` en el body.
- [ ] El webhook de Cal.com actualiza `Meeting.status = confirmed` y emite `ActivityEvent`.
- [ ] Tests E2E (Playwright) cubren el flujo `auth → invite → checkout → dashboard → métrica`.
- [ ] Cobertura de tests ≥ 80 % backend, ≥ 75 % frontend in-scope.

### Fase 2
- [ ] Tempos procesa un pago real end-to-end con precio invisible.
- [ ] El middleware de scope filtra correctamente: un usuario autenticado en `app='tempos'` no ve `Lead` con `app='script9'`.
- [ ] El admin endpoint para crear `Cotizacion` está protegido por `app_metadata.admin` y tiene tests.
- [ ] `app.script-9.com` y `tempos.script-9.com` resuelven a sus landings correspondientes.
- [ ] Una nueva app se incorpora en < 1 día siguiendo el checklist §8.4.

### Fase 3
- [ ] Self-auditoría OWASP top 10: 0 hallazgos críticos, 0 altos.
- [ ] GDPR: `GET /me/export` devuelve un JSON válido; `DELETE /me` anonimiza los datos verificables.
- [ ] CSP, HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy presentes en producción (verificable con `securityheaders.com`).
- [ ] Alertas de Sentry configuradas y probadas (forzar un error 500 → llega alerta).
- [ ] `/metrics` devuelve series Prometheus válidas.

### Fase 4
- [ ] Lighthouse P75: LCP < 1.5 s, INP < 200 ms, CLS < 0.1.
- [ ] Bundle inicial < 150 KB gzipped (verificado con `vite-bundle-visualizer`).
- [ ] Code review visual firmado: Login, Dashboard, Planes, Settings, Profile coherentes con `script-9.com`.
- [ ] 0 `window.location.href` fuera de redirecciones a Stripe (todo es navegación SPA).
- [ ] Todas las mutaciones tienen `onMutate` (optimistic update) o feedback explícito.

### Fase 5
- [ ] ARQ + Redis procesando trabajos en background; latencia de requests de usuario no afectada.
- [ ] i18n funcional: cambiar `lang` en un test E2E refleja strings traducidos.
- [ ] Roles `admin` y `user` operativos; un admin puede invitar a un workspace compartido.
- [ ] Segunda app hermana incorporada y procesando pagos.
- [ ] Plataforma soporta 5+ apps en BD sin degradación de queries (índices correctos en `app`, `user_id`, `creado_en`).

---

## 11. Riesgos y mitigaciones

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|--------|--------------|---------|------------|
| 1 | **Bandwidth de un solo perfil.** Antonio es la única persona que escribe código. Si se enferma o prioriza clientes, el roadmap se paraliza. | Alta | Alto | Priorizar **duramente**: Fase 0 → Fase 1 → Fase 2; lo demás se difiere. Contratar freelance para Fase 3+ (seguridad) si el bandwidth lo exige. Documentar cada decisión para que la incorporación de otro dev sea de 1 semana, no de 1 mes. |
| 2 | **El funnel de precio invisible convierte menos que el de precio público.** Algunos clientes potenciales se asustan al no ver precio. | Media | Alto | Medir: instrumentar `script-9.com/hablemos` con un evento `lead_intent` en Firebase Analytics. A/B test del CTA en Fase 4 (privado vs "saber más"). Si la conversión cae > 30 %, revisar la propuesta; si no, mantener. |
| 3 | **El `bug` de los webhooks (`webhooks.py:42,67,93`) salta en producción antes de Fase 0.** | Media | Alto | El bug está en `xfail` lógico (no se ha ejercitado). El primer webhook real en producción (pago de un cliente) lo expondrá. **Acción inmediata**: reescribir los callbacks como `async def` en una PR de Fase 0. Prioridad #1 dentro de Fase 0. |
| 4 | **Cloud Run escala a cero y el primer request de un cliente tarda 5-10 s en cold start.** | Media | Medio | `min-instances: 1` en producción; budget de cold-start aceptable para SaaS B2B. Monitorizar con Sentry (transacción de boot). Si la latencia P95 > 2 s, evaluar Cloud Run con `cpu=always-allocated`. |
| 5 | **Stripe cambia la API o deprecá `automatic_tax`.** | Baja | Alto | `script9-billing` está aislado como paquete; un bump de versión arregla el caller. Tests E2E con Stripe test mode cubren el happy path. Monitorizar Stripe changelog. |
| 6 | **Firebase Auth tiene una caída.** | Baja | Alto | Degradación elegante: si Firebase está caído, el `/health` devuelve 503, Cloud Run no enruta tráfico. La app muestra "Servicio no disponible" sin crash. Sentry alerta a Antonio en minutos. Plan B (largo plazo): añadir Auth0 o Supabase Auth como fallback — Fase 5+. |
| 7 | **El cliente edita algo en `script-9.com` y rompe la coherencia visual.** | Media | Medio | Convención: cualquier cambio visual en `script-9.com` se documenta en un `BRAND_CHANGELOG.md` (en la raíz del repo) y dispara una tarea de sincronización en el frontend del producto. |
| 8 | **Acreción de features de cliente que no estaban en el scope.** | Alta | Medio | Defensa explícita: este documento (sección 2.3) lista lo que NO está en v1. Cualquier feature nueva se discute contra esa lista. El principio "una arquitectura, un diseño, sin fragmentación" es la línea roja. |

---

## 12. Decision log — preguntas que solo Antonio puede responder

Estas decisiones no se pueden tomar sin la perspectiva de negocio. Las respuestas dan forma a fases futuras, no a Fase 0/1.

1. **¿El SaaS es invite-only o permite self-service signup?**
   *Estado actual*: el plan es invite-only (lo que la nueva arquitectura soporta naturalmente). Pero un formulario "Sign up" en `script-9.com` con un campo "URL de tu empresa" que cualifique automáticamente podría reducir el trabajo de Antonio. **Recomendación**: invite-only en v1; self-service en Fase 5 si la demanda lo justifica.

2. **¿Qué CRM se integra primero?**
   *Opciones*: HubSpot (el más común en B2B español), Pipedrive (más simple, mejor para consultoras pequeñas), Notion (un "CRM" improvisado, el más flexible). **Recomendación**: HubSpot por su API madura y por el target enterprise que Antonio busca. Se puede cambiar en Fase 5.

3. **¿Pago anual prepagado o solo mensual?**
   *Estado actual*: solo mensual en `script-9-billing` (no hay soporte de `interval=year`). **Recomendación**: añadir anual prepagado con descuento (p. ej. 2 meses gratis) en Fase 2; aumenta LTV y reduce churn. Pero requiere negociar con Antonio cómo afecta al flujo de cotización.

4. **¿"Script9 Engine" o simplemente "Script9"?**
   *Estado actual*: el producto se llama "Script9 Engine"; la web pública es "script-9.com". Hay fricción cognitiva. **Recomendación**: la web pública en `script-9.com` se mantiene; el producto en `app.script-9.com` se llama "Script9" a secas (sin "Engine") para evitar la doble palabra. La landing `engine.script-9.com` desaparece. Decisión de marketing, no de ingeniería.

5. **¿Dónde se hospeda? Cloud Run, Railway, Vercel + Render, Fly.io?**
   *Estado actual*: la guía apunta a Cloud Run (`Script9_Engine.md:727-773`). **Recomendación**: Cloud Run por (a) escala a cero, (b) Secret Manager nativo, (c) Cloud SQL en la misma región. El coste para el tamaño actual es < 50 €/mes. Si en Fase 5 el tráfico crece, se evalúa GKE.

6. **¿Qué proveedor de email transaccional?**
   *Opciones*: Resend (moderno, DX excelente, 3.000 emails/mes gratis), SendGrid (consolidado, caro), Amazon SES (barato, fricción alta). **Recomendación**: Resend por su DX y por la coherencia con un stack moderno. Plan free cubre los primeros 3.000 emails/mes.

7. **¿Calendly o Cal.com (self-hosted)?**
   *Opciones*: Cal.com self-hosted (gratis, control total, se integra con el stack), Calendly (más simple, 12 €/mes, mejor UX para el cliente final). **Recomendación**: Cal.com self-hosted en Fase 1 (gratis, datos en EU); Calendly es la red de seguridad si Cal.com se complica.

8. **¿Qué segunda app hermana se construye?**
   *Estado actual*: Tempos es la única. La siguiente app es una decisión de producto. Candidatos naturales: CRM ligero (extensión del journey de leads), o un portal de reporting para clientes. **Recomendación**: esperar a tener 3-5 clientes reales en producción antes de decidir; los datos de uso guiarán la prioridad.

---

## Apéndice — Diagnóstico de inconsistencias detectadas durante el análisis

| Archivo:línea | Inconsistencia | Acción |
|---|---|---|
| `docker-compose.yml:63-65` | `STRIPE_*_PRICE_ID` declaradas pero no se usan (el flujo nuevo resuelve desde `Cotizacion`). | Eliminar en Fase 0. |
| `docker-compose.yml:59` y `app/api/v1/stripe.py:36` | El `app_name` viene de lados distintos. | Estandarizar: lo resuelve el servidor desde `Cotizacion.app` o `Usuario.app`. |
| `backend/Dockerfile` vs `backend/Dockerfile.dev` | Una usa `pip` con versiones pineadas; la otra usa Poetry. | Único: `poetry export` → `requirements.txt` → `pip install -r`. |
| `webhooks.py:42,67,93` | `asyncio.create_task` desde método sync con `db` session que se cerrará antes de que la task corra. | Reescribir como `async def`; fix prioritario en Fase 0. |
| `models.py:21,22,29` | Defaults de `mapped_column` se aplican en flush, no en `__init__`. | Usar `init=True` o un `__init__` explícito. Cierra uno de los `xfail`. |
| `schemas/usuario.py:30` | `email: str | None` en vez de `EmailStr`. | Cambiar a `EmailStr`. Cierra el otro `xfail`. |
| `scripts/generate_openapi.py` existe pero no se invoca en CI ni en `pnpm gen`. | — | Cablear `pnpm gen` que encadene Python + openapi-ts. |
| `frontend/src/client/` vacío a pesar de tener `@hey-api/openapi-ts` instalado. | — | Activar el pipeline en Fase 0. |
| `frontend/src/lib/api-client.ts` (132 líneas) reinventa un cliente HTTP que Hey-API ya provee. | — | Sustituir por wrapper de `@hey-api/client-fetch`. |
| `docker-compose.yml:69` monta `firebase-credentials.json` desde la raíz del repo. Si el archivo no está versionado (debería no estarlo), el contenedor falla. | — | Documentar en README; en producción usar Secret Manager. |
| `tests/conftest.py:39-58` usa SQLite en memoria con `StaticPool`. Los tests E2E con PostgreSQL nunca se ejecutan. | — | Fase 3: añadir suite con Postgres en CI (job con `services: postgres:16`). |
| `app/main.py:21-22` hace `Base.metadata.create_all` en el `lifespan`. Esto crea las tablas al arrancar. Si se introduce Alembic, hay doble responsabilidad. | — | Eliminar `create_all` en Fase 0 cuando Alembic esté operativo. |

---

*Fin de la estrategia. Próximo paso: Antonio valida el decision log (§12) y desbloquea el arranque de Fase 0.*
