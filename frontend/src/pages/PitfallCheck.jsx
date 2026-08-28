import React, { useState, useEffect } from 'react';
import { useParams, useSearchParams, useNavigate, Link } from 'react-router-dom';
import PitfallCheckCard from '../components/pitfalls/PitfallCheckCard';
import PitfallResult from '../components/pitfalls/PitfallResult';
import RemediationCard from '../components/pitfalls/RemediationCard';
import {
  getPitfallCheck,
  submitPitfallAnswer,
  startRemediation,
  submitVerification,
} from '../api/pitfalls';

// Demo learner — in production this comes from auth context / localStorage
const DEMO_LEARNER_ID = 'LRN0001';

const STAGE = {
  LOADING: 'LOADING',
  CHECK: 'CHECK',
  RESULT: 'RESULT',
  REMEDIATION: 'REMEDIATION',
  VERIFICATION: 'VERIFICATION',
  DONE: 'DONE',
  NO_CHECK: 'NO_CHECK',
  ERROR: 'ERROR',
};

const PitfallCheck = () => {
  const { skillId } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const learnerId = searchParams.get('learner_id') || DEMO_LEARNER_ID;

  const [stage, setStage] = useState(STAGE.LOADING);
  const [checkData, setCheckData] = useState(null);
  const [submitResult, setSubmitResult] = useState(null);
  const [remediationData, setRemediationData] = useState(null);
  const [verificationData, setVerificationData] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!skillId) { setStage(STAGE.ERROR); return; }
    getPitfallCheck(skillId, learnerId)
      .then(res => {
        const data = res.data?.data;
        if (data?.available && data?.question) {
          setCheckData(data);
          setStage(STAGE.CHECK);
        } else {
          setStage(STAGE.NO_CHECK);
        }
      })
      .catch(() => setStage(STAGE.ERROR));
  }, [skillId, learnerId]);

  const handleSubmit = async ({ questionId, selectedOption, confidence }) => {
    setIsSubmitting(true);
    try {
      const res = await submitPitfallAnswer({
        learnerId,
        questionId,
        selectedOption,
        confidence,
      });
      setSubmitResult(res.data?.data);
      setStage(STAGE.RESULT);
    } catch (e) {
      setError('Failed to submit answer. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFixThis = async () => {
    const pitfallId = submitResult?.pitfall_id;
    if (!pitfallId) { setStage(STAGE.DONE); return; }
    try {
      const res = await startRemediation(pitfallId, learnerId);
      setRemediationData(res.data?.data);
      setStage(STAGE.REMEDIATION);
    } catch {
      setStage(STAGE.DONE);
    }
  };

  const handleRemediationComplete = () => {
    // Get a verification question (re-use the same question from the check)
    setStage(STAGE.VERIFICATION);
  };

  const handleVerify = async ({ questionId, selectedOption, confidence }) => {
    const pitfallId = submitResult?.pitfall_id;
    setIsSubmitting(true);
    try {
      const res = await submitVerification({
        pitfallId,
        learnerId,
        questionId,
        selectedOption,
        confidence,
      });
      setVerificationData(res.data?.data);
      setStage(STAGE.DONE);
    } catch {
      setStage(STAGE.DONE);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleContinue = () => navigate('/path');
  const handleSkip = () => navigate('/path');

  // ── Render helpers ─────────────────────────────────────────────

  if (stage === STAGE.LOADING) return (
    <div className="max-w-2xl mx-auto py-12 text-center">
      <div className="animate-spin w-10 h-10 border-4 border-blue-200 border-t-blue-600 rounded-full mx-auto mb-4"></div>
      <p className="text-gray-500">Loading concept check…</p>
    </div>
  );

  if (stage === STAGE.NO_CHECK) return (
    <div className="max-w-2xl mx-auto py-12 text-center">
      <p className="text-4xl mb-4">✓</p>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">No pitfall check needed</h1>
      <p className="text-gray-500 mb-6">There are no specific pitfall checks for this skill right now.</p>
      <button onClick={handleContinue} className="bg-blue-600 text-white px-6 py-2 rounded font-medium hover:bg-blue-700">
        Continue Learning →
      </button>
    </div>
  );

  if (stage === STAGE.ERROR) return (
    <div className="max-w-2xl mx-auto py-12 text-center">
      <p className="text-4xl mb-4">⚠️</p>
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Something went wrong</h1>
      <p className="text-gray-500 mb-6">{error || 'Could not load the pitfall check.'}</p>
      <button onClick={handleContinue} className="bg-blue-600 text-white px-6 py-2 rounded font-medium hover:bg-blue-700">
        Continue Anyway →
      </button>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto py-6 space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <Link to="/path" className="hover:text-blue-600">Learning Path</Link>
        <span>›</span>
        <span className="text-gray-700">Concept Check</span>
        {checkData?.concept_name && (
          <>
            <span>›</span>
            <span className="text-gray-700">{checkData.concept_name}</span>
          </>
        )}
      </div>

      {/* STAGE: Question */}
      {stage === STAGE.CHECK && checkData && (
        <PitfallCheckCard
          checkData={checkData}
          onSubmit={handleSubmit}
          onSkip={handleSkip}
          isLoading={isSubmitting}
        />
      )}

      {/* STAGE: Result */}
      {stage === STAGE.RESULT && submitResult && (
        <PitfallResult
          result={submitResult}
          onContinue={handleContinue}
          onFixThis={handleFixThis}
          onPractice={handleFixThis}
        />
      )}

      {/* STAGE: Remediation */}
      {stage === STAGE.REMEDIATION && remediationData && (
        <RemediationCard
          resource={remediationData.resource}
          pitfallTitle={remediationData.pitfall_title}
          explanation={remediationData.explanation}
          remediation_text={remediationData.remediation_text}
          onComplete={handleRemediationComplete}
          onSkip={handleContinue}
        />
      )}

      {/* STAGE: Verification */}
      {stage === STAGE.VERIFICATION && checkData && (
        <div className="space-y-4">
          <div className="bg-purple-50 border border-purple-200 rounded-xl px-6 py-4">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-purple-700 font-bold text-lg">🔍</span>
              <h2 className="font-bold text-purple-900">Verify Understanding</h2>
            </div>
            <p className="text-sm text-purple-700">
              Let's confirm the misconception is resolved with a quick follow-up question.
            </p>
          </div>
          <PitfallCheckCard
            checkData={checkData}
            onSubmit={handleVerify}
            onSkip={handleContinue}
            isLoading={isSubmitting}
          />
        </div>
      )}

      {/* STAGE: Done */}
      {stage === STAGE.DONE && (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center shadow-sm">
          {verificationData?.resolved ? (
            <>
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">✓</span>
              </div>
              <h2 className="text-2xl font-bold text-green-700 mb-2">Misconception Resolved!</h2>
              <p className="text-gray-600 mb-6">
                Great work. You've successfully corrected this misconception. Your learning path has been updated.
              </p>
            </>
          ) : (
            <>
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">📖</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Keep Reviewing</h2>
              <p className="text-gray-600 mb-6">
                {verificationData?.explanation || 'This concept needs a bit more practice. We\'ll revisit it when relevant.'}
              </p>
            </>
          )}
          <button
            onClick={handleContinue}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
          >
            Back to Learning Path →
          </button>
        </div>
      )}
    </div>
  );
};

export default PitfallCheck;
