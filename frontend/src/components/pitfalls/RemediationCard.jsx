import React from 'react';
import Button from '../common/Button';

const RemediationCard = ({ resource, pitfallTitle, explanation, remediation_text, onComplete, onSkip }) => {
  if (!resource && !explanation) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-6 text-center">
        <p className="text-gray-500">No remediation resource found, but here's a quick review:</p>
        <p className="text-gray-700 mt-2 text-sm">{remediation_text || explanation}</p>
        <Button id="remediation-done-btn" className="mt-4" onClick={onComplete}>
          Got it — Verify Understanding
        </Button>
      </div>
    );
  }

  const durationText = resource?.duration_minutes
    ? resource.duration_minutes < 60
      ? `${resource.duration_minutes} min`
      : `${Math.round(resource.duration_minutes / 60)} hr`
    : null;

  const resourceTypeIcons = {
    video: '🎬',
    article: '📄',
    course: '🎓',
    exercise: '💪',
    quiz: '📝',
  };

  return (
    <div className="bg-white rounded-xl border border-blue-100 shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
        <p className="text-indigo-100 text-xs uppercase tracking-wide font-semibold mb-1">
          Recommended remediation
        </p>
        <h2 className="text-white font-bold text-lg">Let's fix this misconception</h2>
      </div>

      {/* Concept explanation */}
      {(explanation || remediation_text) && (
        <div className="px-6 py-4 bg-indigo-50 border-b border-indigo-100">
          <p className="text-sm text-indigo-900 leading-relaxed">
            {explanation || remediation_text}
          </p>
        </div>
      )}

      {/* Resource card */}
      {resource && (
        <div className="px-6 py-5">
          <p className="text-xs text-gray-500 uppercase tracking-wide font-semibold mb-3">
            Study this resource to address the misconception
          </p>
          <div className="rounded-lg border-2 border-indigo-200 bg-indigo-50 p-4">
            <div className="flex items-start gap-3">
              <span className="text-2xl">
                {resourceTypeIcons[resource.resource_type?.toLowerCase()] || '📚'}
              </span>
              <div className="flex-1 min-w-0">
                <h3 className="font-semibold text-gray-900 text-base leading-tight">
                  {resource.title}
                </h3>
                <div className="flex flex-wrap items-center gap-2 mt-2">
                  {resource.provider && (
                    <span className="text-xs text-gray-500 bg-white rounded px-2 py-0.5 border border-gray-200">
                      {resource.provider}
                    </span>
                  )}
                  {resource.resource_type && (
                    <span className="text-xs text-indigo-600 bg-indigo-100 rounded px-2 py-0.5 capitalize">
                      {resource.resource_type}
                    </span>
                  )}
                  {durationText && (
                    <span className="text-xs text-gray-500 flex items-center gap-1">
                      ⏱ {durationText}
                    </span>
                  )}
                  {resource.quality_score && (
                    <span className="text-xs text-yellow-700 bg-yellow-50 rounded px-2 py-0.5">
                      ★ {(resource.quality_score * 10).toFixed(1)}/10
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="px-6 pb-6 pt-2 border-t border-gray-100 space-y-3">
        <Button id="remediation-complete-btn" onClick={onComplete} className="w-full">
          ✓ I've Reviewed This — Verify Understanding
        </Button>
        {onSkip && (
          <button
            id="remediation-skip-btn"
            onClick={onSkip}
            className="w-full text-sm text-gray-400 hover:text-gray-600 transition-colors"
          >
            Skip for now
          </button>
        )}
      </div>
    </div>
  );
};

export default RemediationCard;
