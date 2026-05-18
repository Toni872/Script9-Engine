import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/lib/api-client';
import { useUsuario } from '@/hooks/useUsuario';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { getErrorMessage } from '@/lib/errors';
import { Check, CreditCard } from '@phosphor-icons/react';

const statusConfig: Record<string, { label: string; className: string; dot: string }> = {
  active: { label: 'Activo', className: 'text-emerald-400', dot: 'bg-emerald-500' },
  past_due: { label: 'Vencido', className: 'text-amber-400', dot: 'bg-amber-500' },
  canceled: { label: 'Cancelado', className: 'text-red-400', dot: 'bg-red-500' },
  incomplete: { label: 'Incompleto', className: 'text-amber-400', dot: 'bg-amber-500' },
  trialing: { label: 'Prueba', className: 'text-blue-400', dot: 'bg-blue-500' },
  unpaid: { label: 'Impago', className: 'text-red-400', dot: 'bg-red-500' },
};

function StatusDot({ status }: { status: string | null }) {
  const config = status ? statusConfig[status] : null;
  if (!config) {
    return <span className="text-sm text-slate-500">—</span>;
  }
  return (
    <span className={`flex items-center gap-1.5 text-sm ${config.className}`}>
      <span className={`h-2 w-2 rounded-full ${config.dot}`} />
      {config.label}
    </span>
  );
}

export function Settings() {
  const { data: usuario } = useUsuario();
  const queryClient = useQueryClient();

  const [nombre, setNombre] = useState(usuario?.nombre ?? '');
  const [email, setEmail] = useState(usuario?.email ?? '');
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const mutation = useMutation({
    mutationFn: (data: { nombre?: string; email?: string }) =>
      api.updateMe(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['usuario', 'me'] });
      setSuccessMsg('Perfil actualizado correctamente');
      setTimeout(() => setSuccessMsg(null), 3000);
    },
  });

  const portalMutation = useMutation({
    mutationFn: () => api.createPortal(),
    onSuccess: (data) => {
      window.location.href = data.url;
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSuccessMsg(null);
    mutation.mutate({ nombre, email });
  };

  return (
    <div className="mx-auto max-w-2xl space-y-8 px-6 py-8">
      <div>
        <h1 className="text-2xl font-bold">Ajustes</h1>
        <p className="mt-1 text-sm text-slate-400">
          Gestiona tu perfil y preferencias
        </p>
      </div>

      {/* Profile Settings */}
      <Card title="Perfil" description="Actualiza tu información personal">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Nombre */}
          <div>
            <label htmlFor="nombre" className="mb-1.5 block text-sm font-medium text-slate-300">
              Nombre
            </label>
            <input
              id="nombre"
              type="text"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              className="w-full rounded-lg border border-slate-700/80 bg-slate-900/60 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:border-emerald-500/50 focus:outline-none focus:ring-1 focus:ring-emerald-500/30"
              placeholder="Tu nombre"
            />
          </div>

          {/* Email */}
          <div>
            <label htmlFor="email" className="mb-1.5 block text-sm font-medium text-slate-300">
              Email
            </label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-700/80 bg-slate-900/60 px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 transition-colors focus:border-emerald-500/50 focus:outline-none focus:ring-1 focus:ring-emerald-500/30"
              placeholder="tu@email.com"
            />
          </div>

          {/* Success message */}
          {successMsg && (
            <div className="flex items-center gap-2 rounded-lg bg-emerald-500/10 px-4 py-3 text-sm text-emerald-400">
              <Check size={16} weight="bold" />
              {successMsg}
            </div>
          )}

          {/* Error message */}
          {mutation.isError && (
            <div className="rounded-lg bg-red-500/10 px-4 py-3 text-sm text-red-400">
              {getErrorMessage(mutation.error)}
            </div>
          )}

          {/* Submit */}
          <div className="flex justify-end">
            <Button
              type="submit"
              variant="primary"
              isLoading={mutation.isPending}
              disabled={mutation.isPending}
            >
              Guardar cambios
            </Button>
          </div>
        </form>
      </Card>

      {/* Plan Info */}
      <Card title="Suscripción" description="Tu plan actual y detalles de facturación">
        <div className="space-y-3">
          <div className="flex justify-between">
            <span className="text-sm text-slate-400">Plan</span>
            <span className="text-sm font-medium capitalize text-slate-200">
              {usuario?.plan_suscripcion ?? 'trial'}
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-sm text-slate-400">Estado</span>
            <StatusDot status={usuario?.subscription_status ?? null} />
          </div>

          {usuario?.current_period_end && usuario?.subscription_status === 'active' && (
            <div className="flex justify-between">
              <span className="text-sm text-slate-400">Próximo pago</span>
              <span className="text-sm text-slate-300">
                {new Date(usuario.current_period_end).toLocaleDateString('es-AR', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </span>
            </div>
          )}

          {usuario?.stripe_customer_id && (
            <div className="border-t border-slate-700/50 pt-4">
              <Button
                variant="secondary"
                size="sm"
                leftIcon={<CreditCard size={16} />}
                isLoading={portalMutation.isPending}
                disabled={portalMutation.isPending}
                onClick={() => portalMutation.mutate()}
              >
                Gestionar suscripción
              </Button>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
