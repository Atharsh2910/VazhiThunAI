import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import Button from '../components/common/Button';

const Register = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const response = await apiClient.post('/auth/register', { display_name: name, email, password });
      if (response.data && response.data.success) {
        navigate('/login');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create account. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex bg-slate-50">
      {/* Split Layout: Left side illustration/brand panel (hidden on small devices) */}
      <div className="hidden lg:flex lg:w-1/2 bg-slate-900 text-white flex-col justify-between p-12 relative overflow-hidden">
        {/* Subtle geometric grid background pattern */}
        <div className="absolute inset-0 opacity-5 pointer-events-none">
          <div className="absolute inset-0" style={{ backgroundImage: 'radial-gradient(circle, white 1px, transparent 1px)', backgroundSize: '24px 24px' }}></div>
        </div>

        <div className="z-10">
          <Link to="/" className="flex items-start">
            <img src="/vazhithunai-logo.png" alt="VazhiThunAI" className="auth-logo" />
          </Link>
        </div>

        <div className="z-10 max-w-md space-y-4 my-auto">
          <h2 className="text-4xl font-bold leading-tight">Create your learner account today.</h2>
          <p className="text-slate-400 text-base leading-relaxed">
            Begin mapping your personalized learning path, diagnosing concepts, and analyzing updates for your target career goals.
          </p>
        </div>

        <div className="z-10 text-xs text-slate-500">
          &copy; {new Date().getFullYear()} VazhiThunAI. All rights reserved.
        </div>
      </div>

      {/* Right side form card */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-6 sm:p-12 bg-white">
        <div className="w-full max-w-md space-y-8">
          <div>
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Create Account</h1>
            <p className="mt-2 text-sm text-slate-500">Enter your details to create your personalized space.</p>
          </div>

          {error && (
            <div className="p-4 bg-red-50/50 border border-red-200 rounded-xl text-red-800 text-sm">
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleRegister} className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Full Name</label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-slate-200 bg-white text-slate-950 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-sm"
                placeholder="John Doe"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Email address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-slate-200 bg-white text-slate-950 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-sm"
                placeholder="you@example.com"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-semibold text-slate-700 mb-2">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-lg border border-slate-200 bg-white text-slate-950 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all text-sm"
                placeholder="••••••••"
                required
              />
            </div>

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full py-3"
            >
              {isLoading ? 'Creating account...' : 'Create Account'}
            </Button>
          </form>

          <p className="text-center text-sm text-slate-500">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-500 transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;
