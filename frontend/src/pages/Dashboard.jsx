import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import PitfallDashboard from '../components/pitfalls/PitfallDashboard';
import AdaptiveStatusCard from '../components/adaptive/AdaptiveStatusCard';
import AdaptationHistory from '../components/adaptive/AdaptationHistory';
import WhatIfSimulator from '../components/adaptive/WhatIfSimulator';
import { adaptiveApi } from '../api/adaptive';

const DEMO_LEARNER_ID = 'LRN0001';

const Dashboard = () => {
  const [adaptiveStatus, setAdaptiveStatus] = useState(null);
  const [adaptiveHistory, setAdaptiveHistory] = useState([]);
  const [showSimulator, setShowSimulator] = useState(false);

  useEffect(() => {
    const load = async () => {
      try {
        const [statusRes, histRes] = await Promise.all([
          adaptiveApi.getStatus(DEMO_LEARNER_ID),
          adaptiveApi.getHistory(DEMO_LEARNER_ID, 5),
        ]);
        setAdaptiveStatus(statusRes.data?.data);
        setAdaptiveHistory(histRes.data?.data?.events || []);
      } catch (_) {
        // Backend offline — graceful degradation
      }
    };
    load();
  }, []);

  const nextAction = adaptiveStatus?.current_item;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>

      {/* ── Top row ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-1 md:col-span-2">
          <AdaptiveStatusCard
            status={adaptiveStatus}
            onOpenSimulator={() => setShowSimulator(true)}
          />
        </div>

        {/* Next Action */}
        <Card className="col-span-1">
          <h2 className="text-base font-semibold mb-3 text-gray-700">▶ Next Action</h2>
          {nextAction ? (
            <>
              <p className="font-semibold text-gray-900 mb-1 text-sm">
                {nextAction.stage_title || nextAction.title}
              </p>
              <p className="text-xs text-gray-500 mb-3">
                {nextAction.phase} · ~{nextAction.estimated_minutes ? Math.round(nextAction.estimated_minutes / 60) : '?'} hrs
              </p>
              <Link to="/path">
                <Button id="dashboard-resume-btn" className="w-full text-sm">Resume Learning</Button>
              </Link>
            </>
          ) : (
            <>
              <p className="text-sm text-gray-500 mb-3">Start your ML Engineer journey</p>
              <Link to="/path">
                <Button id="dashboard-start-btn" className="w-full text-sm">View Path</Button>
              </Link>
            </>
          )}
        </Card>
      </div>

      {/* ── Middle row: Skill Mastery + Recent Adaptations ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-base font-semibold mb-4 text-gray-700">Skill Mastery</h2>
          <ul className="space-y-3">
            {[
              { name: 'Python', pct: 80, color: 'bg-emerald-500' },
              { name: 'Statistics', pct: 35, color: 'bg-yellow-500' },
              { name: 'Machine Learning', pct: 15, color: 'bg-blue-500' },
            ].map((skill) => (
              <li key={skill.name}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-medium text-gray-700">{skill.name}</span>
                  <span className="text-gray-400">{skill.pct}%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-1.5">
                  <div className={`${skill.color} h-1.5 rounded-full transition-all duration-700`} style={{ width: `${skill.pct}%` }} />
                </div>
              </li>
            ))}
          </ul>
        </Card>

        <Card>
          <h2 className="text-base font-semibold mb-4 text-gray-700">Recent Adaptations</h2>
          <AdaptationHistory events={adaptiveHistory} compact />
          {adaptiveHistory.length > 0 && (
            <Link to="/path" className="block mt-3 text-xs text-indigo-600 hover:text-indigo-700">
              View full path →
            </Link>
          )}
        </Card>
      </div>

      {/* ── Pitfall Dashboard Widget ── */}
      <PitfallDashboard learnerId={DEMO_LEARNER_ID} compact={true} />

      {/* What-If Simulator Modal */}
      {showSimulator && (
        <WhatIfSimulator
          learnerId={DEMO_LEARNER_ID}
          currentState={adaptiveStatus}
          onApply={() => setShowSimulator(false)}
          onClose={() => setShowSimulator(false)}
        />
      )}
    </div>
  );
};

export default Dashboard;
