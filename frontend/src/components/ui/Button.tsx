import { type ReactNode } from 'react'
import { motion, type HTMLMotionProps } from 'framer-motion'

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'
type ButtonSize    = 'sm' | 'md' | 'lg'

type ButtonProps = {
  children: ReactNode
  variant?: ButtonVariant
  size?: ButtonSize
  loading?: boolean
  leftIcon?: ReactNode
  rightIcon?: ReactNode
  fullWidth?: boolean
} & Omit<HTMLMotionProps<'button'>, 'children'>

const variantStyles: Record<ButtonVariant, string> = {
  primary: [
    'bg-emerald-500 text-slate-950 font-semibold',
    'shadow-script9-glow',
    'hover:bg-emerald-400 hover:shadow-script9-glow-lg',
  ].join(' '),

  secondary: [
    'bg-slate-900 border border-slate-800 text-emerald-400',
    'hover:border-emerald-500/30 hover:bg-slate-800',
  ].join(' '),

  ghost: [
    'bg-transparent text-emerald-400',
    'hover:bg-emerald-500/10',
  ].join(' '),

  danger: [
    'bg-red-500 text-white font-semibold',
    'hover:bg-red-400',
  ].join(' '),
}

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'h-8  px-3 text-xs gap-1.5 rounded-lg',
  md: 'h-10 px-5 text-sm gap-2   rounded-xl',
  lg: 'h-12 px-7 text-base gap-2 rounded-xl',
}

/**
 * Button — the primary interactive element of Script9 Engine.
 * Powered by Framer Motion for subtle scale feedback.
 *
 * @example
 * <Button variant="primary" size="lg">Crear agente</Button>
 * <Button variant="secondary" leftIcon={<PlusIcon />}>Nuevo script</Button>
 * <Button variant="danger">Eliminar</Button>
 */
export function Button({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  leftIcon,
  rightIcon,
  fullWidth = false,
  className = '',
  disabled,
  ...rest
}: ButtonProps) {
  const isDisabled = disabled || loading

  return (
    <motion.button
      whileHover={isDisabled ? undefined : { scale: 1.02 }}
      whileTap={isDisabled  ? undefined : { scale: 0.98 }}
      transition={{ duration: 0.15, ease: 'easeOut' }}
      disabled={isDisabled}
      className={[
        'inline-flex items-center justify-center',
        'font-inter transition-colors duration-200',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:ring-offset-2 focus-visible:ring-offset-slate-950',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        variantStyles[variant],
        sizeStyles[size],
        fullWidth ? 'w-full' : '',
        className,
      ].join(' ')}
      {...rest}
    >
      {loading ? (
        <span className="inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : leftIcon}

      <span>{children}</span>

      {!loading && rightIcon}
    </motion.button>
  )
}
