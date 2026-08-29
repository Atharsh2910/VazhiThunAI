import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';

const Onboarding = () => {
  const [goal, setGoal] = useState('');
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    if (goal.trim()) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-12 px-4">
      <Card className="border border-slate-200 shadow-sm bg-white p-8">
        <h1 className="text-3xl font-extrabold text-slate-900 mb-2 text-center tracking-tight">Welcome to VazhiThunAI</h1>
        <p className="text-slate-500 mb-8 text-center text-sm">Tell us your learning goal. What do you want to achieve?</p>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="goal" className="block text-sm font-semibold text-slate-700 mb-2">Your Goal</label>
            <div className="mt-1">
              <textarea
                id="goal"
                name="goal"
                rows="4"
                className="shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent block w-full text-sm border border-slate-200 rounded-lg p-3.5 bg-white text-slate-900 focus:outline-none transition-all leading-relaxed"
                placeholder="e.g., I want to become a Machine Learning Engineer in 6 months. I know basic Python."
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                required
              />
            </div>
          </div>
          <div className="flex justify-center pt-2">
            <Button type="submit" className="w-full sm:w-auto px-8 py-3 text-sm font-semibold">
              Generate My Path
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default Onboarding;
