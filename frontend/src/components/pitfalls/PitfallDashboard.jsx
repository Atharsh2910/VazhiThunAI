import React, { useEffect, useState } from 'react';
import { getLearnerPitfalls } from '../../api/pitfalls';
import { Link } from 'react-router-dom';
import Button from '../common/Button';

const severityColors = {
  high: { dot: 'bg-red-500', badge: 'bg-red-100 text-red-700', border: 'border-red-200' },
  medium: { dot: 'bg-yellow-500', badge: 'bg-yellow-100 text-yellow-700', border: 'border-yellow-200' },
  low: { dot: 'bg-blue-400', badge: 'bg-blue-100 text-blue-700', border: 'border-blue-200' },
};

const statusLabels = {
  DETECTED: { text: 'Detected', bg: 'bg-orange-100 text-orange-700' },
  REMEDIATION: { text: 'In Remediation', bg: 'bg-blue-100 text-blue-700' },
  VERIFICATION: { text: 'Verification', bg: 'bg-purple-100 text-purple-700' },
  UNRESOLVED: { text: 'Unresolved', bg: 'bg-red-100 text-red-700' },
  RESOLVED: { text: 'Resolved', bg: 'bg-green-100 text-green-700' },
};

const PitfallDashboard = ({ learnerId, compact = false }) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!learnerId) { setLoading(false); return; }
    getLearnerPitfalls(learnerId)
      .then(res => setData(res.data?.data))
      .catch(() => setError('Could not load pitfall data.'))
      .finally(() => setLoading(false));
  }, [learnerId]);

  if (loading) return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-1/3 mb-4"></div>
      <div className="space-y-3">
        <div className="h-12 bg-gray-100 rounded"></div>
        <div className="h-12 bg-gray-100 rounded"></div>
      </div>
    </div>
  );

  if (error || !data) return null;

  const { active_pitfalls, resolved_pitfalls, stats } = data;
  const showActive = compact ? active_pitfalls.slice(0, 2) : active_pitfalls;

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">🧠</span>
          <h2 className="text-lg font-bold text-gray-900">Learning Pitfalls</h2>
        </div>
        <div className="flex items-center gap-3 text-sm text-gray-500">
          <span className="font-semibold text-red-600">{stats.active_count}</span> active ·
          <span className="font-semibold text-green-600 ml-1">{stats.resolved_count}</span> resolved
        </div>
      </div>

      <div className="p-6 space-y-5">
        {/* Stats row */}
        <div className="grid grid-cols-3 gap-3">
          <div className="text-center bg-gray-50 rounded-lg py-3 px-2">
            <p className="text-2xl font-bold text-gray-900">{stats.total_detected}</p>
            <p className="text-xs text-gray-500 mt-0.5">Total Detected</p>
          </div>
          <div className="text-center bg-red-50 rounded-lg py-3 px-2">
            <p className="text-2xl font-bold text-red-600">{stats.active_count}</p>
            <p className="text-xs text-gray-500 mt-0.5">Active</p>
          </div>
          <div className="text-center bg-green-50 rounded-lg py-3 px-2">
            <p className="text-2xl font-bold text-green-600">{stats.resolved_count}</p>
            <p className="text-xs text-gray-500 mt-0.5">Resolved</p>
          </div>
        </div>

        {/* Active Pitfalls */}
        {showActive.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Active</h3>
            <div className="space-y-2">
              {showActive.map((p) => {
                const sc = severityColors[p.severity] || severityColors.medium;
                const sl = statusLabels[p.status] || statusLabels.DETECTED;
                return (
                  <div
                    key={p.pitfall_id}
                    className={`flex items-center justify-between p-3 rounded-lg border ${sc.border} bg-white hover:shadow-sm transition-shadow`}
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <div className={`w-2.5 h-2.5 rounded-full flex-shrink-0 ${sc.dot}`}></div>
                      <div className="min-w-0">
                        <p className="font-medium text-gray-800 text-sm truncate">{p.title}</p>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className={`text-xs px-2 py-0.5 rounded-full ${sl.bg} font-medium`}>
                            {sl.text}
                          </span>
                          <span className="text-xs text-gray-400">{p.concept_name}</span>
                        </div>
                      </div>
                    </div>
                    <Link to={`/pitfalls/${p.pitfall_id}`}>
                      <Button variant="outline" className="text-xs py-1 px-3 ml-3 flex-shrink-0">
                        Fix
                      </Button>
                    </Link>
                  </div>
                );
              })}
            </div>
            {compact && active_pitfalls.length > 2 && (
              <Link to="/pitfalls" className="block text-center text-sm text-blue-600 hover:text-blue-700 mt-3">
                +{active_pitfalls.length - 2} more pitfalls →
              </Link>
            )}
          </div>
        )}

        {/* Resolved Pitfalls */}
        {!compact && resolved_pitfalls.length > 0 && (
          <div>
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Resolved</h3>
            <div className="space-y-2">
              {resolved_pitfalls.map((p) => (
                <div
                  key={p.pitfall_id}
                  className="flex items-center gap-3 p-3 rounded-lg bg-green-50 border border-green-100 opacity-75"
                >
                  <span className="text-green-600 font-bold text-lg flex-shrink-0">✓</span>
                  <div>
                    <p className="font-medium text-gray-700 text-sm">{p.title}</p>
                    <p className="text-xs text-gray-400">{p.concept_name}</p>
                  </div>
                  <span className="ml-auto text-xs text-green-600 font-medium">Resolved</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {active_pitfalls.length === 0 && resolved_pitfalls.length === 0 && (
          <div className="text-center py-6 text-gray-400">
            <p className="text-3xl mb-2">🎯</p>
            <p className="text-sm">No pitfalls detected yet. Complete some concept checks to get started.</p>
          </div>
        )}

        {!compact && (
          <div className="pt-2 border-t border-gray-100">
            <Link
              to="/pitfalls/analytics"
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              📊 View population-level insights →
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default PitfallDashboard;
