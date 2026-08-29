import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import Button from '../components/common/Button';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');
    
    try {
      const response = await apiClient.post('/auth/login', { email, password });
      if (response.data && response.data.success) {
        const token = response.data.data.access_token;
        localStorage.setItem('token', token);
        navigate('/dashboard');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to login. Please check your credentials.');
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
          <h2 className="text-4xl font-bold leading-tight">Your AI-powered career companion.</h2>
          <p className="text-slate-400 text-base leading-relaxed">
            Personalized learning paths, automated pitfall detection, and weekly career intelligence updates curated specifically for your career goals.
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
            <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">Sign in</h1>
            <p className="mt-2 text-sm text-slate-500">Enter your details to access your dashboard.</p>
          </div>

          {error && (
            <div className="p-4 bg-red-50/50 border border-red-200 rounded-xl text-red-800 text-sm">
              ⚠️ {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-6">
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
              <div className="flex items-center justify-between mb-2">
                <label className="block text-sm font-semibold text-slate-700">Password</label>
              </div>
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
              {isLoading ? 'Signing in...' : 'Sign in'}
            </Button>
          </form>

          <p className="text-center text-sm text-slate-500">
            Don't have an account?{' '}
            <Link to="/register" className="font-semibold text-blue-600 hover:text-blue-500 transition-colors">
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;
