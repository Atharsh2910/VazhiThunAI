import React from 'react';
import { Outlet, Link } from 'react-router-dom';

const Layout = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="text-2xl font-bold text-blue-600">
                VazhiThunAI
              </Link>
            </div>
            <nav className="flex space-x-4">
              <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">Dashboard</Link>
              <Link to="/path" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">Learning Path</Link>
              <Link to="/pitfalls" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">🧠 Pitfalls</Link>
              <Link to="/chat" className="text-gray-700 hover:text-blue-600 px-3 py-2 rounded-md text-sm font-medium">AI Assistant</Link>
            </nav>

          </div>
        </div>
      </header>

      <main className="flex-grow max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>

      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500">
            &copy; {new Date().getFullYear()} VazhiThunAI. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
