import { type ReactNode } from 'react'

type TechBadgeVariant = 'default' | 'success' | 'warning' | 'error'

interface TechBadgeProps {
  children: ReactNode
  variant?: TechBadgeVariant
  className?: string
}

const variantStyles: Record<TechBadgeVariant, string> = {
  default: 'text-emerald-400 border-slate-800',
  success: 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10',
  warning: 'text-yellow-400 border-yellow-500/30 bg-yellow-500/10',
  error:   'text-red-400   border-red-500/30   bg-red-500/10',
}

/**
 * TechBadge — inline label for technical categories, statuses, or tags.
 * Monospaced, pill-shaped, dark surface.
 *
 * @example
 * <TechBadge>FastAPI</TechBadge>
 * <TechBadge variant="success">Activo</TechBadge>
 * <TechBadge variant="error">Error 500</TechBadge>
 */
export function TechBadge({ children, variant = 'default', className = '' }: TechBadgeProps) {
  return (
    <span
      className={[
        'inline-flex items-center gap-2 px-3 py-1',
        'rounded-full bg-slate-900 border',
        'text-xs font-mono font-medium',
        'select-none',
        variantStyles[variant],
        className,
      ].join(' ')}
    >
      {children}
    </span>
  )
}
