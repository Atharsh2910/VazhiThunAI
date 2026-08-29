import React, { useState } from 'react';
import { adaptiveApi } from '../../api/adaptive';

const FEEDBACK_OPTIONS = [
  { type: 'TOO_EASY', label: '👍 Too easy', color: 'bg-emerald-50 text-emerald-700 border-emerald-200 hover:bg-emerald-100' },
  { type: 'JUST_RIGHT', label: '✓ Just right', color: 'bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100' },
  { type: 'TOO_HARD', label: '😵 Too difficult', color: 'bg-red-50 text-red-700 border-red-200 hover:bg-red-100' },
  { type: 'ALREADY_KNOWN', label: '🔁 Already know this', color: 'bg-purple-50 text-purple-700 border-purple-200 hover:bg-purple-100' },
  { type: 'TOO_LONG', label: '⏱ Too long', color: 'bg-amber-50 text-amber-700 border-amber-200 hover:bg-amber-100' },
  { type: 'CONFUSING', label: '❓ Confusing', color: 'bg-orange-50 text-orange-700 border-orange-200 hover:bg-orange-100' },
];

const FeedbackButtons = ({ learnerId, itemId, onAdaptation }) => {
  const [loading, setLoading] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const handleFeedback = async (feedbackType) => {
    if (loading) return;
    setLoading(feedbackType);
    try {
      const res = await adaptiveApi.sendFeedback(learnerId, itemId, feedbackType);
      const result = res.data?.data;
      setSubmitted(true);
      if (onAdaptation && result) {
        onAdaptation(result);
      }
    } catch (err) {
      console.error('Feedback failed:', err);
    } finally {
      setLoading(null);
    }
  };

  if (submitted) {
    return (
      <p className="text-xs text-gray-400 italic mt-2">Feedback recorded ✓</p>
    );
  }

  return (
    <div className="mt-3">
      <p className="text-xs text-gray-500 mb-2 font-medium">How is this going?</p>
      <div className="flex flex-wrap gap-1.5">
        {FEEDBACK_OPTIONS.map(({ type, label, color }) => (
          <button
            key={type}
            id={`feedback-${type.toLowerCase()}-${itemId}`}
            onClick={() => handleFeedback(type)}
            disabled={loading !== null}
            className={`text-xs px-2.5 py-1 rounded-full border font-medium transition-all duration-200 ${color} ${
              loading === type ? 'opacity-60 cursor-wait' : 'cursor-pointer'
            }`}
          >
            {loading === type ? '...' : label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default FeedbackButtons;
