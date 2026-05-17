import { useAuth } from '@/hooks/useAuth';

export function Dashboard() {
  const { user } = useAuth();

  return (
    <div className="mx-auto max-w-7xl px-6 py-8">
      <h1 className="mb-2 text-2xl font-bold">
        Hola, <span className="text-emerald-400">{user?.displayName}</span>
      </h1>
      <p className="text-sm text-slate-400">
        Panel principal — próximamente con métricas, fichajes y reportes.
      </p>
    </div>
  );
}
