import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import RemediationCard from '../components/pitfalls/RemediationCard';
import PitfallCheckCard from '../components/pitfalls/PitfallCheckCard';
import PitfallResult from '../components/pitfalls/PitfallResult';
import { startRemediation, submitVerification, getPitfallCheck } from '../api/pitfalls';

const DEMO_LEARNER_ID = 'LRN0001';

const STAGE = {
  LOADING: 'LOADING',
  REMEDIATION: 'REMEDIATION',
  VERIFICATION: 'VERIFICATION',
  DONE: 'DONE',
  ERROR: 'ERROR',
};

const PitfallDetail = () => {
  const { pitfallId } = useParams();
  const navigate = useNavigate();
  const learnerId = DEMO_LEARNER_ID;

  const [stage, setStage] = useState(STAGE.LOADING);
  const [remediationData, setRemediationData] = useState(null);
  const [verificationCheckData, setVerificationCheckData] = useState(null);
  const [verificationResult, setVerificationResult] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // On mount — immediately start remediation (Fix button skips the question step)
  useEffect(() => {
    if (!pitfallId) { setStage(STAGE.ERROR); return; }

    startRemediation(pitfallId, learnerId)
      .then(res => {
        setRemediationData(res.data?.data);
        setStage(STAGE.REMEDIATION);
      })
      .catch(() => setStage(STAGE.ERROR));
  }, [pitfallId, learnerId]);

  // After reviewing the resource, load a verification question
  const handleRemediationComplete = () => {
    // Use the skill linked to this pitfall's concept to fetch a check question
    // We stored skill_id on the concept — the check endpoint gives us a question
    const skillId = remediationData?.skill_id || 'SK011'; // fallback
    getPitfallCheck(skillId, learnerId)
      .then(res => {
        const data = res.data?.data;
        if (data?.available && data?.question) {
          setVerificationCheckData(data);
          setStage(STAGE.VERIFICATION);
        } else {
          // No verification question available — mark as done
          setStage(STAGE.DONE);
        }
      })
      .catch(() => setStage(STAGE.DONE));
  };

  const handleVerify = async ({ questionId, selectedOption, confidence }) => {
    setIsSubmitting(true);
    try {
      const res = await submitVerification({
        pitfallId,
        learnerId,
        questionId,
        selectedOption,
        confidence,
      });
      setVerificationResult(res.data?.data);
      setStage(STAGE.DONE);
    } catch {
      setStage(STAGE.DONE);
    } finally {
      setIsSubmitting(false);
    }
  };

  // ── Render ──────────────────────────────────────────────────────

  if (stage === STAGE.LOADING) return (
    <div className="max-w-2xl mx-auto py-12 text-center">
      <div className="animate-spin w-10 h-10 border-4 border-indigo-200 border-t-indigo-600 rounded-full mx-auto mb-4"></div>
      <p className="text-gray-500">Loading remediation…</p>
    </div>
  );

  if (stage === STAGE.ERROR) return (
    <div className="max-w-2xl mx-auto py-12 text-center">
      <p className="text-4xl mb-3">⚠️</p>
      <h2 className="text-xl font-bold text-gray-900 mb-2">Could not load this pitfall</h2>
      <Link to="/pitfalls" className="text-blue-600 hover:underline text-sm">← Back to Pitfalls</Link>
    </div>
  );

  return (
    <div className="max-w-2xl mx-auto py-6 space-y-6">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-gray-400">
        <Link to="/pitfalls" className="hover:text-blue-600">Pitfalls</Link>
        <span>›</span>
        <span className="text-gray-700">
          {remediationData?.pitfall_title || 'Remediation'}
        </span>
      </div>

      {/* STAGE: Remediation — show the explanation + resource */}
      {stage === STAGE.REMEDIATION && remediationData && (
        <RemediationCard
          resource={remediationData.resource}
          pitfallTitle={remediationData.pitfall_title}
          explanation={remediationData.explanation}
          remediation_text={remediationData.remediation_text}
          onComplete={handleRemediationComplete}
          onSkip={() => navigate('/pitfalls')}
        />
      )}

      {/* STAGE: Verification question */}
      {stage === STAGE.VERIFICATION && verificationCheckData && (
        <div className="space-y-4">
          <div className="bg-purple-50 border border-purple-200 rounded-xl px-6 py-4">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xl">🔍</span>
              <h2 className="font-bold text-purple-900">Verify Understanding</h2>
            </div>
            <p className="text-sm text-purple-700">
              Let's confirm the misconception is resolved with a quick follow-up question.
            </p>
          </div>
          <PitfallCheckCard
            checkData={verificationCheckData}
            onSubmit={handleVerify}
            onSkip={() => navigate('/pitfalls')}
            isLoading={isSubmitting}
          />
        </div>
      )}

      {/* STAGE: Done */}
      {stage === STAGE.DONE && (
        <div className="bg-white rounded-xl border border-gray-200 p-8 text-center shadow-sm">
          {verificationResult?.resolved ? (
            <>
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">✓</span>
              </div>
              <h2 className="text-2xl font-bold text-green-700 mb-2">Misconception Resolved!</h2>
              <p className="text-gray-600 mb-6">
                Great work — you've successfully corrected this misconception.
              </p>
            </>
          ) : (
            <>
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">📖</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Keep Reviewing</h2>
              <p className="text-gray-600 mb-6">
                {verificationResult?.explanation || "This concept needs a bit more practice. We'll revisit it soon."}
              </p>
            </>
          )}
          <Link
            to="/pitfalls"
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors inline-block"
          >
            ← Back to Pitfalls
          </Link>
        </div>
      )}
    </div>
  );
};

export default PitfallDetail;
