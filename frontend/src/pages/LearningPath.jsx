import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';

// Demo skill IDs that map to pitfall concepts in our seeded data
const pathNodes = [
  {
    id: 1,
    title: 'Python Programming',
    skillId: 'SK001',
    status: 'completed',
    duration: '2 weeks',
    hasPitfallCheck: true,
    pitfallConcept: 'Mutable Default Arguments',
  },
  {
    id: 2,
    title: 'Statistics Foundations',
    skillId: 'SK011',
    status: 'in-progress',
    duration: '1 week',
    hasPitfallCheck: true,
    pitfallConcept: 'Conditional Probability & Correlation',
  },
  {
    id: 3,
    title: 'Machine Learning Basics',
    skillId: 'SK021',
    status: 'locked',
    duration: '3 weeks',
    hasPitfallCheck: true,
    pitfallConcept: 'Data Leakage & Overfitting',
  },
  {
    id: 4,
    title: 'Model Evaluation',
    skillId: 'SK024',
    status: 'locked',
    duration: '2 weeks',
    hasPitfallCheck: true,
    pitfallConcept: 'Accuracy on Imbalanced Data',
  },
  {
    id: 5,
    title: 'Deep Learning',
    skillId: 'SK021',
    status: 'locked',
    duration: '4 weeks',
    hasPitfallCheck: false,
    pitfallConcept: null,
  },
];

// Show pitfall banner between completed and in-progress nodes
const PITFALL_CHECK_AFTER = [1]; // show after node id 1 (Python — completed)

const LearningPath = () => {
  const [dismissedChecks, setDismissedChecks] = useState([]);

  const dismissCheck = (nodeId) => setDismissedChecks((prev) => [...prev, nodeId]);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Learning Path</h1>
        <p className="text-gray-600">A personalized roadmap to your goal.</p>
      </div>

      <div className="relative border-l-2 border-gray-200 ml-4 space-y-0 py-4">
        {pathNodes.map((node, idx) => (
          <React.Fragment key={node.id}>
            {/* Path node */}
            <div className="relative pl-8 mb-6">
              <div className={`absolute -left-[9px] top-1 h-4 w-4 rounded-full border-2 ${
                node.status === 'completed' ? 'bg-green-500 border-green-500' :
                node.status === 'in-progress' ? 'bg-blue-500 border-blue-500' :
                'bg-gray-200 border-gray-300'
              }`}></div>

              <Card className={`transition-all duration-300 hover:shadow-md ${node.status === 'locked' ? 'opacity-60' : ''}`}>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-1">{node.title}</h3>
                    <p className="text-sm text-gray-500">{node.duration}</p>
                    {node.hasPitfallCheck && node.status !== 'locked' && (
                      <p className="text-xs text-indigo-500 mt-1 flex items-center gap-1">
                        ⚡ Pitfall check available · {node.pitfallConcept}
                      </p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    {node.status === 'in-progress' && (
                      <>
                        {node.hasPitfallCheck && (
                          <Link to={`/pitfalls/check/${node.skillId}`}>
                            <Button
                              id={`pitfall-check-${node.id}`}
                              variant="outline"
                              className="text-sm py-1 px-3 text-indigo-600 border-indigo-300 hover:bg-indigo-50"
                            >
                              ⚡ Concept Check
                            </Button>
                          </Link>
                        )}
                        <Button id={`continue-${node.id}`} variant="primary" className="text-sm py-1 px-3">
                          Continue
                        </Button>
                      </>
                    )}
                    {node.status === 'completed' && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        Completed
                      </span>
                    )}
                    {node.status === 'locked' && (
                      <span className="text-sm text-gray-400 font-medium">Locked</span>
                    )}
                  </div>
                </div>
              </Card>
            </div>

            {/* Pitfall Check Banner — shown after a completed node when the NEXT is in-progress */}
            {PITFALL_CHECK_AFTER.includes(node.id) &&
              !dismissedChecks.includes(node.id) &&
              pathNodes[idx + 1]?.status === 'in-progress' && (
              <div className="relative pl-8 mb-6">
                <div className="absolute -left-[9px] top-3 h-4 w-4 rounded-full bg-indigo-400 border-2 border-indigo-400 flex items-center justify-center">
                  <span className="text-white text-[8px] font-bold">⚡</span>
                </div>
                <div className="rounded-xl border-2 border-indigo-200 bg-gradient-to-r from-indigo-50 to-blue-50 p-4">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <span className="text-indigo-600 font-bold">⚡ Concept Check</span>
                        <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-medium">
                          2 questions · ~3 min
                        </span>
                      </div>
                      <p className="text-sm text-gray-700">
                        Before moving to <strong>{pathNodes[idx + 1]?.title}</strong>, let's verify
                        a key concept: <em>{pathNodes[idx + 1]?.pitfallConcept}</em>.
                      </p>
                    </div>
                    <div className="flex gap-2 flex-shrink-0">
                      <Link to={`/pitfalls/check/${pathNodes[idx + 1]?.skillId}`}>
                        <Button id={`start-check-${node.id}`} className="text-sm py-1.5 px-4">
                          Start Check
                        </Button>
                      </Link>
                      <button
                        onClick={() => dismissCheck(node.id)}
                        className="text-xs text-gray-400 hover:text-gray-600 transition-colors px-2"
                        title="Dismiss"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </React.Fragment>
        ))}
      </div>

      {/* Link to full pitfall history */}
      <div className="pl-8">
        <Link
          to="/pitfalls"
          className="inline-flex items-center gap-2 text-sm text-indigo-600 hover:text-indigo-700 font-medium"
        >
          🧠 View all detected pitfalls →
        </Link>
      </div>
    </div>
  );
};

export default LearningPath;
