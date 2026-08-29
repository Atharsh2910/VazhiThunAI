import React from 'react';

const triggerIcon = (trigger) => ({
  TOO_HARD: '😵',
  TOO_EASY: '👍',
  ALREADY_KNOWN: '🔁',
  KNOWLEDGE_GAP: '📚',
  MISCONCEPTION: '⚠',
  HOURS_CHANGE: '⏱',
  DEADLINE_CHANGE: '📅',
  FASTER_PATH: '⚡',
  LIGHTER_PATH: '🪶',
  FALLING_BEHIND: '⏰',
}[trigger] || '•');

const triggerColor = (trigger) => ({
  TOO_HARD: 'text-red-600 bg-red-50 border-red-200',
  TOO_EASY: 'text-emerald-600 bg-emerald-50 border-emerald-200',
  KNOWLEDGE_GAP: 'text-amber-600 bg-amber-50 border-amber-200',
  MISCONCEPTION: 'text-orange-600 bg-orange-50 border-orange-200',
  HOURS_CHANGE: 'text-blue-600 bg-blue-50 border-blue-200',
  FALLING_BEHIND: 'text-red-600 bg-red-50 border-red-200',
}[trigger] || 'text-indigo-600 bg-indigo-50 border-indigo-200');

const AdaptationHistory = ({ events = [], compact = false }) => {
  if (!events.length) {
    return (
      <div className={`rounded-xl border border-gray-100 bg-gray-50 p-4 ${compact ? '' : ''}`}>
        <p className="text-xs text-gray-400 text-center">No adaptations yet. Start learning and your path will adapt to you!</p>
      </div>
    );
  }

  const displayEvents = compact ? events.slice(0, 4) : events;

  return (
    <div className="space-y-2">
      {displayEvents.map((evt, i) => (
        <div
          key={evt.event_id || i}
          className="flex items-start gap-3 p-3 rounded-xl border border-gray-100 bg-white hover:border-gray-200 transition-colors"
        >
          {/* Icon */}
          <span className={`flex-shrink-0 inline-flex items-center justify-center w-7 h-7 rounded-full text-sm border ${triggerColor(evt.trigger)}`}>
            {triggerIcon(evt.trigger)}
          </span>

          {/* Content */}
          <div className="flex-grow min-w-0">
            <p className={`text-xs font-semibold ${compact ? 'line-clamp-1' : ''}`}>
              {evt.event_type?.replace(/_/g, ' ')}
            </p>
            <p className={`text-xs text-gray-500 ${compact ? 'line-clamp-1' : 'line-clamp-2'} mt-0.5`}>
              {evt.explanation || evt.reason || 'Path updated'}
            </p>
          </div>

          {/* Timestamp */}
          <span className="flex-shrink-0 text-[10px] text-gray-300 mt-0.5">
            {evt.timestamp ? new Date(evt.timestamp).toLocaleDateString('en-IN', { month: 'short', day: 'numeric' }) : ''}
          </span>
        </div>
      ))}
    </div>
  );
};

export default AdaptationHistory;
