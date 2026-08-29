import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/common/Layout';
import Onboarding from './pages/Onboarding';
import Dashboard from './pages/Dashboard';
import LearningPath from './pages/LearningPath';
import Chat from './pages/Chat';
import Login from './pages/Login';
import Register from './pages/Register';
import PitfallCheck from './pages/PitfallCheck';
import PitfallsPage from './pages/PitfallsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import PitfallDetail from './pages/PitfallDetail';
import WeeklyUpdates from './pages/WeeklyUpdates';
import ProtectedRoute from './components/common/ProtectedRoute';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="onboarding" element={<Onboarding />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="path" element={<LearningPath />} />
            <Route path="chat" element={<Chat />} />
            {/* Pitfall routes */}
            <Route path="pitfalls" element={<PitfallsPage />} />
            <Route path="pitfalls/analytics" element={<AnalyticsPage />} />
            <Route path="pitfalls/check/:skillId" element={<PitfallCheck />} />
            <Route path="pitfalls/:pitfallId" element={<PitfallDetail />} />
            <Route path="weekly-updates" element={<WeeklyUpdates />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
