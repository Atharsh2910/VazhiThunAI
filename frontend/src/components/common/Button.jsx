import React from 'react';

/**
 * Button — generic clickable element with design system states.
 * Reuses same interface: children, variant ('primary'|'secondary'|'outline'|'danger'), className, disabled, type, onClick, etc.
 */
const Button = ({ children, variant = 'primary', className = '', ...props }) => {
  const baseStyle = 'px-4 py-2 text-sm font-medium rounded-lg shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 active:scale-[0.98]',
    secondary: 'bg-slate-100 text-slate-700 hover:bg-slate-200 focus:ring-slate-500 active:scale-[0.98]',
    outline: 'border border-slate-200 text-slate-700 hover:bg-slate-50 active:scale-[0.98]',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 active:scale-[0.98]',
    orange: 'bg-orange-500 text-white hover:bg-orange-600 focus:ring-orange-500 active:scale-[0.98]',
  };

  return (
    <button className={`${baseStyle} ${variants[variant] || variants.primary} ${className}`} {...props}>
      {children}
    </button>
  );
};

export default Button;
