import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { CheckCircle, ArrowRight, RocketLaunch } from '@phosphor-icons/react';

const APP_NAMES: Record<string, string> = {
  tempos: 'Tempos',
  script9: 'Script9 Engine',
};

function getAppName(key: string): string {
  return APP_NAMES[key] || key.charAt(0).toUpperCase() + key.slice(1);
}

export function SuccessPayment() {
  const [searchParams] = useSearchParams();
  const appKey = searchParams.get('app') || 'script9';
  const appName = getAppName(appKey);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    // Animación de entrada
    const t = setTimeout(() => setVisible(true), 100);
    return () => clearTimeout(t);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6">
      <div
        className={`max-w-lg w-full text-center transition-all duration-700 ${
          visible
            ? 'opacity-100 translate-y-0'
            : 'opacity-0 translate-y-4'
        }`}
      >
        {/* Icono de éxito */}
        <div className="mb-6 flex justify-center">
          <div className="rounded-full bg-emerald-500/10 p-4">
            <CheckCircle
              size={64}
              className="text-emerald-400"
              weight="fill"
            />
          </div>
        </div>

        {/* Título */}
        <h1 className="text-3xl font-bold text-slate-100 mb-2">
          ¡Pago exitoso!
        </h1>
        <p className="text-lg text-slate-400 mb-8">
          Tu suscripción a{' '}
          <span className="font-semibold text-emerald-400">{appName}</span> se
          activó correctamente.
        </p>

        {/* Detalles */}
        <div className="glass-card mb-8 p-6 text-left space-y-3">
          <div className="flex items-start gap-3">
            <RocketLaunch
              size={20}
              className="mt-0.5 shrink-0 text-emerald-400"
              weight="fill"
            />
            <div>
              <p className="text-sm font-medium text-slate-200">
                ¿Qué sigue?
              </p>
              <p className="text-sm text-slate-400">
                Ya podés acceder a todas las funciones premium de {appName}.
                Revisá tu correo para ver la factura y los detalles de la
                suscripción.
              </p>
            </div>
          </div>
        </div>

        {/* Acciones */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link
            to="/dashboard"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-emerald-500 px-6 py-3 text-sm font-semibold text-slate-950 transition-colors hover:bg-emerald-400"
          >
            Ir al Dashboard
            <ArrowRight size={16} weight="bold" />
          </Link>
          <a
            href={`https://${appKey}.script-9.com`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center justify-center rounded-lg border border-slate-700 px-6 py-3 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-800"
          >
            Volver a {appName}
          </a>
        </div>

        {/* Footer */}
        <p className="mt-12 text-xs text-slate-600">
          ¿Tenés dudas? Escribinos a{' '}
          <a
            href="mailto:soporte@script-9.com"
            className="text-emerald-500 hover:underline"
          >
            soporte@script-9.com
          </a>
        </p>
      </div>
    </div>
  );
}
