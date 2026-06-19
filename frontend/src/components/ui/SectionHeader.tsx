import { TechBadge } from './TechBadge'

interface SectionHeaderProps {
  /** TechBadge label above the title */
  eyebrow?: string
  title: string
  subtitle?: string
  align?: 'left' | 'center'
  className?: string
}

/**
 * SectionHeader — the standard title block used at the top of every section.
 *
 * @example
 * <SectionHeader
 *   eyebrow="Automatización"
 *   title="Orquesta tus agentes de IA"
 *   subtitle="Script9 Engine gestiona el ciclo completo de ejecución."
 *   align="center"
 * />
 */
export function SectionHeader({
  eyebrow,
  title,
  subtitle,
  align = 'left',
  className = '',
}: SectionHeaderProps) {
  const isCenter = align === 'center'

  return (
    <div className={['flex flex-col gap-4', isCenter ? 'items-center text-center' : 'items-start', className].join(' ')}>
      {eyebrow && <TechBadge>{eyebrow}</TechBadge>}

      <h2 className="text-3xl md:text-5xl font-bold font-space tracking-tight text-white leading-tight">
        {title}
      </h2>

      {subtitle && (
        <p
          className={[
            'text-lg text-slate-400 font-inter font-light leading-relaxed',
            isCenter ? 'max-w-2xl' : 'max-w-xl',
          ].join(' ')}
        >
          {subtitle}
        </p>
      )}
    </div>
  )
}
