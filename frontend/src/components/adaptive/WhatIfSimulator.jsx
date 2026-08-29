import React, { useState } from 'react';
import { adaptiveApi } from '../../api/adaptive';

const DEMO_LEARNER_ID = 'LRN0001';

const WhatIfSimulator = ({ learnerId = DEMO_LEARNER_ID, currentState, onApply, onClose }) => {
  const [scenarios, setScenarios] = useState(null);
  const [loading, setLoading] = useState(false);
  const [applying, setApplying] = useState(null);
  const [applied, setApplied] = useState(null);
  const [customHours, setCustomHours] = useState(currentState?.weekly_hours || 8);
  const [customDeadline, setCustomDeadline] = useState(currentState?.deadline_weeks || 20);
  const [customResult, setCustomResult] = useState(null);

  const loadScenarios = async () => {
    setLoading(true);
    try {
      const res = await adaptiveApi.simulateFaster(learnerId);
      setScenarios(res.data?.data);
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const runCustomSim = async () => {
    setLoading(true);
    try {
      const res = await adaptiveApi.simulate(learnerId, customHours, customDeadline, 'keep');
      setCustomResult(res.data?.data);
    } catch (err) {
      console.error('Custom simulation failed:', err);
    } finally {
      setLoading(false);
    }
  };

  const applyOption = async (option) => {
    setApplying(option.option_key);
    try {
      const params = option.apply_params || { weekly_hours: customHours, optional_policy: 'keep' };
      const res = await adaptiveApi.applySimulation(
        learnerId,
        option.option_key,
        params.weekly_hours,
        params.optional_policy || 'keep'
      );
      setApplied({ option, result: res.data?.data });
      if (onApply) onApply(res.data?.data);
    } catch (err) {
      console.error('Apply failed:', err);
    } finally {
      setApplying(null);
    }
  };

  const feasibilityBadge = (feasible) => {
    if (feasible === null || feasible === undefined) {
      return <span className="text-xs bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full font-medium">⚙ No data</span>;
    }
    return feasible
      ? <span className="text-xs bg-emerald-100 text-emerald-700 px-2 py-0.5 rounded-full font-medium">✓ Feasible</span>
      : <span className="text-xs bg-red-100 text-red-700 px-2 py-0.5 rounded-full font-medium">✗ Too tight</span>;
  };

  const formatWeeks = (w) => {
    if (w === null || w === undefined) return '—';
    return `${w.toFixed(1)} weeks`;
  };

  const noPathData = scenarios && scenarios.current_plan?.error === 'no_path_data';

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center text-xl">📊</div>
            <div>
              <h2 className="text-lg font-bold text-gray-900">What-If Simulator</h2>
              <p className="text-xs text-gray-500">Explore options before committing to any change</p>
            </div>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-2xl">×</button>
        </div>

        {applied ? (
          <div className="text-center py-8">
            <div className="text-5xl mb-3">✅</div>
            <h3 className="text-lg font-bold text-gray-900 mb-2">Your roadmap has been updated</h3>
            <p className="text-sm text-gray-500 mb-2">
              Projected completion: <strong>{applied.result?.new_projected_weeks?.toFixed(1)} weeks</strong>
            </p>
            <button onClick={onClose} className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-xl text-sm font-semibold hover:bg-indigo-700 transition-colors">
              View updated path
            </button>
          </div>
        ) : (
          <>
            {/* Custom input */}
            <div className="bg-gray-50 rounded-xl p-4 mb-4 border border-gray-100">
              <p className="text-sm font-semibold text-gray-700 mb-3">Custom scenario</p>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="text-xs text-gray-500 block mb-1">Weekly hours</label>
                  <input
                    type="number" min="1" max="40" step="0.5"
                    value={customHours}
                    onChange={(e) => setCustomHours(parseFloat(e.target.value))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  />
                </div>
                <div>
                  <label className="text-xs text-gray-500 block mb-1">Deadline (weeks)</label>
                  <input
                    type="number" min="4" max="52" step="1"
                    value={customDeadline}
                    onChange={(e) => setCustomDeadline(parseFloat(e.target.value))}
                    className="w-full border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300"
                  />
                </div>
              </div>
              <button
                onClick={runCustomSim}
                disabled={loading}
                className="mt-3 px-4 py-2 bg-indigo-50 border border-indigo-200 text-indigo-700 rounded-lg text-xs font-medium hover:bg-indigo-100 transition-colors"
              >
                {loading ? 'Calculating...' : 'Run simulation'}
              </button>
              {customResult && (
                <div className="mt-3 p-3 bg-white rounded-lg border border-gray-100 text-sm">
                  {customResult.error ? (
                    <p className="text-amber-600 text-xs">{customResult.message}</p>
                  ) : (
                    <div className="flex items-center justify-between">
                      <div>
                        <span className="text-gray-500">Projected: </span>
                        <strong>{formatWeeks(customResult.projected_weeks)}</strong>
                        <span className="text-gray-400 mx-2">·</span>
                        <span className="text-gray-500">{customResult.remaining_hours ?? '—'} hrs remaining</span>
                      </div>
                      {feasibilityBadge(customResult.feasible)}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Pre-built scenarios */}
            {!scenarios ? (
              <button
                onClick={loadScenarios}
                disabled={loading}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold text-sm hover:opacity-90 transition-opacity"
              >
                {loading ? 'Generating scenarios...' : '⚡ Show faster path options'}
              </button>
            ) : noPathData ? (
              <div className="rounded-xl border border-amber-200 bg-amber-50 p-5 text-center">
                <p className="text-2xl mb-2">⚙️</p>
                <p className="text-sm font-semibold text-amber-800">No path data yet</p>
                <p className="text-xs text-amber-600 mt-1 leading-relaxed">
                  Run <code className="bg-amber-100 px-1 rounded">python -m app.scripts.seed_adaptive</code> in your backend
                  terminal to generate the ML Engineer roadmap for LRN0001.
                </p>
              </div>
            ) : (
              <div>
                {/* Current plan */}
                <div className="p-3 rounded-xl border-2 border-gray-200 bg-gray-50 mb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-xs font-semibold text-gray-500">CURRENT PLAN</p>
                      <p className="text-sm font-bold text-gray-800 mt-0.5">
                        {scenarios.current_plan?.weekly_hours} hrs/week · {formatWeeks(scenarios.current_plan?.projected_weeks)}
                      </p>
                    </div>
                    {feasibilityBadge(scenarios.current_plan?.feasible)}
                  </div>
                </div>

                {/* Options */}
                {(scenarios.options || []).map((opt) => (
                  <div key={opt.option_key} className="p-4 rounded-xl border-2 border-indigo-100 bg-white hover:border-indigo-300 transition-colors mb-3">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <p className="text-xs font-semibold text-indigo-600">OPTION {opt.option_key}</p>
                        <p className="text-sm font-bold text-gray-800 mt-0.5">{opt.label}</p>
                        <p className="text-xs text-gray-500 mt-1">
                          {formatWeeks(opt.projected_weeks)}
                          {opt.removed_optional_items > 0 && ` · ${opt.removed_optional_items} optional items removed`}
                        </p>
                      </div>
                      <div className="flex flex-col items-end gap-2">
                        {feasibilityBadge(opt.feasible)}
                        <button
                          id={`apply-option-${opt.option_key}`}
                          onClick={() => applyOption(opt)}
                          disabled={applying !== null || opt.projected_weeks === null}
                          className="text-xs px-3 py-1.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors disabled:opacity-50"
                        >
                          {applying === opt.option_key ? 'Applying...' : 'Apply'}
                        </button>
                      </div>
                    </div>
                  </div>
                ))}

                <button
                  onClick={onClose}
                  className="w-full py-2.5 border border-gray-200 text-gray-600 rounded-xl text-sm hover:bg-gray-50 transition-colors"
                >
                  Keep current plan
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default WhatIfSimulator;
