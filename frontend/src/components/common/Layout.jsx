import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import { Menu, X } from 'lucide-react';

/**
 * Layout — sets up the sidebar structure on desktop, hamburger toggle on mobile.
 */
const Layout = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-slate-50">
      {/* Sidebar navigation */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content wrapper */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top bar for mobile header/toggle */}
        <header className="flex h-16 items-center justify-between border-b border-slate-200 bg-white px-6 lg:justify-end">
          <button
            onClick={() => setSidebarOpen(true)}
            className="rounded-lg p-1.5 text-slate-500 hover:bg-slate-100 lg:hidden"
            aria-label="Toggle menu"
          >
            <Menu className="h-6 w-6" />
          </button>
          
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-sm font-semibold text-slate-600">
              U
            </div>
            <span className="hidden text-sm font-medium text-slate-700 sm:inline-block">
              Learner
            </span>
          </div>
        </header>

        {/* Scrollable page body */}
        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="mx-auto max-w-5xl">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
