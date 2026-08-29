import React, { useEffect } from 'react';

const AdaptationNotification = ({ adaptation, onDismiss }) => {
  useEffect(() => {
    if (!adaptation) return;
    const timer = setTimeout(onDismiss, 8000);
    return () => clearTimeout(timer);
  }, [adaptation, onDismiss]);

  if (!adaptation) return null;

  const isPositive = adaptation.success !== false;
  const icon = {
    RESOURCE_REPLACED: '↻',
    REMEDIATION_INSERTED: '⚠️',
    ITEM_SKIPPED: '✓',
    VERIFICATION_REQUESTED: '🔍',
    NO_CHANGE: '✓',
    HOURS_UPDATED: '⏱',
    DEADLINE_UPDATED: '📅',
    PATH_LIGHTENED: '🪶',
  }[adaptation.adaptation_type] || '•';

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 max-w-sm w-full rounded-xl shadow-lg border px-5 py-4 bg-white 
        ${isPositive ? 'border-blue-100 text-slate-800' : 'border-red-100 text-slate-800'}
        animate-slide-up`}
      style={{ animation: 'slideUp 0.3s ease-out' }}
    >
      <style>{`
        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}</style>

      <div className="flex items-start gap-3.5">
        <span className={`flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold 
          ${isPositive ? 'bg-blue-50 text-blue-600' : 'bg-red-50 text-red-600'}`}>
          {icon}
        </span>
        <div className="flex-grow">
          <p className="text-sm font-semibold text-slate-900">
            {isPositive ? '✓ Path updated' : 'Could not adapt path'}
          </p>
          <p className="text-xs text-slate-500 mt-1 line-clamp-3 leading-relaxed">
            {adaptation.explanation || adaptation.message || 'Your learning path has been adjusted.'}
          </p>
          {adaptation.adaptation_type === 'VERIFICATION_REQUESTED' && (
            <p className="text-xs text-blue-600 mt-1.5 font-semibold">
              → Verification check in progress
            </p>
          )}
        </div>
        <button
          onClick={onDismiss}
          className="flex-shrink-0 text-slate-300 hover:text-slate-500 text-lg leading-none transition-colors"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default AdaptationNotification;
