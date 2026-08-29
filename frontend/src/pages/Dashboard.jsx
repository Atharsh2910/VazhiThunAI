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
    <div className="space-y-8">
      {/* Top Greeting */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Good morning, Learner</h1>
        <p className="text-slate-500 text-sm">Continue building your career with VazhiThunAI.</p>
      </div>

      {/* ── Top row ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="col-span-1 md:col-span-2">
          <AdaptiveStatusCard
            status={adaptiveStatus}
            onOpenSimulator={() => setShowSimulator(true)}
          />
        </div>

        {/* Next Action */}
        <Card className="col-span-1 flex flex-col justify-between h-full">
          <div>
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4">▶ Recommended Next Step</h2>
            {nextAction ? (
              <div className="space-y-2">
                <p className="font-semibold text-slate-900 text-base leading-snug">
                  {nextAction.stage_title || nextAction.title}
                </p>
                <p className="text-xs text-slate-500">
                  {nextAction.phase} · ~{nextAction.estimated_minutes ? Math.round(nextAction.estimated_minutes / 60) : '?'} hrs
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-sm text-slate-500">Start your ML Engineer journey</p>
              </div>
            )}
          </div>
          
          <div className="mt-6">
            <Link to="/path">
              <Button id="dashboard-resume-btn" className="w-full text-sm py-2.5">
                {nextAction ? 'Resume Learning' : 'View Path'}
              </Button>
            </Link>
          </div>
        </Card>
      </div>

      {/* ── Middle row: Skill Mastery + Recent Adaptations ── */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-5">Skill Mastery</h2>
          <ul className="space-y-4">
            {[
              { name: 'Python', pct: 80, color: 'bg-emerald-500' },
              { name: 'Statistics', pct: 35, color: 'bg-yellow-500' },
              { name: 'Machine Learning', pct: 15, color: 'bg-blue-600' },
            ].map((skill) => (
              <li key={skill.name}>
                <div className="flex justify-between text-xs mb-1">
                  <span className="font-semibold text-slate-700">{skill.name}</span>
                  <span className="text-slate-500 font-medium">{skill.pct}%</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2">
                  <div className={`${skill.color} h-2 rounded-full transition-all duration-700`} style={{ width: `${skill.pct}%` }} />
                </div>
              </li>
            ))}
          </ul>
        </Card>

        <Card className="flex flex-col justify-between">
          <div>
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4">Recent Adaptations</h2>
            <AdaptationHistory events={adaptiveHistory} compact />
          </div>
          {adaptiveHistory.length > 0 && (
            <div className="mt-4 pt-3 border-t border-slate-100">
              <Link to="/path" className="inline-block text-xs font-semibold text-blue-600 hover:text-blue-700">
                View full path →
              </Link>
            </div>
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
