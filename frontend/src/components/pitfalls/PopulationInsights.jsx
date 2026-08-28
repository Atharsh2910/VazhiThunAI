import React, { useEffect, useState } from 'react';
import { getPitfallAnalytics } from '../../api/pitfalls';

const statusConfig = {
  confirmed: { label: 'Confirmed', bg: 'bg-red-100 text-red-700', bar: 'bg-red-500' },
  likely: { label: 'Likely', bg: 'bg-orange-100 text-orange-700', bar: 'bg-orange-500' },
  emerging: { label: 'Emerging', bg: 'bg-yellow-100 text-yellow-700', bar: 'bg-yellow-500' },
  insufficient_evidence: { label: 'Insufficient Evidence', bg: 'bg-gray-100 text-gray-500', bar: 'bg-gray-300' },
};

const PopulationInsights = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    getPitfallAnalytics()
      .then(res => setAnalytics(res.data?.data))
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
      <div className="animate-spin w-8 h-8 border-4 border-blue-200 border-t-blue-600 rounded-full mx-auto mb-3"></div>
      <p className="text-gray-500 text-sm">Loading population analytics…</p>
    </div>
  );

  const pitfalls = analytics?.pitfalls || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Population Insights</h1>
        <p className="text-gray-500 text-sm mt-1">
          Anonymised, aggregated data showing common misconceptions across all learners.
        </p>
      </div>

      {/* Summary stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Total Pitfalls Tracked', value: pitfalls.length },
          { label: 'Confirmed', value: pitfalls.filter(p => p.status === 'confirmed').length, color: 'text-red-600' },
          { label: 'Likely / Emerging', value: pitfalls.filter(p => ['likely', 'emerging'].includes(p.status)).length, color: 'text-orange-600' },
          { label: 'With Evidence', value: pitfalls.filter(p => p.total_attempts > 0).length, color: 'text-blue-600' },
        ].map((stat, i) => (
          <div key={i} className="bg-white rounded-xl border border-gray-200 p-4">
            <p className={`text-3xl font-bold ${stat.color || 'text-gray-900'}`}>{stat.value}</p>
            <p className="text-xs text-gray-500 mt-1">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Pitfall table */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-900">Common Pitfalls by Evidence</h2>
          <p className="text-xs text-gray-400 mt-0.5">Only aggregate data shown — no individual learner information.</p>
        </div>

        {pitfalls.length === 0 ? (
          <div className="px-6 py-12 text-center text-gray-400">
            <p className="text-4xl mb-3">📊</p>
            <p className="text-sm">No population data yet. Pitfall analytics will appear once learners start taking concept checks.</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-100">
            {pitfalls.map((p) => {
              const sc = statusConfig[p.status] || statusConfig.insufficient_evidence;
              const isExpanded = expanded === p.pitfall_id;

              return (
                <div key={p.pitfall_id}>
                  <div
                    className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => setExpanded(isExpanded ? null : p.pitfall_id)}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-gray-900 text-sm">{p.title}</h3>
                          <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${sc.bg}`}>
                            {sc.label}
                          </span>
                        </div>
                        <p className="text-xs text-gray-500">{p.concept_name}</p>

                        {/* Score bar */}
                        <div className="mt-3 flex items-center gap-3">
                          <div className="flex-1 h-1.5 bg-gray-100 rounded-full overflow-hidden">
                            <div
                              className={`h-full rounded-full transition-all ${sc.bar}`}
                              style={{ width: `${(p.pitfall_score * 100).toFixed(0)}%` }}
                            ></div>
                          </div>
                          <span className="text-xs font-bold text-gray-700 w-10 text-right">
                            {(p.pitfall_score * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>

                      <div className="text-right flex-shrink-0">
                        <p className="text-lg font-bold text-gray-900">{p.unique_learners}</p>
                        <p className="text-xs text-gray-400">learners</p>
                        <p className="text-sm font-semibold text-orange-600 mt-1">
                          {(p.prevalence * 100).toFixed(0)}% error rate
                        </p>
                      </div>
                    </div>
                  </div>

                  {/* Expanded detail */}
                  {isExpanded && (
                    <div className="px-6 pb-5 bg-gray-50 border-t border-gray-100">
                      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 pt-4">
                        {[
                          { label: 'Total Attempts', value: p.total_attempts, note: null },
                          { label: 'Prevalence', value: `${(p.prevalence * 100).toFixed(0)}%`, note: 'wrong / total attempts' },
                          { label: 'Consistency', value: `${(p.consistency * 100).toFixed(0)}%`, note: 'answers on one wrong option' },
                          { label: 'High-Conf Errors', value: `${(p.high_confidence_error_rate * 100).toFixed(0)}%`, note: 'wrong + high confidence' },
                          { label: 'Recurrence', value: `${(p.recurrence * 100).toFixed(0)}%`, note: 'repeated failures' },
                        ].map((metric) => (
                          <div key={metric.label} className="text-center">
                            <p className="text-xl font-bold text-gray-800">{metric.value}</p>
                            <p className="text-xs font-medium text-gray-600">{metric.label}</p>
                            {metric.note && <p className="text-xs text-gray-400">{metric.note}</p>}
                          </div>
                        ))}
                      </div>

                      {p.wrong_option_distribution && Object.keys(p.wrong_option_distribution).length > 0 && (
                        <div className="mt-4 pt-4 border-t border-gray-200">
                          <p className="text-xs font-semibold text-gray-600 mb-2">Wrong answer distribution</p>
                          <div className="flex gap-3">
                            {Object.entries(p.wrong_option_distribution).map(([option, count]) => (
                              <div key={option} className="text-center bg-white rounded-lg border border-gray-200 px-4 py-2">
                                <p className="font-bold text-gray-800">Option {option}</p>
                                <p className="text-xs text-gray-500">{count} learners</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      <p className="text-xs text-gray-400 mt-4 italic">
                        Score = 0.30×prevalence + 0.25×consistency + 0.20×high-confidence-error-rate + 0.15×recurrence + 0.10×downstream-impact
                      </p>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

export default PopulationInsights;
