import { type ReactNode } from 'react'
import { motion, type Variants } from 'framer-motion'

interface StaggerChildrenProps {
  children: ReactNode
  className?: string
  /** Delay between each child (seconds) */
  stagger?: number
  /** Initial delay before the first item (seconds) */
  initialDelay?: number
}

const containerVariants: Variants = {
  hidden: {},
  visible: (stagger: number) => ({
    transition: { staggerChildren: stagger },
  }),
}

export const itemVariants: Variants = {
  hidden:  { opacity: 0, y: 16 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.45, ease: [0.16, 1, 0.3, 1] } },
}

/**
 * StaggerChildren — animates each direct child with a staggered delay.
 * Wrap list items with <motion.div variants={itemVariants}>.
 *
 * @example
 * <StaggerChildren stagger={0.1}>
 *   {features.map(f => (
 *     <motion.div key={f.id} variants={itemVariants}>
 *       <GlassCard hover>{f.name}</GlassCard>
 *     </motion.div>
 *   ))}
 * </StaggerChildren>
 */
export function StaggerChildren({
  children,
  className = '',
  stagger = 0.1,
  initialDelay = 0,
}: StaggerChildrenProps) {
  return (
    <motion.div
      className={className}
      variants={containerVariants}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: '-50px' }}
      custom={stagger}
      transition={{ delayChildren: initialDelay }}
    >
      {children}
    </motion.div>
  )
}
