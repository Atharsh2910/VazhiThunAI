import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { profileApi } from '../api/profile';

const Onboarding = () => {
  const [formData, setFormData] = useState({
    display_name: '',
    bio: '',
    skillsString: '',
    career_goal: '',
    career_path: ''
  });
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const skillsArray = formData.skillsString
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);

      const payload = {
        display_name: formData.display_name,
        bio: formData.bio,
        skills: skillsArray,
        career_goal: formData.career_goal,
        career_path: formData.career_path,
        current_level: 'Beginner'
      };

      await profileApi.updateProfile(payload);
      navigate('/dashboard');
    } catch (err) {
      console.error('Failed to update profile during onboarding:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-8 px-4 pb-12">
      <Card className="border border-slate-200 shadow-sm bg-white p-8">
        <h1 className="text-3xl font-extrabold text-slate-900 mb-2 text-center tracking-tight">Welcome to VazhiThunAI</h1>
        <p className="text-slate-500 mb-8 text-center text-sm">Let's set up your profile so we can personalize your learning path.</p>
        
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Display Name</label>
            <input
              type="text"
              name="display_name"
              className="shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent block w-full text-sm border border-slate-200 rounded-lg p-3 bg-white text-slate-900 focus:outline-none transition-all"
              placeholder="e.g., John Doe"
              value={formData.display_name}
              onChange={handleInputChange}
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Brief Bio / Details</label>
            <textarea
              name="bio"
              rows="2"
              className="shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent block w-full text-sm border border-slate-200 rounded-lg p-3 bg-white text-slate-900 focus:outline-none transition-all leading-relaxed"
              placeholder="A short introduction about yourself."
              value={formData.bio}
              onChange={handleInputChange}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Interests & Skills</label>
            <input
              type="text"
              name="skillsString"
              className="shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent block w-full text-sm border border-slate-200 rounded-lg p-3 bg-white text-slate-900 focus:outline-none transition-all"
              placeholder="e.g., Python, Machine Learning, Data Science (comma separated)"
              value={formData.skillsString}
              onChange={handleInputChange}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Career Goal</label>
            <textarea
              name="career_goal"
              rows="3"
              className="shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent block w-full text-sm border border-slate-200 rounded-lg p-3 bg-white text-slate-900 focus:outline-none transition-all leading-relaxed"
              placeholder="e.g., I want to become a Senior ML Engineer within the next 2 years."
              value={formData.career_goal}
              onChange={handleInputChange}
              required
            />
          </div>
          
          <div>
            <label className="block text-sm font-semibold text-slate-700 mb-2">Path Achieved (Current Background)</label>
            <input
              type="text"
              name="career_path"
              className="shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent block w-full text-sm border border-slate-200 rounded-lg p-3 bg-white text-slate-900 focus:outline-none transition-all"
              placeholder="e.g., B.Tech in CS, Junior Python Developer"
              value={formData.career_path}
              onChange={handleInputChange}
              required
            />
          </div>

          <div className="flex justify-center pt-4">
            <Button type="submit" disabled={loading} className="w-full sm:w-auto px-10 py-3 text-sm font-semibold">
              {loading ? 'Saving...' : 'Complete Profile & Continue'}
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default Onboarding;
