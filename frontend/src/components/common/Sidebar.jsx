import React, { useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Map, 
  MessageSquare, 
  Newspaper, 
  Brain, 
  LogOut,
  Sun,
  Moon,
  User
} from 'lucide-react';

const navigation = [
  {
    title: 'MAIN',
    items: [
      { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
      { name: 'Learning Path', path: '/path', icon: Map },
      { name: 'AI Assistant', path: '/chat', icon: MessageSquare },
    ]
  },
  {
    title: 'CAREER',
    items: [
      { name: 'Weekly Updates', path: '/weekly-updates', icon: Newspaper },
      { name: 'Pitfalls', path: '/pitfalls', icon: Brain },
    ]
  },
  {
    title: 'ACCOUNT',
    items: [
      { name: 'My Profile', path: '/profile', icon: User },
    ]
  }
];

const Sidebar = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const [theme, setTheme] = useState(localStorage.getItem('theme') || 'light');

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    localStorage.setItem('theme', nextTheme);
    if (nextTheme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const navItemClass = ({ isActive }) => {
    const base = "flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-colors";
    if (isActive) {
      return `${base} bg-blue-50 text-blue-600`;
    }
    return `${base} text-slate-600 hover:text-slate-900 hover:bg-slate-50`;
  };

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 z-20 bg-slate-900/40 backdrop-blur-sm lg:hidden"
          onClick={onClose}
        />
      )}

      {/* Sidebar Container */}
      <aside 
        className={`fixed inset-y-0 left-0 z-30 flex w-60 flex-col border-r border-slate-200 bg-white transition-transform lg:static lg:translate-x-0 ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="flex h-16 items-center border-b border-slate-100 px-6">
          <NavLink to="/" className="text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span className="h-8 w-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-extrabold text-sm">V</span>
            VazhiThunAI
          </NavLink>
        </div>

        {/* Navigation Groups */}
        <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-7">
          {navigation.map((group) => (
            <div key={group.title} className="space-y-2">
              <h4 className="px-3 text-2xs font-semibold tracking-wider text-slate-400 uppercase">
                {group.title}
              </h4>
              <div className="space-y-1">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  return (
                    <NavLink
                      key={item.path}
                      to={item.path}
                      className={navItemClass}
                      onClick={onClose}
                    >
                      <Icon className="h-4 w-4 flex-shrink-0" />
                      {item.name}
                    </NavLink>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer Area with Theme Toggle & Logout */}
        <div className="border-t border-slate-100 p-4 space-y-1">
          <button
            onClick={toggleTheme}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50 hover:text-slate-900 transition-colors cursor-pointer"
          >
            {theme === 'dark' ? (
              <>
                <Sun className="h-4 w-4 flex-shrink-0 text-slate-400" />
                Light Mode
              </>
            ) : (
              <>
                <Moon className="h-4 w-4 flex-shrink-0 text-slate-400" />
                Dark Mode
              </>
            )}
          </button>
          
          <button
            onClick={handleLogout}
            className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 hover:bg-red-50 hover:text-red-600 transition-colors cursor-pointer"
          >
            <LogOut className="h-4 w-4 flex-shrink-0" />
            Logout
          </button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
