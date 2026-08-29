import React from 'react';

const statusIcon = (isOnTrack) => isOnTrack
  ? <span className="text-emerald-600 font-semibold">✓ On track</span>
  : <span className="text-amber-600 font-semibold">⚠ At risk</span>;

const AdaptiveStatusCard = ({ status, onOpenSimulator }) => {
  if (!status) {
    return (
      <div className="rounded-2xl border border-gray-200 bg-white p-5 animate-pulse">
        <div className="h-4 bg-gray-100 rounded w-1/3 mb-3" />
        <div className="h-3 bg-gray-100 rounded w-2/3" />
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
    <div className={`rounded-2xl border p-5 ${is_on_track ? 'border-emerald-200 bg-gradient-to-br from-emerald-50 to-white' : 'border-amber-200 bg-gradient-to-br from-amber-50 to-white'}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wide">
            🎯 Adaptive Learning — ML Engineer
          </h3>
          {current_item && (
            <p className="text-gray-800 font-semibold text-sm mt-0.5">
              Current: {current_item.stage_title || current_item.title}
            </p>
          )}
        </div>
        <div className="text-right">
          {statusIcon(is_on_track)}
        </div>
      </div>

      {/* Progress bar */}
      <div className="mb-4">
        <div className="flex justify-between text-xs text-gray-500 mb-1">
          <span>Progress</span>
          <span>{completion_percentage}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-700 ${is_on_track ? 'bg-emerald-500' : 'bg-amber-500'}`}
            style={{ width: `${completion_percentage}%` }}
          />
        </div>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center mb-4">
        <div className="bg-white rounded-xl p-3 border border-gray-100">
          <p className="text-xs text-gray-400">Pace</p>
          <p className="text-base font-bold text-gray-800">{weekly_hours} <span className="text-xs font-normal">hrs/wk</span></p>
        </div>
        <div className="bg-white rounded-xl p-3 border border-gray-100">
          <p className="text-xs text-gray-400">Remaining</p>
          <p className="text-base font-bold text-gray-800">{remaining_hours?.toFixed(0)} <span className="text-xs font-normal">hrs</span></p>
        </div>
        <div className="bg-white rounded-xl p-3 border border-gray-100">
          <p className="text-xs text-gray-400">Est. Finish</p>
          <p className="text-base font-bold text-gray-800">{completionDate}</p>
        </div>
        <div className="bg-white rounded-xl p-3 border border-gray-100">
          <p className="text-xs text-gray-400">Deadline</p>
          <p className="text-base font-bold text-gray-800">{deadlineDate}</p>
        </div>
      </div>

      {/* Recent adaptations */}
      {recent_adaptations.length > 0 && (
        <div className="mb-3">
          <p className="text-xs text-gray-500 font-medium mb-2">Recent changes:</p>
          <div className="space-y-1.5">
            {recent_adaptations.slice(0, 3).map((evt, i) => (
              <div key={i} className="flex items-start gap-2 text-xs text-gray-600">
                <span className="flex-shrink-0 mt-0.5">
                  {evt.event_type === 'RESOURCE_REPLACED' ? '↻' :
                   evt.event_type === 'REMEDIATION_INSERTED' ? '⚠' :
                   evt.event_type === 'ITEM_SKIPPED' ? '✓' : '•'}
                </span>
                <span className="line-clamp-1">{evt.explanation || evt.trigger}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-2 flex-wrap">
        <button
          id="open-what-if-simulator"
          onClick={onOpenSimulator}
          className="text-xs px-3 py-1.5 rounded-lg bg-indigo-50 text-indigo-600 border border-indigo-200 hover:bg-indigo-100 transition-colors font-medium"
        >
          📊 What-If Simulator
        </button>
        {!is_on_track && (
          <span className="text-xs px-3 py-1.5 rounded-lg bg-amber-100 text-amber-700 border border-amber-200 font-medium">
            ⚠ Behind schedule — run simulator
          </span>
        )}
      </div>
    </div>
  );
};

export default AdaptiveStatusCard;
