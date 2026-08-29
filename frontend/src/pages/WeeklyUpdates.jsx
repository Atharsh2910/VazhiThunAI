import React, { useState, useEffect, useCallback } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import WeeklyUpdateCard from '../components/weeklyUpdates/WeeklyUpdateCard';
import { weeklyUpdatesApi } from '../api/weeklyUpdates';

const CAREER_OPTIONS = [
  'Machine Learning Engineer',
  'Data Scientist',
  'Data Engineer',
  'Cloud Engineer',
  'DevOps Engineer',
  'Cybersecurity Engineer',
  'Frontend Developer',
  'Backend Developer',
  'Full Stack Developer',
  'Mobile Developer',
  'Data Analyst',
  'Product Manager',
];

const WeeklyUpdates = () => {
  const [careerPath, setCareerPath] = useState('Machine Learning Engineer');
  const [inputValue, setInputValue] = useState('Machine Learning Engineer');
  const [updates, setUpdates] = useState([]);
  const [period, setPeriod] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiUnavailable, setApiUnavailable] = useState(false);

  const fetchUpdates = useCallback(async (path) => {
    setLoading(true);
    setError(null);
    setApiUnavailable(false);
    setUpdates([]);
    setPeriod('');

    try {
      const res = await weeklyUpdatesApi.getUpdates(path);
      const body = res.data;

      if (!body.success) {
        setApiUnavailable(true);
        setError(body.error?.message || 'Weekly updates are temporarily unavailable.');
        return;
      }

      const data = body.data || {};
      setUpdates(data.updates || []);
      setPeriod(data.period || '');
    } catch (err) {
      if (err.response?.status === 404) {
        setError('Endpoint not found. Is the backend running?');
      } else if (!navigator.onLine) {
        setError('You appear to be offline. Please check your connection.');
      } else {
        setError('Unable to fetch this week\'s updates. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchUpdates(careerPath);
  }, [careerPath, fetchUpdates]);

  const handleSearch = (e) => {
    e.preventDefault();
    const trimmed = inputValue.trim();
    if (trimmed && trimmed !== careerPath) {
      setCareerPath(trimmed);
    } else if (trimmed === careerPath) {
      fetchUpdates(trimmed);
    }
  };

  const topUpdate = updates[0] || null;
  const restUpdates = updates.slice(1);

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">📰 Weekly Career Updates</h1>
        <p className="text-slate-500 text-sm">
          Stay informed about the latest developments and industry-wide tech updates in your career path.
        </p>
      </div>

      {/* Career path input panel */}
      <Card className="border border-slate-200 shadow-sm p-6 bg-white">
        <form onSubmit={handleSearch} className="space-y-4">
          <label htmlFor="career-path-input" className="block text-sm font-semibold text-slate-700">
            Target Career Path
          </label>
          <div className="flex gap-3 flex-wrap sm:flex-nowrap">
            <input
              id="career-path-input"
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="e.g. Data Scientist, DevOps..."
              className="w-full sm:flex-grow border border-slate-200 rounded-lg px-4 py-2.5 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white"
            />
            <Button
              id="weekly-updates-search-btn"
              type="submit"
              variant="primary"
              className="text-sm px-6 py-2.5 rounded-lg font-semibold"
              disabled={loading}
            >
              {loading ? 'Fetching...' : 'Get Updates'}
            </Button>
          </div>

          {/* Quick options pills */}
          <div className="flex flex-wrap gap-2 pt-2">
            {CAREER_OPTIONS.map((opt) => (
              <button
                key={opt}
                type="button"
                id={`career-preset-${opt.replace(/\s+/g, '-').toLowerCase()}`}
                onClick={() => {
                  setInputValue(opt);
                  setCareerPath(opt);
                }}
                className={`text-xs px-3 py-1.5 rounded-full border transition-colors cursor-pointer font-medium ${
                  careerPath === opt
                    ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                    : 'bg-slate-50 text-slate-600 border-slate-200 hover:bg-slate-100 hover:text-slate-800'
                }`}
              >
                {opt}
              </button>
            ))}
          </div>
        </form>
      </Card>

      {/* Section info header */}
      {(period || careerPath) && (
        <div className="flex items-center justify-between flex-wrap gap-3 border-b border-slate-100 pb-3">
          <div>
            <span className="text-lg font-bold text-slate-900">{careerPath}</span>
            {period && (
              <span className="ml-2.5 text-sm font-semibold text-slate-400">· {period}</span>
            )}
          </div>
          <button
            id="weekly-updates-refresh-btn"
            onClick={() => fetchUpdates(careerPath)}
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 cursor-pointer"
            disabled={loading}
          >
            ↻ Refresh feed
          </button>
        </div>
      )}

      {/* Loading state animation */}
      {loading && (
        <div className="space-y-6">
          <div className="bg-white border border-slate-200 shadow-sm rounded-xl p-6 animate-pulse">
            <div className="h-4 bg-slate-100 rounded w-1/4 mb-4" />
            <div className="h-6 bg-slate-100 rounded w-3/4 mb-3" />
            <div className="h-4 bg-slate-100 rounded w-full mb-2" />
            <div className="h-4 bg-slate-100 rounded w-5/6" />
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="bg-white border border-slate-200 shadow-sm rounded-xl p-5 animate-pulse space-y-3">
                <div className="h-3 bg-slate-100 rounded w-1/3" />
                <div className="h-4 bg-slate-100 rounded w-5/6" />
                <div className="h-3 bg-slate-100 rounded w-full" />
              </div>
            ))}
          </div>
          <p className="text-center text-xs text-slate-400 animate-pulse font-medium">
            Loading latest career intelligence updates...
          </p>
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <div className={`rounded-xl border px-5 py-4 text-sm flex items-start gap-3.5 ${
          apiUnavailable
            ? 'border-orange-200 bg-orange-50/50 text-orange-800'
            : 'border-red-200 bg-red-50/50 text-red-800'
        }`}>
          <span className="text-lg">{apiUnavailable ? '⚙️' : '⚠️'}</span>
          <div className="space-y-1">
            <p className="font-bold">
              {apiUnavailable ? 'API Integration Required' : 'Unable to Fetch Updates'}
            </p>
            <p className="text-slate-600 text-xs leading-relaxed">{error}</p>
            {apiUnavailable && (
              <p className="mt-2 text-3xs text-orange-700 bg-orange-100/50 border border-orange-200/50 p-2 rounded-md leading-relaxed">
                Add <code className="bg-orange-100 px-1 rounded font-bold">WEEKLY_UPDATES_API_KEY</code> in{' '}
                <code className="bg-orange-100 px-1 rounded font-bold">backend/.env</code> with a valid{' '}
                <a
                  href="https://gnews.io"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="underline font-bold"
                >
                  GNews API token
                </a>.
              </p>
            )}
          </div>
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && updates.length === 0 && (
        <Card className="border border-slate-200 shadow-sm py-12">
          <div className="text-center space-y-2">
            <p className="text-3xl">🔍</p>
            <p className="text-slate-700 font-bold">No updates found for this career path this week.</p>
            <p className="text-xs text-slate-400">
              Try selection keywords or search another career path preset above.
            </p>
          </div>
        </Card>
      )}

      {/* Featured hero card */}
      {!loading && !error && topUpdate && (
        <section className="space-y-3">
          <h2 className="text-3xs font-semibold uppercase tracking-wider text-slate-400">
            🔥 Featured intelligence
          </h2>
          <WeeklyUpdateCard update={topUpdate} featured />
        </section>
      )}

      {/* General update cards grid */}
      {!loading && !error && restUpdates.length > 0 && (
        <section className="space-y-3">
          <h2 className="text-3xs font-semibold uppercase tracking-wider text-slate-400">
            Other Important Updates
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {restUpdates.map((update, idx) => (
              <WeeklyUpdateCard key={`${update.url}-${idx}`} update={update} />
            ))}
          </div>
        </section>
      )}

      {/* Footer disclaimer */}
      {!loading && !error && updates.length > 0 && (
        <p className="text-3xs text-slate-400 text-center font-medium pt-2">
          Sourced from live global news sources and summarized by AI models. Updates cache for 6 hours.
        </p>
      )}
    </div>
  );
};

export default WeeklyUpdates;
