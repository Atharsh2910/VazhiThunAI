import apiClient from './client';

const BASE = '/adaptive';

export const adaptiveApi = {
  // Path
  getPath: (learnerId) => apiClient.get(`${BASE}/path/${learnerId}`),
  getStatus: (learnerId) => apiClient.get(`${BASE}/status/${learnerId}`),
  getHistory: (learnerId, limit = 20) =>
    apiClient.get(`${BASE}/history/${learnerId}?limit=${limit}`),
  getPathDiff: (learnerId) => apiClient.get(`${BASE}/path-diff/${learnerId}`),
  getProgress: (learnerId, actualHours) =>
    apiClient.get(`${BASE}/progress/${learnerId}${actualHours ? `?actual_weekly_hours=${actualHours}` : ''}`),

  // Feedback
  sendFeedback: (learnerId, itemId, feedbackType) =>
    apiClient.post(`${BASE}/feedback`, {
      learner_id: learnerId,
      item_id: itemId,
      feedback_type: feedbackType,
    }),

  // Assessment
  submitAssessment: (learnerId, skillId, score, pitfallId = null, conceptName = null) =>
    apiClient.post(`${BASE}/assessment`, {
      learner_id: learnerId,
      skill_id: skillId,
      score,
      pitfall_id: pitfallId,
      concept_name: conceptName,
    }),

  // Pitfall integration
  triggerPitfallAdaptation: (learnerId, pitfallId, conceptName) =>
    apiClient.post(`${BASE}/pitfall`, {
      learner_id: learnerId,
      pitfall_id: pitfallId,
      concept_name: conceptName,
    }),

  // Simulation
  simulate: (learnerId, weeklyHours, deadlineWeeks, optionalPolicy = 'keep') =>
    apiClient.post(`${BASE}/simulate`, {
      learner_id: learnerId,
      weekly_hours: weeklyHours,
      deadline_weeks: deadlineWeeks,
      optional_policy: optionalPolicy,
    }),

  simulateFaster: (learnerId) =>
    apiClient.post(`${BASE}/simulate/faster?learner_id=${learnerId}`),

  applySimulation: (learnerId, optionKey, weeklyHours, optionalPolicy = 'keep') =>
    apiClient.post(`${BASE}/apply`, {
      learner_id: learnerId,
      option_key: optionKey,
      weekly_hours: weeklyHours,
      optional_policy: optionalPolicy,
    }),

  // Hours / deadline
  updateHours: (learnerId, newHours) =>
    apiClient.post(`${BASE}/hours`, { learner_id: learnerId, new_hours: newHours }),

  updateDeadline: (learnerId, newDeadlineWeeks) =>
    apiClient.post(`${BASE}/deadline`, {
      learner_id: learnerId,
      new_deadline_weeks: newDeadlineWeeks,
    }),

  makeLighter: (learnerId) =>
    apiClient.post(`${BASE}/lighter?learner_id=${learnerId}`),

  // Verification
  applyVerification: (learnerId, itemId, passed) =>
    apiClient.post(`${BASE}/verify`, {
      learner_id: learnerId,
      item_id: itemId,
      passed,
    }),

  // Complete item
  completeItem: (learnerId, itemId) =>
    apiClient.post(`${BASE}/complete-item`, {
      learner_id: learnerId,
      item_id: itemId,
    }),

  // Adaptive chat
  chat: (learnerId, userMessage, currentItemId = null, history = []) =>
    apiClient.post(`${BASE}/chat`, {
      learner_id: learnerId,
      user_message: userMessage,
      current_item_id: currentItemId,
      history,
    }),
};
