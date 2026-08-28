import React from 'react';
import { Link } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import PitfallDashboard from '../components/pitfalls/PitfallDashboard';

// In production this comes from auth context / localStorage
const DEMO_LEARNER_ID = 'LRN0001';

const Dashboard = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="col-span-1 md:col-span-2">
          <h2 className="text-xl font-semibold mb-4">Current Goal</h2>
          <p className="text-gray-700 mb-2">Become a Machine Learning Engineer</p>
          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
            <div className="bg-blue-600 h-2.5 rounded-full" style={{ width: '15%' }}></div>
          </div>
          <p className="text-sm text-gray-500">15% completed • Estimated 5 months remaining</p>
        </Card>

        <Card className="col-span-1">
          <h2 className="text-xl font-semibold mb-4">Next Best Action</h2>
          <p className="font-medium text-gray-800 mb-2">Complete Intro to Statistics</p>
          <p className="text-sm text-gray-600 mb-4">2 hours • Core prerequisite</p>
          <Link to="/path">
            <Button className="w-full">Resume Learning</Button>
          </Link>
        </Card>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <h2 className="text-xl font-semibold mb-4">Skill Mastery</h2>
          <ul className="space-y-3">
            <li>
              <div className="flex justify-between text-sm mb-1">
                <span>Python</span>
                <span>80%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div className="bg-green-500 h-1.5 rounded-full" style={{ width: '80%' }}></div>
              </div>
            </li>
            <li>
              <div className="flex justify-between text-sm mb-1">
                <span>Statistics</span>
                <span>20%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-1.5">
                <div className="bg-yellow-500 h-1.5 rounded-full" style={{ width: '20%' }}></div>
              </div>
            </li>
          </ul>
        </Card>

        <Card>
          <h2 className="text-xl font-semibold mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              <span>Completed Python Basics Quiz</span>
              <span className="ml-auto text-gray-400">Yesterday</span>
            </div>
            <div className="flex items-center gap-4 text-sm text-gray-600">
              <div className="w-2 h-2 rounded-full bg-blue-500"></div>
              <span>Generated ML Engineer Path</span>
              <span className="ml-auto text-gray-400">2 days ago</span>
            </div>
          </div>
        </Card>
      </div>

      {/* ── Pitfall Dashboard Widget ── */}
      <PitfallDashboard learnerId={DEMO_LEARNER_ID} compact={true} />
    </div>
  );
};

export default Dashboard;
