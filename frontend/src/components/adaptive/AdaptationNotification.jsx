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
    REMEDIATION_INSERTED: '⚠',
    ITEM_SKIPPED: '✓',
    VERIFICATION_REQUESTED: '🔍',
    NO_CHANGE: '✓',
    HOURS_UPDATED: '⏱',
    DEADLINE_UPDATED: '📅',
    PATH_LIGHTENED: '🪶',
  }[adaptation.adaptation_type] || '•';

  return (
    <div
      className={`fixed bottom-6 right-6 z-50 max-w-sm w-full rounded-2xl shadow-2xl border px-5 py-4 
        ${isPositive
          ? 'bg-white border-indigo-200 text-gray-800'
          : 'bg-white border-red-200 text-gray-800'}
        animate-slide-up`}
      style={{ animation: 'slideUp 0.3s ease-out' }}
    >
      <style>{`
        @keyframes slideUp {
          from { transform: translateY(20px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}</style>

      <div className="flex items-start gap-3">
        <span className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-base font-bold 
          ${isPositive ? 'bg-indigo-100 text-indigo-600' : 'bg-red-100 text-red-600'}`}>
          {icon}
        </span>
        <div className="flex-grow">
          <p className="text-sm font-semibold">
            {isPositive ? '✓ Your path has been updated' : 'Could not adapt path'}
          </p>
          <p className="text-xs text-gray-500 mt-1 line-clamp-3">
            {adaptation.explanation || adaptation.message || 'Your learning path has been adjusted.'}
          </p>
          {adaptation.adaptation_type === 'VERIFICATION_REQUESTED' && (
            <p className="text-xs text-indigo-600 mt-1 font-medium">
              → A verification check will appear next
            </p>
          )}
        </div>
        <button
          onClick={onDismiss}
          className="flex-shrink-0 text-gray-300 hover:text-gray-500 text-lg leading-none transition-colors"
        >
          ×
        </button>
      </div>
    </div>
  );
};

export default AdaptationNotification;
