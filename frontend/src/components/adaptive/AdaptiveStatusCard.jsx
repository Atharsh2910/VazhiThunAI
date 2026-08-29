import React from 'react';

const statusBadge = (isOnTrack) => isOnTrack
  ? <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">✓ On track</span>
  : <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-orange-50 text-orange-700 border border-orange-200">⚠ At risk</span>;

const AdaptiveStatusCard = ({ status, onOpenSimulator }) => {
  if (!status) {
    return (
      <div className="rounded-xl border border-slate-200 bg-white p-6 animate-pulse">
        <div className="h-4 bg-slate-100 rounded w-1/3 mb-3" />
        <div className="h-3 bg-slate-100 rounded w-2/3" />
      </div>
    );
  }

  const {
    current_item,
    completion_percentage,
    weekly_hours,
    projected_completion_weeks,
    deadline_weeks,
    remaining_hours,
    is_on_track,
    recent_adaptations = [],
  } = status;

  const deadlineDate = deadline_weeks
    ? new Date(Date.now() + deadline_weeks * 7 * 24 * 60 * 60 * 1000).toLocaleDateString('en-IN', {
        month: 'short', day: 'numeric',
      })
    : '—';

  const completionDate = projected_completion_weeks
    ? new Date(Date.now() + projected_completion_weeks * 7 * 24 * 60 * 60 * 1000).toLocaleDateString('en-IN', {
        month: 'short', day: 'numeric',
      })
    : '—';

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-5 flex-wrap gap-2">
        <div>
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
            🎯 Adaptive Learning Path — ML Engineer
          </h3>
          {current_item && (
            <p className="text-slate-900 font-semibold text-base mt-1">
              Current activity: <span className="text-blue-600 font-bold">{current_item.stage_title || current_item.title}</span>
            </p>
          )}
        </div>
        <div>
          {statusBadge(is_on_track)}
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex justify-between text-xs text-slate-500 mb-1.5 font-medium">
          <span>Overall Progress</span>
          <span className="font-bold text-slate-700">{completion_percentage}%</span>
        </div>
        <div className="w-full bg-slate-100 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-700 ${is_on_track ? 'bg-emerald-500' : 'bg-orange-500'}`}
            style={{ width: `${completion_percentage}%` }}
          />
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-100">
          <p className="text-3xs font-semibold uppercase tracking-wider text-slate-400">Pace</p>
          <p className="text-base font-bold text-slate-800 mt-0.5">{weekly_hours} <span className="text-xs font-medium text-slate-500">hrs/wk</span></p>
        </div>
        <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-100">
          <p className="text-3xs font-semibold uppercase tracking-wider text-slate-400">Remaining</p>
          <p className="text-base font-bold text-slate-800 mt-0.5">{remaining_hours?.toFixed(0)} <span className="text-xs font-medium text-slate-500">hrs</span></p>
        </div>
        <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-100">
          <p className="text-3xs font-semibold uppercase tracking-wider text-slate-400">Est. Finish</p>
          <p className="text-base font-bold text-slate-800 mt-0.5">{completionDate}</p>
        </div>
        <div className="bg-slate-50 rounded-lg p-3.5 border border-slate-100">
          <p className="text-3xs font-semibold uppercase tracking-wider text-slate-400">Deadline</p>
          <p className="text-base font-bold text-slate-800 mt-0.5">{deadlineDate}</p>
        </div>
      </div>

      {/* Recent adaptations */}
      {recent_adaptations.length > 0 && (
        <div className="mb-5 border-t border-slate-100 pt-4">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2.5">Recent adaptations</p>
          <div className="space-y-2">
            {recent_adaptations.slice(0, 3).map((evt, i) => (
              <div key={i} className="flex items-start gap-2.5 text-xs text-slate-600 bg-slate-50/50 p-2 rounded-md border border-slate-100">
                <span className="flex-shrink-0 text-slate-400">
                  {evt.event_type === 'RESOURCE_REPLACED' ? '↻' :
                   evt.event_type === 'REMEDIATION_INSERTED' ? '🔧' :
                   evt.event_type === 'ITEM_SKIPPED' ? '✓' : '•'}
                </span>
                <span className="leading-relaxed">{evt.explanation || evt.trigger}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3 flex-wrap">
        <button
          id="open-what-if-simulator"
          onClick={onOpenSimulator}
          className="text-xs px-3.5 py-2 rounded-lg bg-blue-50 text-blue-600 border border-blue-200 hover:bg-blue-100 transition-colors font-semibold"
        >
          📊 What-If Simulator
        </button>
        {!is_on_track && (
          <span className="text-xs px-3.5 py-2 rounded-lg bg-orange-50 text-orange-700 border border-orange-100 font-semibold">
            ⚠️ Behind schedule — run simulator
          </span>
        )}
      </div>
    </div>
  );
};

export default AdaptiveStatusCard;
