import { useUsuario } from '@/hooks/useUsuario';
import { useAuth } from '@/hooks/useAuth';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import {
  User,
  EnvelopeSimple,
  CurrencyDollar,
  GearSix,
  SignOut,
} from '@phosphor-icons/react';
import { useNavigate, Link } from 'react-router-dom';

const planColors: Record<string, string> = {
  trial: 'bg-slate-700 text-slate-300',
  starter: 'bg-blue-900/50 text-blue-300',
  professional: 'bg-emerald-900/50 text-emerald-300',
  enterprise: 'bg-amber-900/50 text-amber-300',
};

const statusConfig: Record<string, { label: string; className: string; dot: string }> = {
  active: { label: 'Activo', className: 'text-emerald-400', dot: 'bg-emerald-500' },
  past_due: { label: 'Vencido', className: 'text-amber-400', dot: 'bg-amber-500' },
  canceled: { label: 'Cancelado', className: 'text-red-400', dot: 'bg-red-500' },
  incomplete: { label: 'Incompleto', className: 'text-amber-400', dot: 'bg-amber-500' },
  trialing: { label: 'Prueba', className: 'text-blue-400', dot: 'bg-blue-500' },
  unpaid: { label: 'Impago', className: 'text-red-400', dot: 'bg-red-500' },
};

export function Dashboard() {
  const { user, logout } = useAuth();
  const { data: usuario, isLoading, isError, error } = useUsuario();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  // Loading skeleton
  if (isLoading) {
    return (
      <div className="mx-auto max-w-7xl space-y-6 px-6 py-8">
        <div className="h-8 w-64 animate-pulse rounded-lg bg-slate-800" />
        <div className="h-4 w-48 animate-pulse rounded-lg bg-slate-800" />
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 animate-pulse rounded-2xl bg-slate-800/50" />
          ))}
        </div>
      </div>
    );
  }

  // Error state
  if (isError) {
    return (
      <div className="mx-auto max-w-7xl px-6 py-8">
        <Card title="Error" className="text-red-400">
          <p>{error instanceof Error ? error.message : 'Error al cargar perfil'}</p>
        </Card>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-7xl space-y-8 px-6 py-8">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold">
            Hola, <span className="text-emerald-400">{user?.displayName ?? 'Usuario'}</span>
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Panel de control — Script9 Engine
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<GearSix size={16} />}
            onClick={() => navigate('/settings')}
          >
            Ajustes
          </Button>
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<SignOut size={16} />}
            onClick={handleLogout}
          >
            Salir
          </Button>
        </div>
      </div>

      {/* Profile Card */}
      <Card title="Perfil" className="max-w-xl">
        <div className="flex items-center gap-4">
          {user?.photoURL && (
            <img
              src={user.photoURL}
              alt="Avatar"
              className="h-14 w-14 rounded-full ring-2 ring-emerald-500/30"
            />
          )}
          <div className="space-y-1">
            <p className="font-medium text-slate-200">{usuario?.nombre ?? user?.displayName}</p>
            <p className="flex items-center gap-1.5 text-sm text-slate-400">
              <EnvelopeSimple size={14} />
              {usuario?.email ?? user?.email}
            </p>
            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`inline-block rounded-full px-3 py-0.5 text-xs font-medium capitalize ${
                  planColors[usuario?.plan_suscripcion ?? 'trial']
                }`}
              >
                {usuario?.plan_suscripcion ?? 'trial'}
              </span>

              {usuario?.subscription_status && (
                <span
                  className={`flex items-center gap-1 text-xs ${
                    statusConfig[usuario.subscription_status]?.className ?? 'text-slate-400'
                  }`}
                >
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${
                      statusConfig[usuario.subscription_status]?.dot ?? 'bg-slate-500'
                    }`}
                  />
                  {statusConfig[usuario.subscription_status]?.label ?? usuario.subscription_status}
                </span>
              )}

              {usuario?.current_period_end && usuario?.subscription_status === 'active' && (
                <span className="text-xs text-slate-500">
                  · Vence{' '}
                  {new Date(usuario.current_period_end).toLocaleDateString('es-AR', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                  })}
                </span>
              )}

              {(!usuario?.stripe_customer_id || usuario?.plan_suscripcion === 'trial') && (
                <Link
                  to="/pricing"
                  className="text-xs font-medium text-emerald-400 transition-colors hover:text-emerald-300"
                >
                  Mejorar plan &rarr;
                </Link>
              )}
            </div>
          </div>
        </div>
      </Card>

      {/* Stats Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        <Card glow className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-emerald-500/10">
            <CurrencyDollar size={24} className="text-emerald-400" />
          </div>
          <div>
            <p className="text-sm text-slate-400">Plan actual</p>
            <p className="text-lg font-semibold capitalize text-slate-100">
              {usuario?.plan_suscripcion ?? 'Cargando...'}
            </p>
          </div>
        </Card>

        <Card className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-blue-500/10">
            <User size={24} className="text-blue-400" />
          </div>
          <div>
            <p className="text-sm text-slate-400">Usuario ID</p>
            <p className="font-mono text-xs text-slate-500">#{usuario?.id ?? '—'}</p>
          </div>
        </Card>

        <Card className="flex items-center gap-4 sm:col-span-2 lg:col-span-1">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-slate-700/50">
            <span className="font-mono text-xs text-slate-400">API</span>
          </div>
          <div>
            <p className="text-sm text-slate-400">Estado</p>
            <p className="flex items-center gap-1.5 text-sm font-medium text-emerald-400">
              <span className="h-2 w-2 rounded-full bg-emerald-500" />
              Conexión activa
            </p>
          </div>
        </Card>
      </div>

      {/* Recent Activity / Placeholder */}
      <Card title="Actividad reciente" description="Tus últimas acciones en la plataforma">
        <p className="py-8 text-center text-sm text-slate-500">
          No hay actividad reciente — próximamente con métricas y fichajes.
        </p>
      </Card>
    </div>
  );
}
