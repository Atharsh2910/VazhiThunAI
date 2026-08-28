import apiClient from './client';

/**
 * Fetch a pitfall check question for a given skill.
 * @param {string} skillId
 * @param {string|null} learnerId - optional, for personalised question selection
 */
export const getPitfallCheck = (skillId, learnerId = null) => {
  const params = learnerId ? { learner_id: learnerId } : {};
  return apiClient.get(`/pitfalls/check/${skillId}`, { params });
};

/**
 * Submit an answer to a pitfall check question.
 */
export const submitPitfallAnswer = ({ learnerId, questionId, selectedOption, confidence }) =>
  apiClient.post('/pitfalls/submit', {
    learner_id: learnerId,
    question_id: questionId,
    selected_option: selectedOption,
    confidence,
  });

/**
 * Get a learner's pitfall dashboard data.
 */
export const getLearnerPitfalls = (learnerId) =>
  apiClient.get(`/pitfalls/learner/${learnerId}`);

/**
 * Start remediation for a pitfall.
 */
export const startRemediation = (pitfallId, learnerId) =>
  apiClient.post(`/pitfalls/${pitfallId}/remediate`, { learner_id: learnerId });

/**
 * Submit a verification answer after remediation.
 */
export const submitVerification = ({ pitfallId, learnerId, questionId, selectedOption, confidence }) =>
  apiClient.post(`/pitfalls/${pitfallId}/verify`, {
    learner_id: learnerId,
    question_id: questionId,
    selected_option: selectedOption,
    confidence,
  });

/**
 * Get population-level analytics for all pitfalls.
 */
export const getPitfallAnalytics = () =>
  apiClient.get('/pitfalls/analytics');

/**
 * Get pitfalls for a specific skill.
 */
export const getPitfallsForSkill = (skillId) =>
  apiClient.get(`/pitfalls/skill/${skillId}`);
