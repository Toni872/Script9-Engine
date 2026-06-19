import { type ReactNode } from 'react'

interface GridBackgroundProps {
  children?: ReactNode
  className?: string
}

/**
 * GridBackground — the subtle 4rem grid that tiles across dark sections.
 * Position absolutely or as a full-bleed wrapper. Content goes inside.
 *
 * @example
 * <GridBackground className="absolute inset-0 z-0" />
 */
export function GridBackground({ children, className = '' }: GridBackgroundProps) {
  return (
    <div
      aria-hidden={!children}
      className={['pointer-events-none', className].join(' ')}
      style={{
        backgroundImage: `
          linear-gradient(to right,  rgba(255,255,255,0.03) 1px, transparent 1px),
          linear-gradient(to bottom, rgba(255,255,255,0.03) 1px, transparent 1px)
        `,
        backgroundSize: '4rem 4rem',
      }}
    >
      {children}
    </div>
  )
}
