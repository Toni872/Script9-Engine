interface MetricNumberProps {
  value: string | number
  label?: string
  trend?: 'up' | 'down' | 'neutral'
  className?: string
}

const TrendIcon = ({ trend }: { trend: 'up' | 'down' | 'neutral' }) => {
  if (trend === 'up')
    return (
      <span className="inline-flex items-center gap-1 text-sm font-mono text-emerald-400">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden>
          <path d="M6 2L10 8H2L6 2Z" fill="currentColor" />
        </svg>
      </span>
    )
  if (trend === 'down')
    return (
      <span className="inline-flex items-center gap-1 text-sm font-mono text-red-400">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none" aria-hidden>
          <path d="M6 10L2 4H10L6 10Z" fill="currentColor" />
        </svg>
      </span>
    )
  return null
}

/**
 * MetricNumber — large KPI display with optional label and trend indicator.
 *
 * @example
 * <MetricNumber value="98.7%" label="Uptime" trend="up" />
 * <MetricNumber value={1_240} label="Ejecuciones hoy" trend="down" />
 */
export function MetricNumber({ value, label, trend = 'neutral', className = '' }: MetricNumberProps) {
  return (
    <div className={`flex flex-col gap-1 ${className}`}>
      <div className="flex items-end gap-2">
        <span className="text-4xl lg:text-5xl font-bold font-mono text-emerald-400 tabular-nums leading-none">
          {value}
        </span>
        {trend !== 'neutral' && <TrendIcon trend={trend} />}
      </div>
      {label && (
        <span className="text-sm font-inter text-slate-400 font-light tracking-wide">
          {label}
        </span>
      )}
    </div>
  )
}
