# Script9 Engine — Railway Deployment Guide

## Prerequisites

Before deploying, ensure you have:

- [Railway](https://railway.app) account (Hobby tier minimum for free tier deployments)
- Stripe test API keys from [Stripe Dashboard](https://dashboard.stripe.com/test/apikeys)
- Stripe webhook signing secret (`whsec_...`)
- Firebase service account JSON file ([instructions](https://firebase.google.com/docs/admin/setup#initialize_the_sdk))

## One-Time Setup

### 1. Install Railway CLI

```bash
npm install -g @railway/cli
```

### 2. Login and link project

```bash
railway login
railway init
# Select "Empty project" if starting fresh
railway link <project-id>
```

### 3. Add backing services

From the Railway dashboard or CLI:

```bash
# Add PostgreSQL
railway add postgres

# Add Redis
railway add redis
```

This creates `POSTGRES_URL` and `REDIS_URL` environment variables automatically.

### 4. Configure environment variables

Set the following in the Railway dashboard under **Variables**:

| Variable | Description | Example |
|----------|-------------|---------|
| `ENVIRONMENT` | `production` | `production` |
| `DATABASE_URL` | Set automatically by Railway Postgres plugin | (auto) |
| `REDIS_URL` | Set automatically by Railway Redis plugin | (auto) |
| `STRIPE_SECRET_KEY` | Stripe test secret key | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook signing secret | `whsec_...` |
| `SENTRY_DSN` | Sentry DSN (optional) | `https://...@sentry.io/...` |
| `FIREBASE_CREDENTIALS_PATH` | Path inside container | `/app/firebase-credentials.json` |
| `SCRIPT9_URL` | Your frontend URL | `https://your-app.railway.app` |

### 5. Upload Firebase credentials

```bash
railway volumes upload firebase-credentials.json /app/firebase-credentials.json
```

Or set the JSON content directly as a Railway secret variable named `FIREBASE_CREDENTIALS_JSON`.

## Deploy Command

```bash
railway up
```

This builds the backend using NIXPACKS (auto-detects Python/FastAPI) and deploys with the `railway.toml` configuration.

## Smoke Test

After deployment:

```bash
curl https://<your-railway-domain>/api/v1/health
```

Expected response:

```json
{"status": "ok", "environment": "production"}
```

## Alembic Migrations

Run database migrations after deployment:

```bash
railway run --service api -- alembic upgrade head
```

**Note**: The initial migration (`0001_initial.py`) creates the `usuarios` table. If you have existing data, back it up first.

To check current migration status:

```bash
railway run --service api -- alembic current
```

To downgrade if needed:

```bash
railway run --service api -- alembic downgrade base
```

## Rollback Procedure

### Option 1: Railway Dashboard
1. Navigate to your deployment in the Railway dashboard
2. Click **Redeploy** and select a previous successful deployment

### Option 2: CLI
```bash
# List recent deployments
railway deployments

# Rollback to a specific deployment
railway rollback <deployment-id>
```

## FAQ

### Q: Cold starts are slow on hobby tier
**A**: This is expected behavior on Railway's free Hobby tier. Cold starts can take 10-30 seconds due to container provisioning. To minimize impact:
- Enable Railway Pro for faster cold starts
- Set `MINIMIZE_COLD_STARTS=1` if available
- Consider keeping a ping/cron job to keep the service warm

### Q: How do I check logs?
```bash
railway logs
# Or for a specific deployment
railway logs --deployment <deployment-id>
```

### Q: How do I connect to the database?
```bash
railway run --service api -- psql $DATABASE_URL
```

### Q: Can I deploy from a PR preview?
Yes — set up a separate Railway environment for staging and promote to production after review.

## Environment Reference

See `backend/.env.example` for all supported environment variables.