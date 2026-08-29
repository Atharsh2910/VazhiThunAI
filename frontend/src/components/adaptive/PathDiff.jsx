import React from 'react';

const PathDiff = ({ diff, onDismiss }) => {
  if (!diff || !diff.has_diff) return null;

  const oldItems = diff.old_path || [];
  const newItems = diff.new_path || [];

  // Build display lists using snapshots (arrays of IDs)
  // For compact display, just count changes
  const added = newItems.filter((id) => !oldItems.includes(id));
  const removed = oldItems.filter((id) => !newItems.includes(id));

  const triggerLabels = {
    TOO_HARD: 'You reported this resource was too difficult',
    TOO_EASY: 'You reported this resource was too easy',
    ALREADY_KNOWN: 'You claimed mastery of this topic',
    KNOWLEDGE_GAP: 'Your assessment revealed a knowledge gap',
    MISCONCEPTION: 'A misconception was detected in your response',
    HOURS_CHANGE: 'Your weekly study hours changed',
    DEADLINE_CHANGE: 'Your deadline was updated',
    FASTER_PATH: 'You requested a faster learning path',
    LIGHTER_PATH: 'You requested a lighter workload',
    FALLING_BEHIND: 'You were at risk of missing your deadline',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6">
        {/* Header */}
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-xl">
            🔄
          </div>
          <div>
            <h2 className="text-lg font-bold text-gray-900">Your Path Changed</h2>
            <p className="text-xs text-gray-500">
              {triggerLabels[diff.trigger] || 'An adaptation was applied to your path'}
            </p>
          </div>
        </div>

        {/* Change stats */}
        <div className="grid grid-cols-2 gap-3 mb-4">
          {added.length > 0 && (
            <div className="bg-emerald-50 rounded-xl p-3 border border-emerald-100">
              <p className="text-xs text-emerald-600 font-semibold">Added</p>
              <p className="text-2xl font-bold text-emerald-700">{added.length}</p>
              <p className="text-xs text-emerald-600">new item{added.length > 1 ? 's' : ''}</p>
            </div>
          )}
          {removed.length > 0 && (
            <div className="bg-red-50 rounded-xl p-3 border border-red-100">
              <p className="text-xs text-red-600 font-semibold">Removed</p>
              <p className="text-2xl font-bold text-red-700">{removed.length}</p>
              <p className="text-xs text-red-600">item{removed.length > 1 ? 's' : ''}</p>
            </div>
          )}
          {added.length === 0 && removed.length === 0 && (
            <div className="col-span-2 bg-blue-50 rounded-xl p-3 border border-blue-100">
              <p className="text-xs text-blue-600 font-semibold">Modified</p>
              <p className="text-xs text-blue-600 mt-0.5">A resource was replaced in your path</p>
            </div>
          )}
        </div>

        {/* Explanation */}
        <div className="bg-gray-50 rounded-xl p-4 mb-5 border border-gray-100">
          <p className="text-xs text-gray-500 font-semibold mb-1">Why?</p>
          <p className="text-sm text-gray-700 leading-relaxed">
            {diff.explanation || diff.reason || 'Your path was adapted to better match your current learning needs.'}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            id="path-diff-close"
            onClick={onDismiss}
            className="flex-1 py-2.5 px-4 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-colors"
          >
            Got it — show me my updated path
          </button>
        </div>
      </div>
    </div>
  );
};

export default PathDiff;
