import React from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';

const LearningPath = () => {
  const pathNodes = [
    { id: 1, title: 'Python Programming', status: 'completed', duration: '2 weeks' },
    { id: 2, title: 'Statistics Foundations', status: 'in-progress', duration: '1 week' },
    { id: 3, title: 'Machine Learning Basics', status: 'locked', duration: '3 weeks' },
    { id: 4, title: 'Deep Learning', status: 'locked', duration: '4 weeks' }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Your Learning Path</h1>
        <p className="text-gray-600">A personalized roadmap to your goal.</p>
      </div>

      <div className="relative border-l-2 border-gray-200 ml-4 space-y-10 py-4">
        {pathNodes.map((node) => (
          <div key={node.id} className="relative pl-8">
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
                </div>
                {node.status === 'in-progress' && (
                  <Button variant="primary" className="text-sm py-1 px-3">Continue</Button>
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
            </Card>
          </div>
        ))}
      </div>
    </div>
  );
};

export default LearningPath;
