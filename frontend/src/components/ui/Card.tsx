import { motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface CardProps {
  title?: string;
  description?: string;
  children?: ReactNode;
  className?: string;
  /** Acciones a mostrar en la esquina superior derecha */
  actions?: ReactNode;
  /** Sombra con glow emerald */
  glow?: boolean;
}

export function Card({
  title,
  description,
  children,
  className = '',
  actions,
  glow = false,
}: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className={`
        glass-card
        ${glow ? 'shadow-[0_0_15px_rgba(16,185,129,0.15)]' : ''}
        ${className}
      `}
    >
      {/* Header */}
      {(title || actions) && (
        <div className="mb-4 flex items-start justify-between gap-4">
          <div>
            {title && (
              <h3 className="text-lg font-semibold text-slate-100">{title}</h3>
            )}
            {description && (
              <p className="mt-1 text-sm text-slate-400">{description}</p>
            )}
          </div>
          {actions && <div className="flex shrink-0 gap-2">{actions}</div>}
        </div>
      )}

      {/* Content */}
      {children && <div>{children}</div>}
    </motion.div>
  );
}
