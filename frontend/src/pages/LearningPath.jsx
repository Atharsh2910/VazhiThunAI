import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import FeedbackButtons from '../components/adaptive/FeedbackButtons';
import AdaptiveStatusCard from '../components/adaptive/AdaptiveStatusCard';
import AdaptationNotification from '../components/adaptive/AdaptationNotification';
import PathDiff from '../components/adaptive/PathDiff';
import WhatIfSimulator from '../components/adaptive/WhatIfSimulator';
import { adaptiveApi } from '../api/adaptive';

const DEMO_LEARNER_ID = 'LRN0001';

const STATUS_CONFIG = {
  completed:    { dot: 'bg-emerald-500 border-emerald-500', badge: 'bg-emerald-100 text-emerald-800', label: 'Completed' },
  mastered_skip:{ dot: 'bg-emerald-400 border-emerald-400', badge: 'bg-emerald-50 text-emerald-600', label: 'Mastered ✓' },
  in_progress:  { dot: 'bg-blue-500 border-blue-500', badge: 'bg-blue-100 text-blue-800', label: 'In Progress' },
  remediation:  { dot: 'bg-orange-500 border-orange-500', badge: 'bg-orange-100 text-orange-800', label: '⚠ Remediation' },
  verification: { dot: 'bg-purple-500 border-purple-500', badge: 'bg-purple-100 text-purple-800', label: '🔍 Verify' },
  planned:      { dot: 'bg-gray-200 border-gray-300', badge: 'bg-gray-100 text-gray-500', label: 'Planned' },
  blocked:      { dot: 'bg-red-300 border-red-300', badge: 'bg-red-100 text-red-600', label: 'Blocked' },
};

const ITEM_TYPE_ICONS = {
  resource:     '📘',
  remediation:  '🔧',
  verification: '🔍',
  project:      '🏗',
};

const LearningPath = () => {
  const [pathData, setPathData] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [notification, setNotification] = useState(null);
  const [pathDiff, setPathDiff] = useState(null);
  const [showSimulator, setShowSimulator] = useState(false);
  const [completing, setCompleting] = useState(null);

  const loadPath = useCallback(async () => {
    try {
      const [pathRes, statusRes] = await Promise.all([
        adaptiveApi.getPath(DEMO_LEARNER_ID),
        adaptiveApi.getStatus(DEMO_LEARNER_ID),
      ]);
      setPathData(pathRes.data?.data);
      setStatus(statusRes.data?.data);
      setError(null);
    } catch (err) {
      setError('Could not load your learning path. Is the backend running?');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadPath(); }, [loadPath]);

  const handleAdaptation = useCallback(async (adaptationResult) => {
    if (!adaptationResult || !adaptationResult.success) return;
    setNotification(adaptationResult);
    // Fetch diff then reload path
    try {
      const diffRes = await adaptiveApi.getPathDiff(DEMO_LEARNER_ID);
      if (diffRes.data?.data?.has_diff) {
        setPathDiff(diffRes.data.data);
      }
    } catch (_) {}
    await loadPath();
  }, [loadPath]);

  const handleComplete = useCallback(async (itemId) => {
    setCompleting(itemId);
    try {
      await adaptiveApi.completeItem(DEMO_LEARNER_ID, itemId);
      await loadPath();
    } catch (err) {
      console.error('Complete failed:', err);
    } finally {
      setCompleting(null);
    }
  }, [loadPath]);

  const isActive = (item) =>
    ['in_progress', 'remediation', 'verification'].includes(item.status);
  const isLocked = (item) => item.status === 'planned' || item.status === 'blocked';

  const path = pathData?.current_path || [];

  // Fallback static path for demo when backend not ready
  const fallbackPath = [
    { id: 'f1', item_type: 'resource', stage_title: 'Python for ML', title: 'Python Programming Basics', skill_id: 'SK001', status: 'completed', required: true, phase: 'Foundation', estimated_minutes: 300 },
    { id: 'f2', item_type: 'resource', stage_title: 'Statistics Foundations', title: 'Statistics & Probability', skill_id: 'SK011', status: 'in_progress', required: true, phase: 'Foundation', estimated_minutes: 480 },
    { id: 'f3', item_type: 'resource', stage_title: 'ML Fundamentals', title: 'Machine Learning Basics', skill_id: 'SK021', status: 'planned', required: true, phase: 'Core ML', estimated_minutes: 600 },
    { id: 'f4', item_type: 'resource', stage_title: 'Supervised Learning', title: 'Supervised Learning Deep Dive', skill_id: 'SK024', status: 'planned', required: true, phase: 'Advanced ML', estimated_minutes: 480 },
    { id: 'f5', item_type: 'resource', stage_title: 'Deep Learning', title: 'Neural Networks & Deep Learning', skill_id: 'SK021', status: 'planned', required: false, phase: 'Specialization', estimated_minutes: 720 },
    { id: 'f6', item_type: 'resource', stage_title: 'MLOps', title: 'MLOps & Model Deployment', skill_id: 'SK030', status: 'planned', required: true, phase: 'ML Engineering', estimated_minutes: 540 },
    { id: 'f7', item_type: 'project', stage_title: 'Capstone Project', title: 'ML Engineering Capstone', skill_id: null, status: 'planned', required: true, phase: 'Capstone', estimated_minutes: 1200 },
  ];

  const displayPath = path.length > 0 ? path : fallbackPath;
  const usingFallback = path.length === 0;

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-1">Your ML Engineer Path</h1>
        <p className="text-gray-500 text-sm">
          A personalized, adaptive roadmap. Your path evolves as you learn.
        </p>
      </div>

      {/* Adaptive Status */}
      {status && (
        <AdaptiveStatusCard status={status} onOpenSimulator={() => setShowSimulator(true)} />
      )}

      {/* Error banner */}
      {error && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-3 text-sm text-amber-700 flex items-center gap-2">
          <span>⚠</span>
          <span>{error} Showing demo path.</span>
        </div>
      )}

      {/* Loading */}
      {loading && (
        <div className="space-y-3">
          {[1,2,3].map(i => (
            <div key={i} className="h-24 bg-gray-100 rounded-2xl animate-pulse" />
          ))}
        </div>
      )}

      {/* Path timeline */}
      {!loading && (
        <div className="relative border-l-2 border-gray-200 ml-4 space-y-0 py-4">
          {displayPath.map((item, idx) => {
            const cfg = STATUS_CONFIG[item.status] || STATUS_CONFIG.planned;
            const active = isActive(item);
            const locked = isLocked(item);
            const icon = ITEM_TYPE_ICONS[item.item_type] || '📘';
            const isOptional = !item.required;

            return (
              <div key={item.id} className="relative pl-8 mb-4">
                {/* Timeline dot */}
                <div className={`absolute -left-[9px] top-3 h-4 w-4 rounded-full border-2 ${cfg.dot}`} />

                <Card className={`transition-all duration-300 ${
                  active ? 'border-blue-200 shadow-md ring-1 ring-blue-100' :
                  locked ? 'opacity-55' : ''
                } ${item.item_type === 'remediation' ? 'border-l-4 border-orange-300' :
                   item.item_type === 'verification' ? 'border-l-4 border-purple-300' : ''}`}>

                  <div className="flex justify-between items-start gap-3">
                    <div className="flex-grow">
                      {/* Phase label */}
                      {(idx === 0 || displayPath[idx-1]?.phase !== item.phase) && (
                        <span className="text-[10px] uppercase tracking-widest text-gray-400 font-semibold mb-1 block">
                          {item.phase}
                        </span>
                      )}

                      {/* Title */}
                      <h3 className="text-base font-semibold text-gray-900 flex items-center gap-2">
                        <span>{icon}</span>
                        <span>{item.stage_title || item.title}</span>
                        {isOptional && (
                          <span className="text-[10px] bg-gray-100 text-gray-400 px-2 py-0.5 rounded-full font-medium">optional</span>
                        )}
                      </h3>

                      {/* Resource title if different from stage */}
                      {item.stage_title && item.title !== item.stage_title && (
                        <p className="text-xs text-gray-500 mt-0.5">{item.title}</p>
                      )}

                      {/* Meta */}
                      <div className="flex items-center gap-3 mt-1 text-xs text-gray-400">
                        {item.provider && <span>{item.provider}</span>}
                        {item.estimated_minutes && (
                          <span>~{Math.round(item.estimated_minutes / 60 * 10) / 10} hrs</span>
                        )}
                        {item.skill_id && item.status !== 'planned' && (
                          <Link
                            to={`/pitfalls/check/${item.skill_id}`}
                            className="text-indigo-500 hover:text-indigo-700 font-medium flex items-center gap-1"
                          >
                            ⚡ Concept check
                          </Link>
                        )}
                      </div>

                      {/* Remediation / Verification context */}
                      {item.item_type === 'remediation' && item.concept_name && (
                        <p className="text-xs text-orange-600 mt-1 font-medium">
                          🔧 Remediation for: {item.concept_name}
                        </p>
                      )}
                      {item.item_type === 'verification' && (
                        <p className="text-xs text-purple-600 mt-1 font-medium">
                          🔍 Verification check — complete to continue
                        </p>
                      )}

                      {/* Feedback buttons for active items */}
                      {active && (
                        <FeedbackButtons
                          learnerId={DEMO_LEARNER_ID}
                          itemId={item.id}
                          onAdaptation={handleAdaptation}
                        />
                      )}
                    </div>

                    {/* Right actions */}
                    <div className="flex flex-col items-end gap-2 flex-shrink-0">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${cfg.badge}`}>
                        {cfg.label}
                      </span>

                      {active && (
                        <Button
                          id={`complete-${item.id}`}
                          variant="primary"
                          className="text-xs py-1 px-3"
                          onClick={() => handleComplete(item.id)}
                          disabled={completing === item.id}
                        >
                          {completing === item.id ? '...' : 'Mark Complete'}
                        </Button>
                      )}
                    </div>
                  </div>
                </Card>
              </div>
            );
          })}

          {/* End marker */}
          <div className="relative pl-8">
            <div className="absolute -left-[9px] top-3 h-4 w-4 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 border-2 border-indigo-500" />
            <div className="py-3 pl-2">
              <p className="text-sm font-semibold text-gray-700">🎉 ML Engineer — Goal Achieved</p>
            </div>
          </div>
        </div>
      )}

      {/* Footer links */}
      <div className="flex items-center gap-4 pl-4">
        <Link to="/pitfalls" className="text-sm text-indigo-600 hover:text-indigo-700 font-medium">
          🧠 View detected pitfalls →
        </Link>
        <button
          onClick={() => setShowSimulator(true)}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          📊 Open simulator
        </button>
      </div>

      {/* Modals and notifications */}
      {pathDiff && (
        <PathDiff
          diff={pathDiff}
          onDismiss={() => { setPathDiff(null); loadPath(); }}
        />
      )}

      {showSimulator && (
        <WhatIfSimulator
          learnerId={DEMO_LEARNER_ID}
          currentState={pathData}
          onApply={async (result) => {
            setShowSimulator(false);
            setNotification({ success: true, adaptation_type: 'APPLIED', explanation: `Your roadmap has been updated. New projected completion: ${result?.new_projected_weeks?.toFixed(1)} weeks.` });
            await loadPath();
          }}
          onClose={() => setShowSimulator(false)}
        />
      )}

      <AdaptationNotification
        adaptation={notification}
        onDismiss={() => setNotification(null)}
      />
    </div>
  );
};

export default LearningPath;
