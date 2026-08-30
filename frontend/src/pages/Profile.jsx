import React, { useState, useEffect, useCallback } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { profileApi } from '../api/profile';
import { adaptiveApi } from '../api/adaptive';
import { Terminal, Briefcase, Code, User, Mail, Award, Target, BookOpen, Edit3, X, Camera } from 'lucide-react';

const DEMO_LEARNER_ID = 'LRN0001';

const Profile = () => {
  const [profile, setProfile] = useState(null);
  const [learningProgress, setLearningProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Edit Modal State
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [editForm, setEditForm] = useState({
    display_name: '',
    bio: '',
    career_goal: '',
    career_path: '',
    current_level: 'Beginner',
    github_url: '',
    linkedin_url: '',
    leetcode_url: '',
    skillsString: '',
  });
  const [saving, setSaving] = useState(false);

  // Profile Photo Upload State
  const fileInputRef = React.useRef(null);
  const [photoError, setPhotoError] = useState('');
  const [photoUploading, setPhotoUploading] = useState(false);

  const handlePhotoChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!validTypes.includes(file.type)) {
      setPhotoError('Invalid image format. Supported formats: JPG, JPEG, PNG, WEBP.');
      return;
    }

    // Validate size (5MB max)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      setPhotoError('Image size exceeds 5MB limit.');
      return;
    }

    setPhotoError('');
    setPhotoUploading(true);

    try {
      const reader = new FileReader();
      reader.onload = async (event) => {
        const rawBase64 = event.target.result;
        
        // Resize image to max 250x250 pixels on a canvas for quick load times and DB compatibility
        const resizedBase64 = await resizeImage(rawBase64, 250, 250);
        
        await profileApi.updateProfile({ avatar: resizedBase64 });
        await loadData();
      };
      reader.readAsDataURL(file);
    } catch (err) {
      setPhotoError('Failed to upload photo. Please try again.');
    } finally {
      setPhotoUploading(false);
    }
  };

  const handlePhotoRemove = async () => {
    setPhotoError('');
    setPhotoUploading(true);
    try {
      await profileApi.updateProfile({ avatar: '' });
      await loadData();
    } catch (err) {
      setPhotoError('Failed to remove photo.');
    } finally {
      setPhotoUploading(false);
    }
  };

  // Helper function to resize the image inside a HTML Canvas element
  const resizeImage = (base64Str, maxWidth = 250, maxHeight = 250) => {
    return new Promise((resolve) => {
      const img = new Image();
      img.src = base64Str;
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > maxWidth) {
            height = Math.round((height * maxWidth) / width);
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width = Math.round((width * maxHeight) / height);
            height = maxHeight;
          }
        }

        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        resolve(canvas.toDataURL('image/jpeg', 0.8));
      };
    });
  };

  const loadData = useCallback(async () => {
    try {
      const [profileRes, statusRes] = await Promise.all([
        profileApi.getProfile(),
        adaptiveApi.getStatus(DEMO_LEARNER_ID).catch(() => null), // Graceful fallback
      ]);
      
      const profileData = profileRes.data?.data || {};
      setProfile(profileData);
      
      if (statusRes && statusRes.data?.data) {
        setLearningProgress(statusRes.data.data.completion_percentage);
      }
      setError(null);
    } catch (err) {
      setError('Could not load profile information. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Open edit modal and populate state
  const handleOpenEdit = () => {
    if (!profile) return;
    setEditForm({
      display_name: profile.display_name || '',
      bio: profile.bio || '',
      career_goal: profile.career_goal || '',
      career_path: profile.career_path || '',
      current_level: profile.current_level || 'Beginner',
      github_url: profile.github_url || '',
      linkedin_url: profile.linkedin_url || '',
      leetcode_url: profile.leetcode_url || '',
      skillsString: (profile.skills || []).join(', '),
    });
    setIsEditOpen(true);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setEditForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const skillsArray = editForm.skillsString
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);

      const payload = {
        display_name: editForm.display_name,
        bio: editForm.bio,
        career_goal: editForm.career_goal,
        career_path: editForm.career_path,
        current_level: editForm.current_level,
        github_url: editForm.github_url,
        linkedin_url: editForm.linkedin_url,
        leetcode_url: editForm.leetcode_url,
        skills: skillsArray,
      };

      await profileApi.updateProfile(payload);
      setIsEditOpen(false);
      await loadData();
    } catch (err) {
      console.error('Update profile failed:', err);
    } finally {
      setSaving(false);
    }
  };

  // Profile Completion Calculation (10 fields total, 10% each)
  const calculateCompletion = () => {
    if (!profile) return 0;
    const fields = [
      profile.display_name,
      profile.email,
      profile.bio,
      profile.career_goal,
      profile.career_path,
      profile.current_level,
      profile.github_url,
      profile.linkedin_url,
      profile.leetcode_url,
      profile.skills && profile.skills.length > 0 ? 'skills' : null,
    ];
    const filled = fields.filter((f) => f && String(f).trim() !== '').length;
    return filled * 10;
  };

  const completionScore = calculateCompletion();

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto space-y-6 animate-pulse">
        <div className="h-40 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="h-48 col-span-2 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200" />
          <div className="h-48 bg-slate-100 dark:bg-slate-800 rounded-xl border border-slate-200" />
        </div>
      </div>
    );
  }

  const userDisplayName = profile?.display_name || 'Learner';
  const userEmail = profile?.email || 'Not set';
  const userBio = profile?.bio || 'Not set';
  const userGoal = profile?.career_goal || 'Not set';
  const userPath = profile?.career_path || 'Not set';
  const userLevel = profile?.current_level || 'Not set';
  const userSkills = profile?.skills || [];

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Error state */}
      {error && (
        <div className="p-4 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 rounded-xl text-red-800 dark:text-red-200 text-sm flex items-center gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* ── Profile Header Panel ── */}
      <Card className="p-6 relative overflow-hidden bg-white border border-slate-200 shadow-sm">
        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
          {/* Interactive Avatar Area */}
          <div className="flex flex-col items-center gap-2 flex-shrink-0">
            <div 
              onClick={() => fileInputRef.current?.click()}
              className="group relative h-20 w-20 rounded-full overflow-hidden bg-blue-50 dark:bg-blue-950 flex items-center justify-center text-blue-600 dark:text-blue-400 font-extrabold text-2xl border border-blue-100 dark:border-blue-900 cursor-pointer"
              title="Change Profile Photo"
            >
              {profile?.avatar ? (
                <img 
                  src={profile.avatar} 
                  alt="Profile Avatar" 
                  className="h-full w-full object-cover" 
                />
              ) : (
                userDisplayName.charAt(0).toUpperCase()
              )}
              
              {/* Camera Overlay on Hover */}
              <div className="absolute inset-0 bg-slate-900/60 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                <Camera className="h-5 w-5 text-white" />
              </div>
            </div>

            {/* Hidden File Input */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handlePhotoChange}
              accept="image/jpeg,image/jpg,image/png,image/webp"
              className="hidden"
            />

            {/* Photo Action Links */}
            <div className="flex gap-2 text-2xs font-semibold">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-blue-600 hover:text-blue-800 transition-colors cursor-pointer"
                disabled={photoUploading}
              >
                {profile?.avatar ? 'Change' : 'Add Photo'}
              </button>
              {profile?.avatar && (
                <>
                  <span className="text-slate-350 dark:text-slate-700">|</span>
                  <button
                    onClick={handlePhotoRemove}
                    className="text-red-500 hover:text-red-700 transition-colors cursor-pointer"
                    disabled={photoUploading}
                  >
                    Remove
                  </button>
                </>
              )}
            </div>

            {/* Photo Error Banner */}
            {photoError && (
              <p className="text-[10px] text-red-500 font-bold text-center leading-tight max-w-[120px]">
                {photoError}
              </p>
            )}
          </div>

          {/* User Meta */}
          <div className="flex-grow text-center sm:text-left space-y-1.5">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <h1 className="text-2xl font-extrabold text-slate-900 dark:text-slate-100 tracking-tight">
                  {userDisplayName}
                </h1>
                <p className="text-xs text-slate-500 dark:text-slate-400 flex items-center justify-center sm:justify-start gap-1.5 mt-0.5 font-medium">
                  <Mail className="h-3.5 w-3.5" />
                  {userEmail}
                </p>
              </div>

              <Button
                onClick={handleOpenEdit}
                variant="outline"
                className="text-xs py-2 px-4 font-semibold flex items-center gap-1.5 border-slate-200 hover:bg-slate-50"
              >
                <Edit3 className="h-3.5 w-3.5" />
                Edit Profile
              </Button>
            </div>

            <div className="pt-2">
              <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Short Bio</p>
              <p className="text-slate-600 dark:text-slate-300 text-sm leading-relaxed mt-1 italic">
                "{userBio}"
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* ── Row 1: Career Info + Profile Completion ── */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Career Information Card */}
        <Card className="md:col-span-2 flex flex-col justify-between">
          <div className="space-y-4">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-slate-400" />
              Career Information
            </h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-lg p-3">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Career Goal</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 mt-1">{userGoal}</p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-lg p-3">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Target Path</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 mt-1">{userPath}</p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-lg p-3">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Current Level</p>
                <p className="text-sm font-semibold text-slate-900 dark:text-slate-100 mt-1">{userLevel}</p>
              </div>

              <div className="bg-slate-50 dark:bg-slate-900 border border-slate-100 dark:border-slate-800 rounded-lg p-3">
                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Learning Progress</p>
                <p className="text-sm font-bold text-blue-600 dark:text-blue-400 mt-1">
                  {learningProgress !== null ? `${learningProgress}%` : 'Not set'}
                </p>
              </div>
            </div>
          </div>
        </Card>

        {/* Profile Completion Indicator */}
        <Card className="flex flex-col justify-between">
          <div className="space-y-4">
            <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <Target className="h-4 w-4 text-slate-400" />
              Profile Completion
            </h2>
            <div className="text-center py-2">
              <span className="text-4xl font-extrabold text-slate-900 dark:text-slate-100">
                {completionScore}%
              </span>
            </div>
            <div className="space-y-1">
              <div className="w-full bg-slate-100 dark:bg-slate-800 rounded-full h-2">
                <div
                  className="h-2 rounded-full bg-blue-600 transition-all duration-500"
                  style={{ width: `${completionScore}%` }}
                />
              </div>
              <p className="text-3xs text-slate-400 font-semibold text-right uppercase">
                {completionScore === 100 ? 'Completed 🎉' : 'Fill more fields to reach 100%'}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* ── Row 2: Professional Profiles ── */}
      <Card>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-5 flex items-center gap-2">
          <Award className="h-4 w-4 text-slate-400" />
          Professional Profiles
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* GitHub Link */}
          <div className="border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex items-center justify-between gap-4 hover:border-slate-350 dark:hover:border-slate-700 transition-colors">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg bg-slate-100 dark:bg-slate-900 flex items-center justify-center text-slate-600 dark:text-slate-400 flex-shrink-0">
                <Terminal className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-700 dark:text-slate-300">GitHub</p>
                {profile?.github_url ? (
                  <a
                    href={profile.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-2xs text-blue-600 hover:underline break-all block truncate max-w-[130px]"
                  >
                    {profile.github_url.replace(/https?:\/\/(www\.)?/, '')}
                  </a>
                ) : (
                  <span className="text-2xs text-slate-400">Not added</span>
                )}
              </div>
            </div>
            <button
              onClick={handleOpenEdit}
              className="text-3xs font-bold text-blue-600 hover:text-blue-800 underline cursor-pointer"
            >
              {profile?.github_url ? 'Edit' : 'Add'}
            </button>
          </div>

          {/* LinkedIn Link */}
          <div className="border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex items-center justify-between gap-4 hover:border-slate-350 dark:hover:border-slate-700 transition-colors">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg bg-slate-100 dark:bg-slate-900 flex items-center justify-center text-slate-600 dark:text-slate-400 flex-shrink-0">
                <Briefcase className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-700 dark:text-slate-300">LinkedIn</p>
                {profile?.linkedin_url ? (
                  <a
                    href={profile.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-2xs text-blue-600 hover:underline break-all block truncate max-w-[130px]"
                  >
                    {profile.linkedin_url.replace(/https?:\/\/(www\.)?/, '')}
                  </a>
                ) : (
                  <span className="text-2xs text-slate-400">Not added</span>
                )}
              </div>
            </div>
            <button
              onClick={handleOpenEdit}
              className="text-3xs font-bold text-blue-600 hover:text-blue-800 underline cursor-pointer"
            >
              {profile?.linkedin_url ? 'Edit' : 'Add'}
            </button>
          </div>

          {/* LeetCode Link */}
          <div className="border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex items-center justify-between gap-4 hover:border-slate-350 dark:hover:border-slate-700 transition-colors">
            <div className="flex items-center gap-3">
              <div className="h-9 w-9 rounded-lg bg-slate-100 dark:bg-slate-900 flex items-center justify-center text-slate-600 dark:text-slate-400 flex-shrink-0">
                <Code className="h-5 w-5" />
              </div>
              <div>
                <p className="text-xs font-bold text-slate-700 dark:text-slate-300">LeetCode</p>
                {profile?.leetcode_url ? (
                  <a
                    href={profile.leetcode_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-2xs text-blue-600 hover:underline break-all block truncate max-w-[130px]"
                  >
                    {profile.leetcode_url.replace(/https?:\/\/(www\.)?/, '')}
                  </a>
                ) : (
                  <span className="text-2xs text-slate-400">Not added</span>
                )}
              </div>
            </div>
            <button
              onClick={handleOpenEdit}
              className="text-3xs font-bold text-blue-600 hover:text-blue-800 underline cursor-pointer"
            >
              {profile?.leetcode_url ? 'Edit' : 'Add'}
            </button>
          </div>
        </div>
      </Card>

      {/* ── Row 3: Skills Section ── */}
      <Card>
        <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
          <Award className="h-4 w-4 text-slate-400" />
          Skills
        </h2>
        {userSkills.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {userSkills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-400 border border-blue-100 dark:border-blue-900"
              >
                {skill}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-slate-400 text-xs italic">No skills listed yet. Click "Edit Profile" to add skills.</p>
        )}
      </Card>

      {/* ── EDIT PROFILE MODAL ── */}
      {isEditOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/50 backdrop-blur-sm">
          <div className="relative w-full max-w-2xl bg-white border border-slate-200 rounded-xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
            {/* Modal Header */}
            <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
              <h3 className="text-lg font-bold text-slate-900">Edit Profile</h3>
              <button
                onClick={() => setIsEditOpen(false)}
                className="text-slate-400 hover:text-slate-655 transition-colors cursor-pointer"
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Modal Body / Scrollable Form */}
            <form onSubmit={handleSave} className="flex-grow overflow-y-auto p-6 space-y-5">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Full Name
                  </label>
                  <input
                    type="text"
                    name="display_name"
                    value={editForm.display_name}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm placeholder-slate-400"
                    placeholder="Enter your name"
                    required
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Current Level
                  </label>
                  <select
                    name="current_level"
                    value={editForm.current_level}
                    onChange={handleInputChange}
                    className="w-full px-3 py-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
                  >
                    <option value="Beginner">Beginner</option>
                    <option value="Intermediate">Intermediate</option>
                    <option value="Advanced">Advanced</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Short Bio
                </label>
                <textarea
                  name="bio"
                  rows="2"
                  value={editForm.bio}
                  onChange={handleInputChange}
                  placeholder="Tell us a bit about yourself..."
                  className="w-full px-3 py-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm placeholder-slate-400"
                />
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Career Goal
                  </label>
                  <input
                    type="text"
                    name="career_goal"
                    value={editForm.career_goal}
                    onChange={handleInputChange}
                    placeholder="e.g. Become a Machine Learning Engineer"
                    className="w-full px-3 py-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm placeholder-slate-400"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                    Target Career Path
                  </label>
                  <input
                    type="text"
                    name="career_path"
                    value={editForm.career_path}
                    onChange={handleInputChange}
                    placeholder="e.g. Machine Learning Engineer"
                    className="w-full px-3 py-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm placeholder-slate-400"
                  />
                </div>
              </div>

              <div className="space-y-4 pt-2 border-t border-slate-100">
                <h4 className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">
                  Professional Profile URLs
                </h4>
                
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-[10px] font-bold text-slate-600 mb-1.5">
                      GitHub URL
                    </label>
                    <input
                      type="url"
                      name="github_url"
                      value={editForm.github_url}
                      onChange={handleInputChange}
                      placeholder="https://github.com/..."
                      className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-xs placeholder-slate-400"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold text-slate-600 mb-1.5">
                      LinkedIn URL
                    </label>
                    <input
                      type="url"
                      name="linkedin_url"
                      value={editForm.linkedin_url}
                      onChange={handleInputChange}
                      placeholder="https://linkedin.com/in/..."
                      className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-xs placeholder-slate-400"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-bold text-slate-600 mb-1.5">
                      LeetCode URL
                    </label>
                    <input
                      type="url"
                      name="leetcode_url"
                      value={editForm.leetcode_url}
                      onChange={handleInputChange}
                      placeholder="https://leetcode.com/..."
                      className="w-full px-3 py-2 rounded-lg border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-xs placeholder-slate-400"
                    />
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-100">
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">
                  Skills (comma-separated)
                </label>
                <input
                  type="text"
                  name="skillsString"
                  value={editForm.skillsString}
                  onChange={handleInputChange}
                  placeholder="Python, Machine Learning, Deep Learning, SQL"
                  className="w-full px-3 py-2.5 rounded-lg border border-slate-200 bg-slate-50 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm placeholder-slate-400"
                />
              </div>

              {/* Modal Actions */}
              <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100 mt-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setIsEditOpen(false)}
                  disabled={saving}
                  className="px-4 py-2 border-slate-200"
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  disabled={saving}
                  className="px-6 py-2"
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile;
