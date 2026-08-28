import React, { useState } from 'react';
import ConfidenceSelector from './ConfidenceSelector';
import Button from '../common/Button';

const PitfallCheckCard = ({ checkData, onSubmit, onSkip, isLoading }) => {
  const [selectedOption, setSelectedOption] = useState(null);
  const [confidence, setConfidence] = useState(null);

  const { pitfall_title, concept_name, severity, question } = checkData;

  const severityColors = {
    high: 'bg-red-100 text-red-700 border-red-200',
    medium: 'bg-yellow-100 text-yellow-700 border-yellow-200',
    low: 'bg-green-100 text-green-700 border-green-200',
  };

  const handleSubmit = () => {
    if (!selectedOption || !confidence) return;
    onSubmit({
      questionId: question.question_id,
      selectedOption,
      confidence,
    });
  };

  const optionKeys = question ? Object.keys(question.options) : [];

  return (
    <div className="bg-white rounded-xl border border-blue-100 shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-6 py-4">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-2xl">⚡</span>
          <span className="text-white font-bold text-lg">Concept Check</span>
        </div>
        <p className="text-blue-100 text-sm">
          Before moving on, let's verify a key concept for your next step.
        </p>
      </div>

      {/* Concept badge */}
      <div className="px-6 pt-5 pb-0 flex items-center gap-3">
        <div className="flex-1">
          <span className="text-xs text-gray-500 uppercase tracking-wide font-semibold">Topic</span>
          <h2 className="text-xl font-bold text-gray-900 mt-0.5">{concept_name}</h2>
        </div>
        <span className={`px-3 py-1 rounded-full border text-xs font-semibold capitalize ${severityColors[severity] || severityColors.medium}`}>
          {severity} priority
        </span>
      </div>

      {/* Question */}
      {question && (
        <div className="px-6 py-5">
          <p className="text-gray-800 font-medium text-base leading-relaxed mb-5">
            {question.question_text}
          </p>

          {/* Options */}
          <div className="space-y-3">
            {optionKeys.map((key) => (
              <button
                key={key}
                id={`option-${key}`}
                onClick={() => setSelectedOption(key)}
                className={`
                  w-full text-left px-4 py-3 rounded-lg border-2 transition-all duration-200 text-sm
                  ${selectedOption === key
                    ? 'border-blue-500 bg-blue-50 text-blue-800 font-medium shadow-sm'
                    : 'border-gray-200 bg-gray-50 text-gray-700 hover:border-blue-300 hover:bg-blue-50/30'
                  }
                `}
              >
                <span className={`inline-flex items-center justify-center w-6 h-6 rounded-full mr-3 text-xs font-bold
                  ${selectedOption === key ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'}`}>
                  {key}
                </span>
                {question.options[key]}
              </button>
            ))}
          </div>

          <ConfidenceSelector value={confidence} onChange={setConfidence} />
        </div>
      )}

      {/* Actions */}
      <div className="px-6 pb-6 flex gap-3 pt-2 border-t border-gray-100 mt-2">
        <Button
          id="pitfall-submit-btn"
          onClick={handleSubmit}
          disabled={!selectedOption || !confidence || isLoading}
          className="flex-1"
        >
          {isLoading ? 'Evaluating...' : 'Submit Answer'}
        </Button>
        <Button
          id="pitfall-skip-btn"
          variant="secondary"
          onClick={onSkip}
          disabled={isLoading}
        >
          Skip
        </Button>
      </div>
    </div>
  );
};

export default PitfallCheckCard;
