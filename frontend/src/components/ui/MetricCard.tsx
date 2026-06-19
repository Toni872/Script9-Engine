import { GlassCard } from './GlassCard';
import { MetricNumber } from './MetricNumber';
import { Sparkline } from './Sparkline';
import { TrendUp, TrendDown } from '@phosphor-icons/react';
import { type ReactNode } from 'react';

interface MetricCardProps {
  title: string;
  value: number | string;
  delta_pct?: number;
  sparkline?: number[];
  icon?: ReactNode;
}

export function MetricCard({ title, value, delta_pct, sparkline, icon }: MetricCardProps) {
  const trend = delta_pct === undefined ? 'neutral' : delta_pct > 0 ? 'up' : delta_pct < 0 ? 'down' : 'neutral';

  return (
    <GlassCard hover>
      <div className="flex flex-col gap-3">
        <div className="flex items-center justify-between">
          <span className="text-sm font-inter text-slate-400">{title}</span>
          {icon && <span className="text-emerald-400">{icon}</span>}
        </div>
        <div className="flex items-end gap-3">
          <MetricNumber value={value} trend={trend} />
          {delta_pct !== undefined && (
            <div className={`flex items-center gap-1 text-sm font-mono mb-1 ${
              trend === 'up' ? 'text-emerald-400' : trend === 'down' ? 'text-red-400' : 'text-slate-500'
            }`}>
              {trend === 'up' && <TrendUp size={14} weight="bold" />}
              {trend === 'down' && <TrendDown size={14} weight="bold" />}
              <span>{delta_pct > 0 ? '+' : ''}{delta_pct}%</span>
            </div>
          )}
        </div>
        {sparkline && sparkline.length > 0 && (
          <div className="mt-2">
            <Sparkline data={sparkline} width={120} height={32} />
          </div>
        )}
      </div>
    </GlassCard>
  );
}
