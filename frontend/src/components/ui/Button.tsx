import { forwardRef } from 'react';
import { motion } from 'framer-motion';
import { Spinner } from '@phosphor-icons/react';

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

// Omit props that conflict with Framer Motion's motion.button types
interface ButtonProps
  extends Omit<
    React.ButtonHTMLAttributes<HTMLButtonElement>,
    'onDrag' | 'onDragStart' | 'onDragEnd' | 'onAnimationStart'
  > {
  variant?: ButtonVariant;
  size?: ButtonSize;
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const variantStyles: Record<ButtonVariant, string> = {
  primary:
    'bg-emerald-500 text-slate-950 font-bold hover:bg-emerald-400 shadow-[0_4px_14px_rgba(16,185,129,0.39)] hover:shadow-[0_4px_24px_rgba(16,185,129,0.23)]',
  secondary:
    'border border-blue-700 text-blue-400 font-medium hover:bg-blue-950/50',
  ghost:
    'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50',
  danger:
    'bg-red-600/10 text-red-400 border border-red-800/30 hover:bg-red-600/20',
};

const sizeStyles: Record<ButtonSize, string> = {
  sm: 'px-3 py-1.5 text-sm rounded-lg gap-1.5',
  md: 'px-5 py-2.5 text-sm rounded-lg gap-2',
  lg: 'px-8 py-4 text-base rounded-lg gap-2.5',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      isLoading = false,
      disabled,
      leftIcon,
      rightIcon,
      children,
      className = '',
      ...props
    },
    ref,
  ) => {
    const isDisabled = disabled || isLoading;

    return (
      <motion.button
        ref={ref}
        whileTap={{ scale: isDisabled ? 1 : 0.97 }}
        disabled={isDisabled}
        className={`
          inline-flex items-center justify-center
          transition-all duration-200
          disabled:opacity-50 disabled:cursor-not-allowed
          ${variantStyles[variant]}
          ${sizeStyles[size]}
          ${className}
        `}
        {...props}
      >
        {isLoading ? (
          <Spinner className="h-4 w-4 animate-spin" />
        ) : (
          leftIcon
        )}
        {children}
        {rightIcon && !isLoading && (
          <span className="transition-transform duration-200 group-hover:translate-x-0.5">
            {rightIcon}
          </span>
        )}
      </motion.button>
    );
  },
);

Button.displayName = 'Button';
