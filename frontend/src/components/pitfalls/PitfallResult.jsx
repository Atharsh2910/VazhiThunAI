import React from 'react';
import Button from '../common/Button';

const RESULT_CONFIG = {
  MASTERY: {
    icon: '✓',
    iconBg: 'bg-green-100',
    iconColor: 'text-green-600',
    border: 'border-green-200',
    headerBg: 'bg-green-50',
    badge: 'bg-green-100 text-green-700',
    title: 'Concept looks solid!',
    subtitle: "You demonstrated a good understanding of this concept.",
  },
  KNOWLEDGE_GAP: {
    icon: '⚠',
    iconBg: 'bg-yellow-100',
    iconColor: 'text-yellow-600',
    border: 'border-yellow-200',
    headerBg: 'bg-yellow-50',
    badge: 'bg-yellow-100 text-yellow-700',
    title: 'Knowledge gap',
    subtitle: "You may need a little more practice with this concept.",
  },
  MISCONCEPTION: {
    icon: '🚨',
    iconBg: 'bg-red-100',
    iconColor: 'text-red-600',
    border: 'border-red-200',
    headerBg: 'bg-red-50',
    badge: 'bg-red-100 text-red-700',
    title: 'Possible misconception detected',
    subtitle: "Your answer suggests a common misconception about this concept.",
  },
  UNCERTAINTY: {
    icon: '?',
    iconBg: 'bg-blue-100',
    iconColor: 'text-blue-600',
    border: 'border-blue-200',
    headerBg: 'bg-blue-50',
    badge: 'bg-blue-100 text-blue-700',
    title: 'Needs more review',
    subtitle: "This concept needs a bit more attention.",
  },
};

const PitfallResult = ({ result, onContinue, onFixThis, onPractice }) => {
  const classification = result?.classification || 'KNOWLEDGE_GAP';
  const config = RESULT_CONFIG[classification] || RESULT_CONFIG.KNOWLEDGE_GAP;
  const pitfall = result?.pitfall;
  const question = result?.question;

  return (
    <div className={`bg-white rounded-xl border-2 ${config.border} shadow-lg overflow-hidden`}>
      {/* Header */}
      <div className={`${config.headerBg} px-6 py-5 border-b ${config.border}`}>
        <div className="flex items-start gap-4">
          <div className={`${config.iconBg} ${config.iconColor} w-12 h-12 rounded-full flex items-center justify-center text-xl font-bold flex-shrink-0`}>
            {config.icon}
          </div>
          <div>
            <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wide ${config.badge} mb-1`}>
              {classification.replace('_', ' ')}
            </span>
            <h2 className="text-xl font-bold text-gray-900">{config.title}</h2>
            <p className="text-gray-600 text-sm mt-1">{config.subtitle}</p>
          </div>
        </div>
      </div>

      {/* LLM Explanation */}
      {result?.explanation && (
        <div className="px-6 py-5">
          <p className="text-gray-700 leading-relaxed text-sm">{result.explanation}</p>
        </div>
      )}

      {/* Misconception breakdown (only for MISCONCEPTION) */}
      {classification === 'MISCONCEPTION' && pitfall && (
        <div className="px-6 pb-5 space-y-4">
          <div className="rounded-lg bg-red-50 border border-red-100 p-4">
            <div className="space-y-3 text-sm">
              <div>
                <p className="font-semibold text-red-700 mb-1">What you may have thought</p>
                <p className="text-gray-700">{pitfall.misconception}</p>
              </div>
              <div className="border-t border-red-100 pt-3">
                <p className="font-semibold text-green-700 mb-1">The correct mental model</p>
                <p className="text-gray-700">{pitfall.correct_mental_model}</p>
              </div>
            </div>
          </div>

          {result?.misconception_hint && (
            <div className="rounded-lg bg-orange-50 border border-orange-100 p-3">
              <p className="text-xs text-orange-700 font-medium">Why your choice indicated this</p>
              <p className="text-sm text-gray-700 mt-1">{result.misconception_hint}</p>
            </div>
          )}
        </div>
      )}

      {/* Correct answer info for wrong answers */}
      {!result?.is_correct && question && (
        <div className="px-6 pb-4">
          <div className="rounded-lg bg-gray-50 border border-gray-200 p-3 text-sm">
            <span className="font-medium text-gray-700">Correct answer: </span>
            <span className="font-semibold text-blue-700">Option {question.correct_option}</span>
            {question.explanation && (
              <p className="text-gray-600 mt-1">{question.explanation}</p>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="px-6 pb-6 pt-2 border-t border-gray-100">
        {classification === 'MASTERY' && (
          <Button id="continue-btn" onClick={onContinue} className="w-full">
            Continue Learning →
          </Button>
        )}
        {classification === 'KNOWLEDGE_GAP' && (
          <div className="flex gap-3">
            <Button id="fix-this-btn" onClick={onFixThis} className="flex-1">
              Learn This First
            </Button>
            <Button id="continue-anyway-btn" variant="secondary" onClick={onContinue}>
              Continue Anyway
            </Button>
          </div>
        )}
        {(classification === 'MISCONCEPTION') && (
          <div className="space-y-3">
            <p className="text-sm text-gray-600 font-medium">Recommended next action:</p>
            <div className="flex gap-3">
              <Button id="fix-misconception-btn" onClick={onFixThis} className="flex-1 bg-red-600 hover:bg-red-700">
                🔧 Fix This Now
              </Button>
              <Button id="practice-btn" variant="outline" onClick={onPractice}>
                Practice
              </Button>
            </div>
            <button
              id="continue-anyway-misconception-btn"
              onClick={onContinue}
              className="text-sm text-gray-400 hover:text-gray-600 w-full text-center transition-colors"
            >
              Continue anyway (not recommended)
            </button>
          </div>
        )}
        {classification === 'UNCERTAINTY' && (
          <div className="flex gap-3">
            <Button id="fix-uncertainty-btn" onClick={onFixThis} className="flex-1">
              Review Concept
            </Button>
            <Button id="continue-uncertainty-btn" variant="secondary" onClick={onContinue}>
              Continue
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default PitfallResult;
