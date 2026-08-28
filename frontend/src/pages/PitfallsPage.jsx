import React from 'react';
import PitfallDashboard from '../components/pitfalls/PitfallDashboard';
import PopulationInsights from '../components/pitfalls/PopulationInsights';
import { Link } from 'react-router-dom';

const DEMO_LEARNER_ID = 'LRN0001';

const PitfallsPage = () => {
  return (
    <div className="space-y-8">
      {/* Hero header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Pitfall & Misconception Tracker</h1>
        <p className="text-gray-500 mt-1">
          Track detected misconceptions, monitor your progress, and explore population-level insights.
        </p>
      </div>

      {/* Quick links */}
      <div className="flex gap-3 flex-wrap">
        <Link
          to="/path"
          className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          📚 Back to Learning Path
        </Link>
        <a
          href="/pitfalls/analytics"
          className="inline-flex items-center gap-2 bg-white text-gray-700 border border-gray-300 px-4 py-2 rounded-lg text-sm font-medium hover:border-blue-400 hover:text-blue-600 transition-colors"
        >
          📊 Population Insights
        </a>
      </div>

      {/* Personal dashboard */}
      <PitfallDashboard learnerId={DEMO_LEARNER_ID} compact={false} />
    </div>
  );
};

export default PitfallsPage;
