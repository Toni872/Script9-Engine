import { type ReactNode } from 'react'

type GlowColor = 'emerald' | 'blue' | 'purple'

interface GlowBackgroundProps {
  children?: ReactNode
  className?: string
  color?: GlowColor
  /** Size of the blur orb as a Tailwind w-* value (e.g. 'w-96') */
  size?: string
}

const colorMap: Record<GlowColor, string> = {
  emerald: 'bg-emerald-500/5',
  blue:    'bg-blue-500/5',
  purple:  'bg-purple-500/5',
}

/**
 * GlowBackground — absolute-positioned ambient blur orb.
 * Wrap a section with relative positioning and drop this inside.
 *
 * @example
 * <section className="relative overflow-hidden py-24">
 *   <GlowBackground color="emerald" />
 *   <div className="relative z-10">…content…</div>
 * </section>
 */
export function GlowBackground({
  children,
  className = '',
  color = 'emerald',
  size = 'w-[600px] h-[600px]',
}: GlowBackgroundProps) {
  return (
    <>
      <div
        aria-hidden
        className={[
          'pointer-events-none absolute inset-0 flex items-center justify-center',
          className,
        ].join(' ')}
      >
        <div
          className={[
            colorMap[color],
            size,
            'rounded-full blur-[120px]',
          ].join(' ')}
        />
      </div>
      {children}
    </>
  )
}
