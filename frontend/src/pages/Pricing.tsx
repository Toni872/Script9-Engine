import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { api } from '@/lib/api-client';
import { useUsuario } from '@/hooks/useUsuario';
import { Button } from '@/components/ui/Button';
import { Check, ArrowRight, Star } from '@phosphor-icons/react';

const PLANS = [
  {
    id: 'starter',
    name: 'Starter',
    price: 29,
    features: [
      '5 automatizaciones activas',
      '100 ejecuciones/mes',
      'Soporte por email',
      'Panel de control básico',
    ],
    priceId: import.meta.env.VITE_STRIPE_STARTER_PRICE_ID ?? '',
  },
  {
    id: 'professional',
    name: 'Professional',
    price: 99,
    features: [
      '25 automatizaciones activas',
      '1,000 ejecuciones/mes',
      'Soporte prioritario',
      'Panel de control avanzado',
      'Integraciones premium',
      'Historial 90 días',
    ],
    priceId: import.meta.env.VITE_STRIPE_PROFESSIONAL_PRICE_ID ?? '',
    popular: true,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: null,
    features: [
      'Automatizaciones ilimitadas',
      'Ejecuciones ilimitadas',
      'Soporte dedicado 24/7',
      'On-premise disponible',
      'SLA garantizado',
      'Auditoría y compliance',
    ],
    priceId: import.meta.env.VITE_STRIPE_ENTERPRISE_PRICE_ID ?? '',
  },
];

export function Pricing() {
  const { data: usuario } = useUsuario();
  const navigate = useNavigate();
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const checkoutMutation = useMutation({
    mutationFn: (priceId: string) => api.createCheckout(priceId),
    onSuccess: (data) => {
      window.location.href = data.url;
    },
    onError: (err: Error) => {
      setErrorMsg(err.message ?? 'Error al crear la sesión de pago');
    },
  });

  const isSubscribed =
    usuario?.stripe_customer_id != null &&
    usuario?.subscription_status === 'active';

  const isTrial = usuario?.plan_suscripcion === 'trial';

  return (
    <div className="mx-auto max-w-7xl px-6 py-12">
      <div className="mb-12 text-center">
        <h1 className="text-3xl font-bold">Planes y Precios</h1>
        <p className="mt-2 text-slate-400">
          Elegí el plan que mejor se adapte a tus necesidades
        </p>
      </div>

      {errorMsg && (
        <div className="mx-auto mb-8 max-w-xl rounded-lg bg-red-500/10 px-4 py-3 text-center text-sm text-red-400">
          {errorMsg}
        </div>
      )}

      <div className="mx-auto grid max-w-5xl gap-8 md:grid-cols-3">
        {PLANS.map((plan) => {
          const isCurrentPlan = usuario?.plan_suscripcion === plan.id;
          const isLoading =
            checkoutMutation.isPending &&
            checkoutMutation.variables === plan.priceId;

          return (
            <div
              key={plan.id}
              className={`glass-card relative flex flex-col ${
                plan.popular ? 'ring-2 ring-emerald-500' : ''
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="inline-flex items-center gap-1 rounded-full bg-emerald-500 px-3 py-1 text-xs font-semibold text-slate-950">
                    <Star size={12} weight="fill" />
                    Más popular
                  </span>
                </div>
              )}

              {isCurrentPlan && isSubscribed && (
                <div className="absolute -top-3 right-4">
                  <span className="rounded-full bg-emerald-500/20 px-3 py-1 text-xs font-medium text-emerald-400">
                    Plan actual
                  </span>
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-xl font-bold text-slate-100">
                  {plan.name}
                </h3>
                <div className="mt-3">
                  {plan.price !== null ? (
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-bold text-slate-100">
                        ${plan.price}
                      </span>
                      <span className="text-sm text-slate-400">/mes</span>
                    </div>
                  ) : (
                    <span className="text-2xl font-bold text-slate-100">
                      Personalizado
                    </span>
                  )}
                </div>
              </div>

              <ul className="mb-8 flex-1 space-y-3">
                {plan.features.map((feature) => (
                  <li
                    key={feature}
                    className="flex items-start gap-2 text-sm text-slate-300"
                  >
                    <Check
                      size={16}
                      className="mt-0.5 shrink-0 text-emerald-400"
                      weight="bold"
                    />
                    {feature}
                  </li>
                ))}
              </ul>

              {plan.price !== null ? (
                isCurrentPlan && isSubscribed ? (
                  <Button
                    variant="secondary"
                    onClick={() => navigate('/settings')}
                  >
                    Gestionar suscripción
                  </Button>
                ) : (
                  <Button
                    variant={plan.popular ? 'primary' : 'secondary'}
                    isLoading={isLoading}
                    disabled={isLoading}
                    rightIcon={<ArrowRight size={16} weight="bold" />}
                    onClick={() => {
                      setErrorMsg(null);
                      checkoutMutation.mutate(plan.priceId);
                    }}
                  >
                    {isTrial ? 'Actualizar ahora' : 'Comenzar'}
                  </Button>
                )
              ) : (
                <Button
                  variant="secondary"
                  onClick={() =>
                    (window.location.href = 'mailto:sales@script9.com')
                  }
                >
                  Contactar ventas
                </Button>
              )}
            </div>
          );
        })}
      </div>

      {isTrial && (
        <div className="mx-auto mt-12 max-w-xl text-center">
          <p className="text-sm text-slate-400">
            Estás en el plan Trial — sin límite de tiempo, pero con funciones
            limitadas. Actualizá a un plan pago para desbloquear todo el
            potencial de Script9 Engine.
          </p>
        </div>
      )}
    </div>
  );
}
