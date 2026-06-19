import { useUsuario } from '@/hooks/useUsuario';
import { useAuth } from '@/hooks/useAuth';
import { MetricCard } from '@/components/ui/MetricCard';
import { ActivityCard } from '@/components/ui/ActivityCard';
import { GlassCard } from '@/components/ui/GlassCard';
import { SectionHeader } from '@/components/ui/SectionHeader';
import { useLeadsThisWeek } from '@/hooks/useLeadsThisWeek';
import { useActivityFeed } from '@/hooks/useActivityFeed';
import { EnvelopeSimple, ChartLine, Share, GearSix, SignOut } from '@phosphor-icons/react';
import { useNavigate } from 'react-router-dom';

export function Dashboard() {
  const { user, logout } = useAuth();
  const { data: usuario } = useUsuario();
  const { data: leadsMetric, isLoading: metricLoading } = useLeadsThisWeek();
  const { data: activityFeed, isLoading: feedLoading } = useActivityFeed(7);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const shareUrl = `https://script-9.com/l/${usuario?.nombre?.toLowerCase().replace(/\s+/g, '-') || 'tu-slug'}`;

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
          <button
            onClick={() => navigate('/settings')}
            className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-slate-400 transition-colors hover:bg-slate-800/50 hover:text-slate-200"
          >
            <GearSix size={16} />
            Ajustes
          </button>
          <button
            onClick={handleLogout}
            className="inline-flex items-center gap-1.5 rounded-lg px-3 py-1.5 text-sm text-slate-400 transition-colors hover:bg-slate-800/50 hover:text-slate-200"
          >
            <SignOut size={16} />
            Salir
          </button>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {metricLoading ? (
          <>
            <GlassCard className="h-32 animate-pulse bg-slate-800/30" />
            <GlassCard className="h-32 animate-pulse bg-slate-800/30" />
            <GlassCard className="h-32 animate-pulse bg-slate-800/30" />
          </>
        ) : (
          <MetricCard
            title="Leads esta semana"
            value={leadsMetric?.value ?? 0}
            delta_pct={leadsMetric?.delta_pct}
            sparkline={leadsMetric?.sparkline}
            icon={<ChartLine size={20} />}
          />
        )}
      </div>

      {/* Activity Feed */}
      <section>
        <SectionHeader
          title="Actividad reciente"
          subtitle="Tus últimos 7 días"
          className="mb-4"
        />

        {feedLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map(i => (
              <GlassCard key={i} compact className="h-16 animate-pulse bg-slate-800/30" />
            ))}
          </div>
        ) : activityFeed && activityFeed.events.length > 0 ? (
          <div className="space-y-3">
            {activityFeed.events.map(event => (
              <ActivityCard
                key={event.id}
                tipo={event.tipo}
                payload={event.payload}
                creado_en={event.creado_en}
              />
            ))}
          </div>
        ) : (
          <GlassCard className="flex flex-col items-center text-center py-12 gap-4">
            <EnvelopeSimple size={48} className="text-slate-600" />
            <div>
              <p className="text-slate-400 mb-2">Aún no hay actividad.</p>
              <p className="text-sm text-slate-500">Comparte tu formulario para empezar a capturar leads.</p>
            </div>
            <div className="flex flex-col items-center gap-2 mt-2">
              <p className="text-xs text-slate-500">Tu enlace de formulario:</p>
              <code className="text-sm font-mono text-emerald-400 bg-slate-900/50 px-3 py-2 rounded-lg border border-slate-800">
                {shareUrl}
              </code>
              <button
                onClick={() => navigator.clipboard.writeText(shareUrl)}
                className="inline-flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 transition-colors"
              >
                <Share size={14} />
                Copiar enlace
              </button>
            </div>
          </GlassCard>
        )}
      </section>
    </div>
  );
}
