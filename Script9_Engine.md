# Guía Maestra de Prompts — SaaS Full Stack Production-Ready

## FastAPI + React + Firebase + PostgreSQL + Redis | Enterprise Edition v2

**Cómo usar esta guía:** Los prompts están numerados y son **estrictamente secuenciales**. No avances al siguiente hasta que el agente confirme que el paso anterior está completo, los archivos existen y, donde aplique, los tests pasan. Cada prompt es autónomo: incluye el contexto necesario para que el agente entienda qué hace y por qué.

---

## Mapa de Progreso

| Paso | Área                  | Descripción                                             |
|------|-----------------------|---------------------------------------------------------|
| 1    | Monorepo              | Estructura base y archivos de configuración             |
| 2    | Backend Core          | FastAPI + SQLModel + conexión async a DB                |
| 3    | Configuración y Calidad | Ruff, Mypy, variables de entorno validadas            |
| 4    | Seguridad Backend     | Firebase Auth, rate limiting, manejo global de errores  |
| 5    | Stripe Webhooks       | Firma de eventos y actualización de suscripciones       |
| 6    | Testing Backend       | pytest, pytest-asyncio, cobertura mínima                |
| 7    | Observabilidad        | Structlog, Sentry, health checks                        |
| 8    | Frontend Base         | Vite + React + TypeScript + Tailwind                    |
| 9    | Cliente API           | Hey-API SDK + TanStack Query + interceptores auth       |
| 10   | Frontend UI           | Dark Glassmorphism, componentes, Framer Motion          |
| 11   | Testing Frontend      | Vitest + Testing Library + Playwright E2E               |
| 12   | Infraestructura       | Docker Compose local + Dockerfile multi-stage           |
| 13   | Migraciones           | Alembic configurado y primera migración                 |
| 14   | CI/CD                 | GitHub Actions pipeline completo                        |
| 15   | Producción            | Secret Manager, configuración Cloud Run                 |

---

## Arquitectura de referencia

Antes de empezar, comparte este diagrama con el agente en el Paso 1 para que entienda el sistema completo:

```
Cliente React (Vite + TS)
  └─ TanStack Query + Hey-API SDK
       └─ Firebase Auth SDK (inyecta JWT en cada request)
             └─ HTTP → FastAPI (Puerto 8081)
                   ├─ Rate Limiter (slowapi + Redis)
                   ├─ Firebase Auth Middleware (verifica JWT + auto-registro)
                   ├─ Pydantic v2 Schemas
                   └─ SQLModel Service Layer
                         ├─ asyncpg → PostgreSQL
                         └─ Redis (caché + colas ARQ)
```

---

## PASO 1 — Estructura del Monorepo y Archivos de Configuración

```
Quiero iniciar un proyecto SaaS profesional con arquitectura monorepo.
El stack es: FastAPI (Python) en el backend y React + Vite + TypeScript en el frontend.

Crea la siguiente estructura de directorios vacía (sin código todavía, solo los archivos
de configuración y dependencias):

ESTRUCTURA:
mi-proyecto-saas/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas/
│   │   │   └── __init__.py
│   │   └── api/
│   │       ├── __init__.py
│   │       └── v1/
│   │           ├── __init__.py
│   │           ├── router.py
│   │           ├── auth.py
│   │           └── usuarios.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── test_auth.py
│   │       ├── test_usuarios.py
│   │       └── test_webhooks.py
│   ├── scripts/
│   │   └── generate_openapi.py
│   ├── pyproject.toml
│   ├── poetry.lock       ← se generará con poetry install
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── lib/
    │   │   ├── firebase.ts
    │   │   ├── api-client.ts
    │   │   ├── zod-schemas.ts
    │   │   └── query-client.ts
    │   ├── hooks/
    │   │   ├── useAuth.ts
    │   │   └── useUsuario.ts
    │   ├── components/
    │   │   └── ui/
    │   │       ├── Button.tsx
    │   │       └── Card.tsx
    │   ├── pages/
    │   │   ├── Login.tsx
    │   │   └── Dashboard.tsx
    │   ├── App.tsx
    │   └── index.css
    ├── tests/
    │   ├── unit/
    │   │   ├── hooks/
    │   │   │   ├── useAuth.test.ts
    │   │   │   └── useUsuario.test.ts
    │   │   └── components/
    │   │       └── Button.test.tsx
    │   └── e2e/
    │       └── auth.spec.ts
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    ├── tailwind.config.ts
    └── .env.example

Para backend/pyproject.toml, usa Poetry y añade estas dependencias de producción:
- fastapi[standard] ^0.115
- sqlmodel ^0.0.21
- asyncpg ^0.30
- alembic ^1.14
- redis[hiredis] ^5.2
- firebase-admin ^6.6
- stripe ^11.4
- slowapi ^0.1.9
- structlog ^24.4
- sentry-sdk[fastapi] ^2.19
- pydantic-settings ^2.7
- aiosqlite ^0.20   ← solo para tests locales

Dev dependencies:
- pytest ^8.3
- pytest-asyncio ^0.24
- pytest-cov ^6.0
- httpx ^0.28
- factory-boy ^3.3
- ruff ^0.8
- mypy ^1.13

Para frontend/package.json usa pnpm y añade:
- react, react-dom ^18
- react-router-dom ^6
- @tanstack/react-query ^5
- firebase ^11
- framer-motion ^11
- zod ^3
- @hey-api/client-fetch (cliente generado)

Dev: vite, typescript, tailwindcss, @vitejs/plugin-react, vitest,
@testing-library/react, @playwright/test, eslint

Muéstrame el contenido completo de pyproject.toml y package.json.
```

---

## PASO 2 — Núcleo de Datos: Base de Datos Asíncrona y Modelos

```
Trabajamos en la carpeta /backend. El stack es FastAPI + SQLModel + asyncpg + PostgreSQL.

Implementa los siguientes archivos con su lógica completa:

1. app/config.py
   Usa pydantic-settings para crear una clase Settings que cargue y valide estas
   variables de entorno. Si alguna falta al iniciar, la app debe detenerse con un
   error claro:
   - DATABASE_URL (str) — debe empezar con postgresql+asyncpg:// en producción
   - REDIS_URL (str) — URL de conexión a Redis
   - FIREBASE_CREDENTIALS_JSON (str) — JSON completo de las credenciales de Firebase Admin
   - STRIPE_SECRET_KEY (str)
   - STRIPE_WEBHOOK_SECRET (str)
   - ENVIRONMENT (str, valores permitidos: "local", "staging", "production", default "local")
   - SENTRY_DSN (str, opcional)
   - DOCS_ENABLED (bool, default True en local, False en producción)
   Implementa la lógica para que DOCS_ENABLED sea automáticamente False si ENVIRONMENT != "local"
   aunque el usuario no la configure.
   Crea una instancia singleton 'settings' al final del archivo.

2. app/database.py
   Configura el motor asíncrono de SQLAlchemy con asyncpg.
   Pool de conexiones: pool_size=20, max_overflow=10, pool_recycle=3600,
   pool_pre_ping=True (detecta conexiones muertas antes de usarlas).
   Crea una función generadora asíncrona 'get_session' que use AsyncSession
   como context manager para inyectar en las rutas vía Depends().
   Si DATABASE_URL empieza con 'sqlite', usa aiosqlite en su lugar (para tests locales).

3. app/models.py
   Define el modelo SQLModel 'Usuario' con estos campos:
   - id: int, primary key, autoincremental
   - firebase_uid: str, único, indexado (búsqueda frecuente)
   - email: EmailStr, único
   - nombre: str
   - plan_suscripcion: str, default "trial"
   - stripe_customer_id: Optional[str], nullable
   - activo: bool, default True
   - creado_en: datetime, default utcnow
   - actualizado_en: datetime, default utcnow, se actualiza automáticamente

4. app/main.py
   Configura la aplicación FastAPI:
   - Puerto 8081 (obligatorio, documéntalo en un comentario)
   - Título, versión y descripción del proyecto
   - Middleware CORS: origins configurables desde settings, permite credentials,
     métodos y headers estándar
   - Deshabilita /docs, /redoc y /openapi.json si settings.DOCS_ENABLED es False
   - Lifespan que al iniciar: inicializa Firebase Admin SDK con las credenciales de settings,
     inicializa Sentry si hay DSN configurado, y crea las tablas si ENVIRONMENT == "local"
   - Incluye el router principal de /api/v1
   - Incluye un endpoint GET /health que devuelva {"status": "ok", "environment": ...}
     sin autenticación, útil para health checks de Cloud Run

Muéstrame el contenido completo de los 4 archivos.
```

---

## PASO 3 — Calidad de Código: Configuración de Ruff y Mypy

```
Trabajamos en /backend. Ya tenemos pyproject.toml con las secciones [tool.ruff]
y [tool.mypy] configuradas.

Ahora necesito que:

1. Ejecutes 'ruff check app/' y corrijas todos los errores que encuentre en los archivos
   creados en el paso anterior (config.py, database.py, models.py, main.py).
   Si hay errores que requieren decisión manual, explícamelos.

2. Ejecutes 'mypy app/' y corrijas todos los errores de tipos.
   Presta especial atención a:
   - Tipos de retorno en todas las funciones
   - Optional[T] vs T | None (usa el estilo moderno de Python 3.12)
   - Tipos en los campos de SQLModel

3. Crea un archivo .pre-commit-config.yaml en la raíz de /backend que ejecute
   automáticamente ruff check y ruff format en cada commit.

4. Documenta en un comentario al inicio de cada archivo de app/ qué hace ese módulo
   (una línea, estilo docstring de módulo).

Al terminar, muéstrame la salida limpia de 'ruff check app/' y 'mypy app/'
indicando cero errores.
```

---

## PASO 4 — Seguridad Backend: Auth, Rate Limiting y Manejo de Errores

```
Continuamos en /backend. Implementa los siguientes módulos de seguridad:

1. app/api/v1/auth.py — Dependencia de autenticación Firebase
   Implementa una función asíncrona 'get_current_user' para usar con Depends():
   - Extrae el token del header 'Authorization: Bearer <token>'
   - Verifica el token contra Firebase usando firebase_admin.auth.verify_id_token()
     con check_revoked=True para detectar tokens revocados (cuentas baneadas, etc.)
   - Busca al usuario en la base de datos por firebase_uid
   - Si el token es válido pero el usuario NO existe en la base de datos, lo crea
     automáticamente (auto-registro) con los datos del token de Firebase
   - Si el token es inválido o expirado, lanza HTTPException 401 con mensaje claro
   - Si el usuario existe pero activo=False, lanza HTTPException 403 (cuenta suspendida)
   - Loguea con structlog el uid del usuario autenticado en cada request exitoso

2. app/api/v1/usuarios.py — Endpoints de usuario autenticados
   Implementa dos endpoints protegidos con Depends(get_current_user):
   - GET /me — devuelve el perfil del usuario autenticado
   - PATCH /me — actualiza nombre y/o email del usuario autenticado
   Usa esquemas de Pydantic v2 separados para request y response (no expongas campos internos)

3. app/services/cache_service.py — Capa de caché con Redis
   Implementa funciones asíncronas para:
   - get_usuario_cached(firebase_uid) → Usuario | None
   - set_usuario_cached(usuario: Usuario, ttl=300)
   - invalidate_usuario_cache(firebase_uid)
   Usa redis.asyncio y serializa/deserializa con model_dump_json / model_validate_json
   Haz que get_current_user use esta caché antes de ir a PostgreSQL

4. app/main.py — Rate Limiting y manejo global de errores
   Añade a main.py:
   - Slowapi como middleware de rate limiting: 100 requests/minuto por IP en todas las rutas,
     30 requests/minuto específicamente en endpoints de auth
   - Exception handler para RequestValidationError que devuelva JSON normalizado:
     {"detail": [...errors...], "code": "VALIDATION_ERROR"}
   - Exception handler para HTTPException que devuelva JSON normalizado:
     {"detail": message, "code": "HTTP_ERROR", "status": status_code}
   - Exception handler para Exception genérica que loguee con structlog el traceback completo
     y devuelva {"detail": "Error interno del servidor", "code": "INTERNAL_ERROR"}
     sin exponer detalles en producción

Muéstrame el contenido completo de cada archivo.
```

---

## PASO 5 — Stripe Webhooks Seguros

```
Continuamos en /backend. Implementa app/api/v1/webhooks.py:

El endpoint POST /webhooks/stripe debe:
1. Leer el body de la petición como bytes crudos (no JSON parseado, esto es crítico
   para que la verificación de firma funcione)
2. Extraer la cabecera 'Stripe-Signature'
3. Verificar la firma usando stripe.Webhook.construct_event() con el
   STRIPE_WEBHOOK_SECRET de settings. Si la firma falla, devuelve 400 con mensaje "Firma inválida"
4. Manejar estos eventos de forma asíncrona:
   - 'customer.subscription.created' → actualiza plan_suscripcion del usuario al plan
     del nuevo subscription
   - 'customer.subscription.updated' → actualiza plan_suscripcion con el nuevo plan
   - 'customer.subscription.deleted' → establece plan_suscripcion a "trial"
   - 'invoice.payment_failed' → loguea el evento con structlog y podría notificar al usuario
     (deja un TODO comentado para el sistema de notificaciones)
   - Cualquier otro evento → responde 200 con {"received": true} sin hacer nada
     (Stripe reintenta si no devuelves 2xx, así que siempre devuelve 2xx si el evento
     es válido aunque no lo proceses)
5. Busca al usuario por stripe_customer_id en la base de datos
6. Si no encuentra al usuario, loguea un warning pero devuelve 200 igualmente
   (puede ser un customer de una etapa de test, no debe romper el webhook)
7. Loguea con structlog cada evento recibido con: tipo de evento, customer_id, timestamp

Importante: Este endpoint NO debe estar protegido por get_current_user porque las
peticiones vienen de Stripe, no de usuarios autenticados. Su protección es la firma.

Muéstrame el archivo completo.
```

---

## PASO 6 — Testing del Backend

```
Implementa la suite completa de tests en /backend/tests/:

1. tests/conftest.py
   Configura los fixtures de pytest:
   - 'engine': crea un motor de SQLite en memoria (no PostgreSQL) para que los tests
     sean rápidos y no necesiten infraestructura externa
   - 'db_session': crea las tablas antes del test y las destruye después (limpieza total)
   - 'client': AsyncClient de httpx apuntando a la app de FastAPI con override de la
     dependencia 'get_session' para usar la sesión de test
   - 'mock_firebase': fixture que parchea firebase_admin.auth.verify_id_token para
     devolver un token válido falso sin necesitar Firebase real
   - 'usuario_factory': factory-boy para crear usuarios de prueba en la base de datos
   - 'mock_redis': fixture que parchea el cliente de Redis para evitar necesitar Redis real

2. tests/api/test_auth.py
   Tests para el flujo de autenticación:
   - Test: request sin header Authorization devuelve 401
   - Test: request con token malformado devuelve 401
   - Test: request con token válido de Firebase crea el usuario en BD si no existe (auto-registro)
   - Test: request con token válido de usuario existente devuelve el usuario sin duplicar
   - Test: usuario con activo=False devuelve 403

3. tests/api/test_usuarios.py
   Tests para los endpoints de usuario:
   - Test: GET /me devuelve el perfil del usuario autenticado
   - Test: PATCH /me actualiza nombre correctamente
   - Test: PATCH /me con email inválido devuelve 422 (validación Pydantic)

4. tests/api/test_webhooks.py
   Tests para los webhooks de Stripe:
   - Test: POST /webhooks/stripe sin cabecera Stripe-Signature devuelve 400
   - Test: POST /webhooks/stripe con firma inválida devuelve 400
   - Test: POST /webhooks/stripe con evento customer.subscription.updated actualiza el plan

El objetivo de cobertura mínimo es 80%. Muéstrame el contenido de cada archivo
y al terminar ejecuta 'pytest --cov=app --cov-report=term-missing' y comparte la salida.
```

---

## PASO 7 — Observabilidad: Logging Estructurado y Health Checks

```
Implementa la capa de observabilidad en /backend:

1. app/services/logging_service.py
   Configura structlog para que:
   - En ENVIRONMENT="local": los logs sean en formato legible por humanos (consola coloreada)
   - En ENVIRONMENT="staging" o "production": los logs sean en formato JSON puro
     (para que Cloud Run los indexe en Google Cloud Logging)
   - Cada log debe incluir automáticamente: timestamp ISO 8601, nivel, módulo, función
   - Crea una función 'get_logger(name)' que devuelva un logger de structlog listo para usar
   - Documenta cómo usarlo en cualquier módulo: logger = get_logger(__name__)

2. Actualiza app/main.py para inicializar structlog al arrancar usando la función anterior

3. app/api/v1/health.py
   Implementa un endpoint GET /health más completo que el básico del paso 2:
   - Verifica la conectividad con PostgreSQL haciendo una query simple
   - Verifica la conectividad con Redis con un ping
   - Devuelve el estado de cada componente: {"status": "ok|degraded|error", "checks": {...}}
   - Si algún check falla, devuelve HTTP 503 (Service Unavailable) en lugar de 200
   - Este endpoint NO requiere autenticación

4. Integración con Sentry
   En app/main.py (lifespan), cuando SENTRY_DSN está configurado, inicializa Sentry con:
   - traces_sample_rate=0.2 en producción (20% de traces, controla el costo)
   - traces_sample_rate=1.0 en local y staging (100% para depuración)
   - Integración FastAPI automática de Sentry

5. Añade un middleware de request logging que loguee con structlog cada request:
   método, path, status_code y tiempo de respuesta en milisegundos.
   Excluye el endpoint /health de este log para no saturar los logs con health checks.

Muéstrame el contenido completo de los archivos modificados y nuevos.
```

---

## PASO 8 — Frontend Base: Vite + TypeScript + Tailwind + Firebase

```
Trabajamos en /frontend. Configura la base del frontend:

1. src/lib/firebase.ts
   Inicializa el SDK de Firebase Client JS.
   Las credenciales deben venir de variables de entorno de Vite (VITE_FIREBASE_*).
   Exporta: 'app' (la app de Firebase), 'auth' (Firebase Auth)
   Configura la persistencia de sesión como LOCAL (el usuario no pierde sesión al cerrar el tab)

2. src/lib/api-client.ts
   Configura el cliente de Hey-API para que:
   - Apunte a la URL base del backend (configurable por variable de entorno VITE_API_URL,
     default 'http://localhost:8081')
   - Antes de cada request, obtenga el ID token del usuario autenticado de Firebase
     usando auth.currentUser.getIdToken(true) — el parámetro 'true' fuerza el refresh
     si el token está cerca de expirar
   - Inyecte el token en el header 'Authorization: Bearer <token>'
   - Si el usuario no está autenticado (no hay currentUser), lanza un error específico
     que el componente pueda capturar para redirigir al login

3. src/lib/zod-schemas.ts
   Define los siguientes schemas de Zod para validar respuestas de la API:
   - UsuarioSchema: id, firebase_uid, email, nombre, plan_suscripcion, activo, creado_en
   - UsuarioUpdateSchema: nombre (opcional), email (opcional, validado como email)
   - ApiErrorSchema: detail, code
   Exporta los tipos TypeScript inferidos de cada schema usando z.infer<>

4. src/App.tsx
   Configura el router de la aplicación con react-router-dom v6:
   - Ruta pública: /login → página de Login
   - Rutas protegidas (requieren auth): /dashboard, /settings, /profile
   - Ruta catch-all: redirige a /dashboard si está autenticado, a /login si no
   - Componente 'ProtectedRoute' que verifica si hay usuario en Firebase Auth
     y redirige a /login si no hay sesión
   - Envuelve toda la app en QueryClientProvider (TanStack Query) con configuración:
     staleTime: 5 minutos, retry: 2 intentos, refetchOnWindowFocus: false

5. Crea un archivo .env.example en /frontend con las variables de entorno necesarias:
   VITE_API_URL, VITE_FIREBASE_API_KEY, VITE_FIREBASE_AUTH_DOMAIN,
   VITE_FIREBASE_PROJECT_ID, VITE_FIREBASE_APP_ID, VITE_SENTRY_DSN

Muéstrame el contenido completo de cada archivo.
```

---

## PASO 9 — Cliente API Tipado: Hey-API + TanStack Query

```
Continuamos en /frontend. Conecta el backend con el frontend de forma completamente tipada:

1. Script de generación del schema OpenAPI
   En /backend/scripts/generate_openapi.py, escribe el script que exporte el schema
   de FastAPI a /backend/openapi.json. Este script debe importar la app y usar
   get_openapi() para generar el JSON.

   En frontend/package.json, en el script 'generate-client', añade el comando
   que primero ejecute el script de Python y luego ejecute 'openapi-ts'
   para regenerar src/client/ automáticamente.

2. src/hooks/useUsuario.ts
   Hook personalizado que usa TanStack Query para:
   - Obtener el perfil del usuario autenticado (GET /api/v1/usuarios/me)
   - Usar el cliente generado por Hey-API en src/client/
   - Validar la respuesta contra UsuarioSchema de Zod antes de retornar
   - Si la validación de Zod falla, loguea el error en Sentry y lanza un error descriptivo
   - Exporta también 'useUpdateUsuario': mutation para actualizar el perfil (PATCH /me)
     que invalida automáticamente la caché de useUsuario al completarse con éxito

3. src/hooks/useAuth.ts
   Hook que encapsula todo el estado de autenticación:
   - Escucha los cambios de sesión de Firebase con onAuthStateChanged
   - Exporta: user (el usuario de Firebase), isLoading, isAuthenticated
   - Incluye funciones: loginWithGoogle(), loginWithEmail(), logout()
   - logout() debe limpiar la caché de TanStack Query además de cerrar sesión en Firebase

4. src/lib/query-client.ts
   Configura y exporta el QueryClient de TanStack Query con:
   - onError global: si el error es 401, redirige al login y limpia la caché
   - onError global: cualquier error inesperado lo reporta a Sentry
   - Configuración de staleTime, retry y refetchOnWindowFocus

Muéstrame el contenido completo de cada archivo.
```

---

## PASO 10 — UI Premium: Dark Glassmorphism + Componentes Base

```
Continuamos en /frontend. Implementa la capa visual:

1. src/index.css
   Configura el sistema de diseño completo:
   - Variables CSS globales: colores del tema dark (fondo #0a0a0c, superficies, bordes),
     colores de acento (gradiente primary), radios de borde, sombras
   - Clase utilitaria '.glass-card': fondo semitransparente oscuro, backdrop-filter blur(12px),
     borde sutil semitransparente, border-radius consistente con el sistema
   - Clase utilitaria '.gradient-text': texto con gradiente del color de acento
   - Animaciones CSS base para micro-interacciones (no las que requieren Framer Motion)
   - Scrollbar personalizado oscuro para webkit

2. src/components/ui/Button.tsx
   Componente Button con estas variantes:
   - primary: gradiente del color de acento
   - secondary: estilo glass-card
   - ghost: sin fondo, solo texto
   - danger: rojo para acciones destructivas
   Cada variante tiene estado hover con transición suave (Framer Motion motion.button)
   Props: variant, size (sm/md/lg), isLoading (muestra spinner), disabled, onClick, children
   Completamente tipado con TypeScript.

3. src/components/ui/Card.tsx
   Componente Card con estilo glass-card aplicado.
   Props: title (opcional), description (opcional), children, className
   Animación de entrada con Framer Motion (fade + slide up)

4. src/pages/Login.tsx
   Página de login completa:
   - Diseño centrado con fondo oscuro y partículas o gradiente animado
   - Logo y nombre del producto
   - Botón "Continuar con Google" (usa loginWithGoogle del hook useAuth)
   - Estado de carga mientras procesa el login
   - Si hay error, muestra un mensaje descriptivo (no el error técnico de Firebase)
   - Redirige automáticamente a /dashboard si ya hay sesión activa

5. src/pages/Dashboard.tsx
   Dashboard básico pero funcional:
   - Muestra "Hola, {nombre}" con los datos reales del usuario desde useUsuario
   - Muestra el plan de suscripción actual con un badge
   - Estado de skeleton loading mientras carga (no spinners)
   - Estado de error si el fetch falla, con botón de reintentar

Muéstrame el contenido completo de cada archivo.
```

---

## PASO 11 — Testing del Frontend

```
Implementa la suite de tests en /frontend:

1. tests/unit/hooks/useAuth.test.ts
   Tests para el hook de autenticación:
   - Mock de Firebase Auth (onAuthStateChanged, signInWithPopup, signOut)
   - Test: isAuthenticated es false cuando no hay usuario
   - Test: isAuthenticated es true cuando Firebase devuelve un usuario
   - Test: logout limpia la caché de TanStack Query y cierra sesión

2. tests/unit/hooks/useUsuario.test.ts
   - Mock del cliente de API generado por Hey-API
   - Test: devuelve el perfil del usuario cuando la API responde correctamente
   - Test: lanza error si la respuesta de la API no pasa la validación de Zod
   - Test: useUpdateUsuario invalida la caché tras una actualización exitosa

3. tests/unit/components/Button.test.tsx
   - Test: renderiza el texto de los children
   - Test: ejecuta onClick cuando se hace click
   - Test: muestra spinner cuando isLoading es true
   - Test: no ejecuta onClick cuando disabled es true

4. tests/e2e/auth.spec.ts (Playwright)
   Flujo E2E de autenticación:
   - Test: un usuario no autenticado que visita /dashboard es redirigido a /login
   - Test: la página de login muestra el botón de Google
   Nota: para el test de login completo, usa el emulador de Firebase Auth en local
   o mockea las respuestas de red con Playwright network intercept.

5. Configura el script 'test' en package.json para ejecutar:
   'vitest run --coverage' y documenta el threshold mínimo de 75% de cobertura.

Muéstrame el contenido completo de cada archivo y la configuración de coverage.
```

---

## PASO 12 — Infraestructura Local y Docker

```
Crea la infraestructura de contenedores del proyecto:

1. docker-compose.yml en la raíz del monorepo
   Servicios:
   - db: postgres:16-alpine, puerto 5432, volumen persistente, healthcheck con pg_isready
   - redis: redis:7-alpine, puerto 6379, con persistencia AOF activada
   - api: construye desde ./backend/Dockerfile.dev, puerto 8081,
     monta el código fuente como volumen para hot-reload con uvicorn --reload,
     depends_on con condition: service_healthy para db y redis,
     variables de entorno cargadas desde ./backend/.env (que no existe en git)
   Incluye un perfil opcional 'tools' con pgAdmin para gestión visual de la base de datos.

2. backend/Dockerfile.dev
   Imagen de desarrollo ligera para usar con docker-compose:
   - Basada en python:3.12-slim
   - Instala dependencias de Poetry sin crear virtualenv (usa el sistema)
   - Copia el código y arranca con: uvicorn app.main:app --host 0.0.0.0 --port 8081 --reload

3. backend/Dockerfile (producción — multi-stage)
   Stage 'builder':
   - python:3.12-slim
   - Instala solo las dependencias de producción de Poetry en /opt/venv
   - Usa --no-cache-dir y --no-root para maximizar el caché de capas de Docker
   Stage 'production':
   - python:3.12-slim limpio (sin Poetry, sin herramientas de build)
   - Copia solo /opt/venv del stage builder y el código fuente
   - Crea un usuario no-root 'appuser' y ejecuta como ese usuario (seguridad)
   - EXPOSE 8081
   - CMD con gunicorn usando UvicornWorker, workers = 2*CPU+1, timeout 120,
     puerto 8081, con --preload para detectar errores de inicio antes de servir tráfico

4. .dockerignore en /backend:
   Excluye: .git, __pycache__, .pytest_cache, .mypy_cache, .ruff_cache,
   tests/, *.pyc, .env, openapi.json

5. backend/.env.example con todas las variables necesarias y valores de ejemplo
   para desarrollo local con docker-compose.

Muéstrame el contenido completo de cada archivo.
```

---

## PASO 13 — Migraciones con Alembic

```
Configura Alembic para gestión de migraciones en /backend:

1. Inicializa Alembic en /backend con 'alembic init migrations'

2. Edita migrations/env.py para que:
   - Importe los modelos de SQLModel (app/models.py) para que Alembic los detecte
   - Use la DATABASE_URL de settings (app/config.py) como URL de conexión
   - Soporte migraciones asíncronas con asyncpg usando run_sync y AsyncEngine
   - Configure target_metadata = SQLModel.metadata para detección automática de cambios

3. Edita alembic.ini para que la variable 'sqlalchemy.url' esté vacía
   (la URL se inyecta desde settings en env.py, no desde el ini)

4. Genera la primera migración automática con:
   alembic revision --autogenerate -m "create_usuarios_table"

5. Muéstrame cómo verificar la migración generada en migrations/versions/ y
   el comando para aplicarla: alembic upgrade head

6. Documenta en un comentario en env.py el flujo de trabajo estándar de migraciones:
   - Modificar modelos en app/models.py
   - Generar migración: alembic revision --autogenerate -m "descripcion"
   - Revisar el archivo generado manualmente antes de aplicar
   - Aplicar: alembic upgrade head
   - Revertir si hay problema: alembic downgrade -1

Muéstrame el contenido completo de migrations/env.py y el diff de alembic.ini.
```

---

## PASO 14 — CI/CD: GitHub Actions

```
Crea el pipeline de CI/CD en .github/workflows/ci.yml:

El pipeline debe ejecutarse en cada push a cualquier rama y en cada Pull Request a main.
Usa ubuntu-latest y Python 3.12.

Jobs (pueden ejecutarse en paralelo donde sea posible):

1. Job 'backend-quality':
   - Instala dependencias con Poetry (usa cache de pip para velocidad)
   - Ejecuta: ruff check app/ (falla si hay errores de linting)
   - Ejecuta: ruff format --check app/ (falla si el código no está formateado)
   - Ejecuta: mypy app/ (falla si hay errores de tipos)

2. Job 'backend-tests':
   Servicios Docker necesarios para los tests:
   - postgres:16-alpine en puerto 5432 con healthcheck
   - redis:7-alpine en puerto 6379 con healthcheck
   Variables de entorno de test (DATABASE_URL con sqlite en memoria para rapidez,
   REDIS_URL apuntando al servicio de redis del job, credenciales de Firebase
   como secretos de GitHub)
   Pasos:
   - Instala dependencias con Poetry
   - Ejecuta pytest con cobertura
   - Sube el reporte de cobertura a Codecov (usa el action oficial de Codecov)
   - Falla si la cobertura cae por debajo del 80%

3. Job 'frontend-quality':
   - Instala dependencias con pnpm (usa cache)
   - Ejecuta: pnpm lint (ESLint)
   - Ejecuta: pnpm tsc --noEmit (verifica tipos sin compilar)

4. Job 'frontend-tests':
   - Instala dependencias con pnpm
   - Ejecuta: pnpm test --coverage
   - Falla si la cobertura cae por debajo del 75%

5. Job 'build-check' (solo en PR a main):
   Depende de que todos los jobs anteriores pasen.
   - Construye la imagen Docker de producción del backend
   - Verifica que pnpm build del frontend termine sin errores
   Este job confirma que el código es desplegable antes de mergear.

Incluye en el YAML los permisos mínimos necesarios para cada job (principio de
mínimo privilegio). Muéstrame el contenido completo del archivo.
```

---

## PASO 15 — Configuración de Producción: Secret Manager y Cloud Run

```
Configura el entorno de producción para Google Cloud Run:

1. Actualiza app/config.py para que en ENVIRONMENT="production":
   - Las variables sensibles (DATABASE_URL, FIREBASE_CREDENTIALS_JSON, etc.)
     se lean desde Google Secret Manager en lugar de variables de entorno directas
   - Usa el SDK de google-cloud-secret-manager para acceder a los secretos
   - El nombre del proyecto de GCP debe venir de una variable de entorno
     GCP_PROJECT_ID (esta sí puede ser una variable normal, no un secreto)
   - Si GCP_PROJECT_ID no está configurado en producción, la app falla con error claro
   - En local y staging, mantén el comportamiento actual (variables de entorno)

2. Añade google-cloud-secret-manager a las dependencias de producción en pyproject.toml

3. Crea un archivo cloudbuild.yaml en la raíz del repositorio con los pasos para
   Cloud Build que:
   - Construye la imagen Docker multi-stage del backend
   - La sube a Artifact Registry con el tag del commit de git
   - Despliega a Cloud Run en la región configurada con:
     - Mínimo 0 instancias, máximo 10 (escala a cero cuando no hay tráfico)
     - 512MB de memoria, 1 CPU
     - Timeout de 300 segundos
     - Variables de entorno no sensibles configuradas directamente
     - Secretos montados desde Secret Manager como variables de entorno

4. Documenta el comando gcloud para el primer despliegue manual y la
   configuración de los secretos en Secret Manager:
   - Cómo crear cada secreto: gcloud secrets create ...
   - Cómo dar permisos al Service Account de Cloud Run para leer los secretos

5. Crea un archivo DEPLOYMENT.md en la raíz con el checklist completo de
   pasos a seguir para el primer despliegue a producción, en orden:
   - Configuración de GCP (proyecto, APIs habilitadas, Service Accounts)
   - Configuración de Firebase (proyecto, Auth providers, reglas)
   - Creación de secretos en Secret Manager
   - Primera migración de base de datos
   - Despliegue del backend a Cloud Run
   - Despliegue del frontend a Firebase Hosting
   - Verificación del health check
   - Configuración del webhook de Stripe apuntando al dominio de Cloud Run

Muéstrame el contenido completo de los archivos modificados y nuevos.
```

---

## Checklist de Validación Final

Una vez completados todos los pasos, pide al agente que valide:

```
Valida que el proyecto está completo y listo para producción ejecutando:

BACKEND:
1. poetry run ruff check app/ → 0 errores
2. poetry run mypy app/ → 0 errores
3. poetry run pytest --cov=app → cobertura ≥ 80%
4. docker build -f backend/Dockerfile -t saas-backend . → build exitoso

FRONTEND:
5. pnpm lint → 0 errores
6. pnpm tsc --noEmit → 0 errores de tipos
7. pnpm test --coverage → cobertura > 75%
8. pnpm build → build exitoso sin warnings críticos

INTEGRACIÓN:
9. docker-compose up → todos los servicios arrancan y pasan healthchecks
10. curl http://localhost:8081/health → {"status": "ok", ...}

Muéstrame la salida de cada comando. Si alguno falla, corrígelo antes de reportar
el proyecto como completo.
```

---

## Notas para el Agente

Incluye estas instrucciones al inicio de tu sesión con el agente:

```
Eres un ingeniero de software senior especializado en Python y TypeScript.
Trabajamos en un proyecto SaaS profesional con arquitectura monorepo.

REGLAS:
- Sigue los pasos en orden estricto. No avances sin confirmación.
- Cada archivo debe estar completo y funcional, no fragmentos.
- Usa siempre tipos explícitos (Python 3.12+ y TypeScript strict).
- Si detectas una decisión de arquitectura que mejoraría el sistema, propónla
  antes de implementar, no después.
- Cuando termines un paso, lista los archivos creados/modificados y confirma
  que están listos para el siguiente paso.
```
