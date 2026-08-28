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
      // Typically save to API or context here
      navigate('/dashboard');
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-10">
      <Card>
        <h1 className="text-3xl font-bold text-gray-900 mb-6 text-center">Welcome to VazhiThunAI</h1>
        <p className="text-gray-600 mb-8 text-center text-lg">Tell us your learning goal. What do you want to achieve?</p>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="goal" className="block text-sm font-medium text-gray-700">Your Goal</label>
            <div className="mt-1">
              <textarea
                id="goal"
                name="goal"
                rows="4"
                className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md p-3 border"
                placeholder="e.g., I want to become a Machine Learning Engineer in 6 months. I know basic Python."
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
              />
            </div>
          </div>
          <div className="flex justify-center">
            <Button type="submit" className="w-full sm:w-auto px-8 py-3 text-lg">Generate My Path</Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default Onboarding;
