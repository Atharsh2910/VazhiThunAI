import React from 'react';

const CATEGORY_STYLES = {
  'AI / Technology':    'bg-blue-50 text-blue-700 border-blue-100',
  'Tools & Frameworks': 'bg-violet-50 text-violet-700 border-violet-100',
  'Security':           'bg-red-50 text-red-700 border-red-100',
  'Career':             'bg-emerald-50 text-emerald-700 border-emerald-100',
  'Research':           'bg-amber-50 text-amber-700 border-amber-100',
  'Industry':           'bg-slate-50 text-slate-700 border-slate-200',
  'Learning':           'bg-teal-50 text-teal-700 border-teal-100',
};

const defaultStyle = 'bg-slate-50 text-slate-700 border-slate-200';

/**
 * WeeklyUpdateCard — displays single news/trend update item.
 * Supports "featured" hero variant (larger text, clear callouts) and standard grid variant.
 */
const WeeklyUpdateCard = ({ update, featured = false }) => {
  const {
    title = '',
    summary = '',
    why_it_matters = '',
    category = 'Industry',
    source = '',
    published_at = '',
    url = '#',
  } = update;

  const badgeColor = CATEGORY_STYLES[category] || defaultStyle;

  if (featured) {
    return (
      <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 hover:shadow-md transition-all duration-200 relative overflow-hidden flex flex-col justify-between">
        {/* Top left subtle color indicator */}
        <div className="absolute top-0 left-0 right-0 h-1.5 bg-blue-600" />
        
        <div>
          {/* Badge line */}
          <div className="flex items-center gap-2 mb-4 flex-wrap mt-1">
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-3xs font-extrabold bg-blue-600 text-white tracking-wide uppercase">
              🔥 Featured
            </span>
            <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-3xs font-bold border ${badgeColor}`}>
              {category}
            </span>
          </div>

          {/* Title */}
          <h2 className="text-lg font-bold text-slate-900 mb-2.5 leading-snug">{title}</h2>

          {/* Summary */}
          <p className="text-slate-600 text-sm leading-relaxed mb-4">{summary}</p>

          {/* Why it matters callout panel (replaces purple with blue accent) */}
          {why_it_matters && (
            <div className="bg-blue-50/50 border border-blue-100 rounded-lg px-4 py-3.5 mb-5">
              <p className="text-3xs font-bold text-blue-700 mb-1 uppercase tracking-wider">
                Why this matters for your career
              </p>
              <p className="text-xs text-blue-900 leading-relaxed font-medium">{why_it_matters}</p>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between flex-wrap gap-2 pt-4 border-t border-slate-100 mt-2">
          <p className="text-xs text-slate-400 font-medium">
            {source && <span className="font-semibold text-slate-600">{source}</span>}
            {source && published_at && <span className="mx-1.5">·</span>}
            {published_at}
          </p>
          {url && url !== '#' && (
            <a
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs font-bold text-blue-600 hover:text-blue-800 transition-colors flex items-center gap-1.5"
            >
              Read Article →
            </a>
          )}
        </div>
      </div>
    );
  }

  /* ── Standard card ── */
  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm p-5 hover:shadow-md transition-all duration-200 flex flex-col justify-between">
      <div>
        {/* Category badge */}
        <div className="flex items-center gap-2 mb-3.5 flex-wrap">
          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-3xs font-bold border ${badgeColor}`}>
            {category}
          </span>
        </div>

        {/* Title */}
        <h3 className="text-sm font-bold text-slate-900 mb-2 leading-snug">{title}</h3>

        {/* Summary */}
        <p className="text-xs text-slate-600 leading-relaxed mb-3.5">{summary}</p>

        {/* Why it matters callout */}
        {why_it_matters && (
          <div className="bg-slate-50 border border-slate-100 rounded-lg p-3 mb-4">
            <p className="text-3xs font-bold text-slate-400 mb-1 uppercase tracking-wider">
              Why it matters
            </p>
            <p className="text-3xs text-slate-600 leading-relaxed font-medium">{why_it_matters}</p>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between flex-wrap gap-2 pt-3 border-t border-slate-100 mt-1">
        <p className="text-2xs text-slate-400 font-medium">
          {source && <span className="font-semibold text-slate-600">{source}</span>}
          {source && published_at && <span className="mx-1.5">·</span>}
          {published_at}
        </p>
        {url && url !== '#' && (
          <a
            href={url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-2xs font-bold text-blue-600 hover:text-blue-800 transition-colors"
          >
            Read More →
          </a>
        )}
      </div>
    </div>
  );
};

export default WeeklyUpdateCard;
