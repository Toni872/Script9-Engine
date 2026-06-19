import { type ReactNode } from 'react'

interface GlassCardProps {
  children?: ReactNode
  className?: string
  /** Enable hover lift + glow effects */
  hover?: boolean
  /** Compact padding (p-4 instead of p-6) */
  compact?: boolean
  as?: keyof JSX.IntrinsicElements
}

/**
 * GlassCard — dark glass surface with optional hover glow.
 * The foundational card primitive of the Script9 design system.
 *
 * @example
 * <GlassCard hover>
 *   <MetricNumber value="98.7%" label="Uptime" />
 * </GlassCard>
 */
export function GlassCard({
  children,
  className = '',
  hover = false,
  compact = false,
  as: Tag = 'div',
}: GlassCardProps) {
  const base = [
    'bg-slate-900/40 border border-slate-800/80 rounded-2xl',
    compact ? 'p-4' : 'p-6',
    'transition-all duration-300',
  ]

  const hoverStyles = hover
    ? [
        'cursor-pointer',
        'hover:border-emerald-500/30',
        'hover:bg-slate-900/60',
        'hover:shadow-script9-glow',
        'hover:-translate-y-0.5',
      ]
    : []

  return (
    <Tag className={[...base, ...hoverStyles, className].join(' ')}>
      {children}
    </Tag>
  )
}
