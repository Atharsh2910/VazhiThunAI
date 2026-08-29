import React from 'react';

/**
 * Card — base surface component.
 * Props: className, children, hover (bool), padding (string override)
 * All existing usage preserved — className prop still forwarded.
 */
const Card = ({ children, className = '', hover = false }) => {
  return (
    <div
      className={[
        'bg-white border border-slate-200 rounded-xl shadow-sm',
        'p-6',
        hover ? 'hover:shadow-md hover:border-slate-300 transition-all duration-150' : '',
        className,
      ].filter(Boolean).join(' ')}
    >
      {children}
    </div>
  );
};

export default Card;
