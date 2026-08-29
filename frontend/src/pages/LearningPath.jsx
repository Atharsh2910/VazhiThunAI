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
  completed:    { dot: 'bg-emerald-500 border-emerald-600', badge: 'bg-emerald-50 text-emerald-700 border border-emerald-200', label: 'Completed' },
  mastered_skip:{ dot: 'bg-emerald-400 border-emerald-500', badge: 'bg-emerald-50 text-emerald-600 border border-emerald-150', label: 'Mastered ✓' },
  in_progress:  { dot: 'bg-blue-600 border-blue-600 ring-4 ring-blue-50', badge: 'bg-blue-50 text-blue-700 border border-blue-200', label: 'In Progress' },
  remediation:  { dot: 'bg-orange-500 border-orange-500', badge: 'bg-orange-50 text-orange-700 border border-orange-200', label: '⚠ Remediation' },
  verification: { dot: 'bg-purple-500 border-purple-500', badge: 'bg-purple-50 text-purple-700 border border-purple-200', label: '🔍 Verify' },
  planned:      { dot: 'bg-slate-200 border-slate-300', badge: 'bg-slate-50 text-slate-500 border border-slate-200', label: 'Planned' },
  blocked:      { dot: 'bg-red-400 border-red-400', badge: 'bg-red-50 text-red-600 border border-red-200', label: 'Blocked' },
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

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Your ML Engineer Path</h1>
        <p className="text-sm text-slate-500">
          A personalized, adaptive roadmap. Your path evolves dynamically as you learn.
        </p>
      </div>

      {/* Adaptive Status summary */}
      {status && (
        <AdaptiveStatusCard status={status} onOpenSimulator={() => setShowSimulator(true)} />
      )}

      {/* Error banner */}
      {error && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 flex items-center gap-2 font-medium">
          <span>⚠️</span>
          <span>{error} Showing demo path.</span>
        </div>
      )}

      {/* Loading animation */}
      {loading && (
        <div className="space-y-4">
          {[1,2,3].map(i => (
            <div key={i} className="h-24 bg-slate-100 rounded-xl border border-slate-200 animate-pulse" />
          ))}
        </div>
      )}

      {/* Timeline view */}
      {!loading && (
        <div className="relative border-l border-slate-200 ml-4 space-y-0 py-4">
          {displayPath.map((item, idx) => {
            const cfg = STATUS_CONFIG[item.status] || STATUS_CONFIG.planned;
            const active = isActive(item);
            const locked = isLocked(item);
            const icon = ITEM_TYPE_ICONS[item.item_type] || '📘';
            const isOptional = !item.required;

            return (
              <div key={item.id} className="relative pl-8 mb-6">
                {/* Timeline node dot */}
                <div className={`absolute -left-[4.5px] top-4 h-2.5 w-2.5 rounded-full ${cfg.dot}`} />

                <Card className={`transition-all duration-300 ${
                  active ? 'border-blue-400 ring-2 ring-blue-50' :
                  locked ? 'opacity-60 bg-slate-50/50' : ''
                } ${item.item_type === 'remediation' ? 'border-l-4 border-l-orange-400' :
                   item.item_type === 'verification' ? 'border-l-4 border-l-purple-400' : ''}`}>

                  <div className="flex justify-between items-start gap-4 flex-wrap sm:flex-nowrap">
                    <div className="flex-grow space-y-2">
                      {/* Phase subtitle */}
                      {(idx === 0 || displayPath[idx-1]?.phase !== item.phase) && (
                        <span className="text-[10px] uppercase tracking-widest text-slate-400 font-bold block mb-1">
                          {item.phase}
                        </span>
                      )}

                      {/* Header row */}
                      <h3 className="text-base font-bold text-slate-900 flex items-center gap-2">
                        <span>{icon}</span>
                        <span>{item.stage_title || item.title}</span>
                        {isOptional && (
                          <span className="text-[10px] bg-slate-100 text-slate-500 px-2 py-0.5 rounded-full font-semibold border border-slate-200">optional</span>
                        )}
                      </h3>

                      {/* Resource details */}
                      {item.stage_title && item.title !== item.stage_title && (
                        <p className="text-xs text-slate-500 font-medium">{item.title}</p>
                      )}

                      {/* Meta information line */}
                      <div className="flex items-center gap-3 text-xs text-slate-400 flex-wrap">
                        {item.provider && <span className="font-semibold text-slate-500">{item.provider}</span>}
                        {item.estimated_minutes && (
                          <span>~{Math.round(item.estimated_minutes / 60 * 10) / 10} hrs</span>
                        )}
                        {item.skill_id && item.status !== 'planned' && (
                          <Link
                            to={`/pitfalls/check/${item.skill_id}`}
                            className="text-blue-600 hover:text-blue-800 font-bold flex items-center gap-1.5"
                          >
                            ⚡ Concept check
                          </Link>
                        )}
                      </div>

                      {/* Special type callouts */}
                      {item.item_type === 'remediation' && item.concept_name && (
                        <p className="text-xs text-orange-600 font-semibold bg-orange-50 border border-orange-100 px-2.5 py-1 rounded-md inline-block">
                          🔧 Remediation loop for: {item.concept_name}
                        </p>
                      )}
                      {item.item_type === 'verification' && (
                        <p className="text-xs text-purple-600 font-semibold bg-purple-50 border border-purple-100 px-2.5 py-1 rounded-md inline-block">
                          🔍 Verification check required to unlock roadmap
                        </p>
                      )}

                      {/* Adaptation action buttons */}
                      {active && (
                        <div className="pt-2">
                          <FeedbackButtons
                            learnerId={DEMO_LEARNER_ID}
                            itemId={item.id}
                            onAdaptation={handleAdaptation}
                          />
                        </div>
                      )}
                    </div>

                    {/* Status badges and Primary complete actions */}
                    <div className="flex flex-row sm:flex-col items-center sm:items-end justify-between sm:justify-start w-full sm:w-auto gap-3.5 pt-2 sm:pt-0 border-t sm:border-t-0 border-slate-100">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold ${cfg.badge}`}>
                        {cfg.label}
                      </span>

                      {active && (
                        <Button
                          id={`complete-${item.id}`}
                          variant="primary"
                          className="text-xs py-1.5 px-3 rounded-md"
                          onClick={() => handleComplete(item.id)}
                          disabled={completing === item.id}
                        >
                          {completing === item.id ? 'Saving...' : 'Mark Complete'}
                        </Button>
                      )}
                    </div>
                  </div>
                </Card>
              </div>
            );
          })}

          {/* End Milestone */}
          <div className="relative pl-8">
            <div className="absolute -left-[5px] top-3.5 h-3 w-3 rounded-full bg-blue-600 ring-4 ring-blue-50" />
            <div className="py-2 pl-2">
              <p className="text-sm font-bold text-slate-800">🎉 ML Engineer Goals Achieved</p>
            </div>
          </div>
        </div>
      )}

      {/* Footer Navigation links */}
      <div className="flex items-center gap-5 pl-4 flex-wrap">
        <Link to="/pitfalls" className="text-xs font-bold text-blue-600 hover:text-blue-700">
          🧠 View detected pitfalls →
        </Link>
        <button
          onClick={() => setShowSimulator(true)}
          className="text-xs font-semibold text-slate-400 hover:text-slate-600 cursor-pointer"
        >
          📊 Open simulation panel
        </button>
      </div>

      {/* Simulator Modal overlays */}
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
