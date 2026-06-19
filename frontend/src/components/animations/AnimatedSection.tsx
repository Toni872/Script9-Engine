import { type ReactNode } from 'react'
import { motion } from 'framer-motion'

interface AnimatedSectionProps {
  children: ReactNode
  className?: string
  /** Y offset to animate from (default 20px) */
  offset?: number
  /** Animation duration in seconds */
  duration?: number
  /** Delay in seconds */
  delay?: number
}

/**
 * AnimatedSection — fades + slides children into view on scroll.
 * Fires once per mount; no re-trigger on scroll back up.
 *
 * @example
 * <AnimatedSection>
 *   <SectionHeader title="Características" />
 * </AnimatedSection>
 */
export function AnimatedSection({
  children,
  className = '',
  offset = 20,
  duration = 0.5,
  delay = 0,
}: AnimatedSectionProps) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, y: offset }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: '-50px' }}
      transition={{ duration, delay, ease: [0.16, 1, 0.3, 1] }}
    >
      {children}
    </motion.div>
  )
}
