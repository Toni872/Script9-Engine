import { type ReactNode } from 'react'
import { motion } from 'framer-motion'

interface CardHoverProps {
  children: ReactNode
  className?: string
  /** Vertical lift in px (default -5) */
  lift?: number
}

/**
 * CardHover — adds a smooth upward hover to any child element.
 *
 * @example
 * <CardHover>
 *   <GlassCard>…</GlassCard>
 * </CardHover>
 */
export function CardHover({ children, className = '', lift = -5 }: CardHoverProps) {
  return (
    <motion.div
      className={className}
      whileHover={{ y: lift }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
    >
      {children}
    </motion.div>
  )
}
