import { GlassCard } from './GlassCard';
import {
  EnvelopeSimple,
  Calendar,
  CheckCircle,
  ArrowRight,
  Robot,
  UserPlus,
} from '@phosphor-icons/react';

interface ActivityCardProps {
  tipo: string;
  payload: Record<string, unknown>;
  creado_en: string;
}

const tipoIcons: Record<string, React.ReactNode> = {
  lead_captured: <EnvelopeSimple size={16} />,
  meeting_scheduled: <Calendar size={16} />,
  meeting_confirmed: <CheckCircle size={16} />,
  crm_synced: <ArrowRight size={16} />,
  subscription_activated: <CheckCircle size={16} />,
  invitation_sent: <UserPlus size={16} />,
};

const tipoLabels: Record<string, string> = {
  lead_captured: 'Lead capturado',
  meeting_scheduled: 'Reunión propuesta',
  meeting_confirmed: 'Reunión confirmada',
  crm_synced: 'Sincronizado CRM',
  subscription_activated: 'Suscripción activada',
  invitation_sent: 'Invitación enviada',
};

function timeAgo(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 60) return `hace ${diffMins} min`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `hace ${diffHours}h`;
  const diffDays = Math.floor(diffHours / 24);
  return `hace ${diffDays}d`;
}

export function ActivityCard({ tipo, payload, creado_en }: ActivityCardProps) {
  const icon = tipoIcons[tipo] || <Robot size={16} />;
  const label = tipoLabels[tipo] || tipo;

  const payloadPreview = payload && Object.keys(payload).length > 0
    ? JSON.stringify(payload).slice(0, 50)
    : null;

  return (
    <GlassCard compact className="flex items-center gap-4">
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <span className="text-emerald-400 flex-shrink-0">{icon}</span>
        <div className="flex flex-col gap-0.5 min-w-0">
          <span className="text-sm font-inter text-slate-200 truncate">{label}</span>
          {payloadPreview && (
            <span className="text-xs text-slate-500 truncate">
              {payloadPreview}
            </span>
          )}
        </div>
      </div>
      <span className="text-xs text-slate-500 flex-shrink-0">{timeAgo(creado_en)}</span>
    </GlassCard>
  );
}
