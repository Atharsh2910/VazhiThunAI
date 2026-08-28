import React from 'react';

const labels = {
  1: 'Not sure at all',
  2: 'Slightly sure',
  3: 'Somewhat sure',
  4: 'Pretty confident',
  5: 'Very confident',
};

const ConfidenceSelector = ({ value, onChange }) => {
  return (
    <div className="mt-6">
      <p className="text-sm font-medium text-gray-700 mb-3">
        How confident are you in your answer?
      </p>
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map((level) => (
          <button
            key={level}
            id={`confidence-${level}`}
            onClick={() => onChange(level)}
            title={labels[level]}
            className={`
              w-10 h-10 rounded-full border-2 font-semibold text-sm transition-all duration-200
              ${value === level
                ? 'border-blue-600 bg-blue-600 text-white shadow-md scale-110'
                : 'border-gray-300 bg-white text-gray-600 hover:border-blue-400 hover:text-blue-600'
              }
            `}
          >
            {level}
          </button>
        ))}
      </div>
      {value && (
        <p className="text-xs text-blue-600 mt-2 font-medium">{labels[value]}</p>
      )}
    </div>
  );
};

export default ConfidenceSelector;
