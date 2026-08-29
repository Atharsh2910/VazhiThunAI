import React, { useState, useRef, useEffect } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import WhatIfSimulator from '../components/adaptive/WhatIfSimulator';
import AdaptationNotification from '../components/adaptive/AdaptationNotification';
import { adaptiveApi } from '../api/adaptive';

const DEMO_LEARNER_ID = 'LRN0001';

const QUICK_PROMPTS = [
  "I find this too difficult",
  "I already know Python",
  "I only have 5 hours a week",
  "Can I finish faster?",
  "Make my roadmap lighter",
  "Why did my path change?",
  "I need to finish in 3 months",
];

const intentLabel = (intent) => ({
  TOO_HARD:        { icon: '😵', label: 'Too Difficult — Adjusting path', color: 'text-red-600 bg-red-50' },
  TOO_EASY:        { icon: '👍', label: 'Too Easy — Finding harder resource', color: 'text-emerald-600 bg-emerald-50' },
  ALREADY_KNOWN:   { icon: '🔁', label: 'Verification requested', color: 'text-purple-600 bg-purple-50' },
  REQUEST_FASTER:  { icon: '⚡', label: 'Generating faster path scenarios', color: 'text-indigo-600 bg-indigo-50' },
  REQUEST_LIGHTER: { icon: '🪶', label: 'Creating lighter path simulation', color: 'text-amber-600 bg-amber-50' },
  CHANGE_HOURS:    { icon: '⏱', label: 'Updating weekly hours', color: 'text-blue-600 bg-blue-50' },
  CHANGE_DEADLINE: { icon: '📅', label: 'Updating deadline', color: 'text-teal-600 bg-teal-50' },
  WHY_CHANGED:     { icon: '❓', label: 'Explaining path changes', color: 'text-gray-600 bg-gray-50' },
  WHAT_IF:         { icon: '📊', label: 'Running simulation', color: 'text-indigo-600 bg-indigo-50' },
}[intent] || null);

const Chat = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'ai',
      text: "Hi! I'm your adaptive learning assistant. I can adjust your ML Engineer path based on your feedback.\n\nTry saying: 'This is too hard', 'I only have 5 hours a week', or 'Can I finish faster?'",
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [showSimulator, setShowSimulator] = useState(false);
  const [simulatorData, setSimulatorData] = useState(null);
  const [notification, setNotification] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const addMessage = (role, text, meta = {}) => {
    setMessages((prev) => [...prev, { id: Date.now() + Math.random(), role, text, ...meta }]);
  };

  const handleSend = async (msgText) => {
    const text = (msgText || input).trim();
    if (!text || loading) return;
    setInput('');
    addMessage('user', text);
    setLoading(true);

    try {
      const res = await adaptiveApi.chat(DEMO_LEARNER_ID, text, null, []);
      const data = res.data?.data;

      const intent = data?.intent;
      const label = intentLabel(intent);

      // Show intent badge if recognized adaptive intent
      if (label && intent !== 'GENERAL_CHAT') {
        addMessage('system', `${label.icon} ${label.label}`, { intent });
      }

      // Main AI response
      addMessage('ai', data?.response || 'Got it!', {
        adaptationResult: data?.adaptation_result,
        simulationResult: data?.simulation_result,
        requiresConfirmation: data?.requires_confirmation,
      });

      // If adaptation happened, show notification
      if (data?.adaptation_result?.success) {
        setNotification(data.adaptation_result);
      }

      // If simulation, open the simulator modal
      if (data?.requires_confirmation && data?.simulation_result) {
        setSimulatorData(data.simulation_result);
        setTimeout(() => setShowSimulator(true), 500);
      }

    } catch (err) {
      // Fallback to general response
      addMessage('ai', "I'm having trouble connecting to the backend right now. Please make sure the backend server is running on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[82vh] flex flex-col gap-4">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">AI Assistant</h1>
        <p className="text-sm text-gray-500">Chat to adapt your ML Engineer learning path</p>
      </div>

      <Card className="flex-grow flex flex-col overflow-hidden p-0 min-h-0">
        {/* Messages */}
        <div className="flex-grow overflow-y-auto p-5 space-y-3">
          {messages.map((msg) => {
            if (msg.role === 'system') {
              const lbl = intentLabel(msg.intent);
              return (
                <div key={msg.id} className="flex justify-center">
                  <span className={`text-xs px-3 py-1.5 rounded-full font-medium ${lbl?.color || 'bg-gray-100 text-gray-600'}`}>
                    {msg.text}
                  </span>
                </div>
              );
            }

            return (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-indigo-600 text-white rounded-br-none'
                    : 'bg-gray-100 text-gray-800 rounded-bl-none'
                }`}>
                  <p className="whitespace-pre-line">{msg.text}</p>

                  {/* Show adaptation inline result */}
                  {msg.adaptationResult?.success && msg.adaptationResult.adaptation_type !== 'NO_CHANGE' && (
                    <div className="mt-2 pt-2 border-t border-gray-200 text-xs">
                      <span className="text-indigo-600 font-medium">✓ Path updated — </span>
                      <a href="/path" className="text-indigo-500 underline">View changes</a>
                    </div>
                  )}

                  {/* Show simulator trigger */}
                  {msg.requiresConfirmation && msg.simulationResult && (
                    <button
                      onClick={() => setShowSimulator(true)}
                      className="mt-2 block text-xs text-indigo-600 font-medium underline"
                    >
                      📊 Open What-If Simulator →
                    </button>
                  )}
                </div>
              </div>
            );
          })}

          {loading && (
            <div className="flex justify-start">
              <div className="bg-gray-100 rounded-2xl rounded-bl-none px-4 py-3">
                <div className="flex gap-1">
                  {[0,1,2].map(i => (
                    <div key={i} className="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: `${i*0.15}s` }} />
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Quick prompts */}
        <div className="px-4 py-2 border-t border-gray-100 bg-gray-50">
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {QUICK_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                onClick={() => handleSend(prompt)}
                disabled={loading}
                className="flex-shrink-0 text-xs px-3 py-1.5 rounded-full border border-gray-200 text-gray-600 bg-white hover:bg-gray-50 hover:border-indigo-300 hover:text-indigo-600 transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Input */}
        <div className="p-4 border-t border-gray-200 bg-white">
          <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-2">
            <input
              id="chat-input"
              type="text"
              className="flex-grow border border-gray-200 rounded-full px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-300 focus:border-indigo-300"
              placeholder="e.g. 'I only have 5 hours a week now' or 'Make it easier'..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <Button id="chat-send-btn" type="submit" className="rounded-full px-5" disabled={loading}>
              {loading ? '...' : 'Send'}
            </Button>
          </form>
        </div>
      </Card>

      {/* Simulator modal */}
      {showSimulator && (
        <WhatIfSimulator
          learnerId={DEMO_LEARNER_ID}
          onApply={(result) => {
            setShowSimulator(false);
            setNotification({ success: true, adaptation_type: 'APPLIED', explanation: `Applied! New projected completion: ${result?.new_projected_weeks?.toFixed(1)} weeks.` });
            addMessage('ai', `✓ Done! Your path has been updated. Projected completion: ${result?.new_projected_weeks?.toFixed(1)} weeks.`);
          }}
          onClose={() => setShowSimulator(false)}
        />
      )}

      <AdaptationNotification adaptation={notification} onDismiss={() => setNotification(null)} />
    </div>
  );
};

export default Chat;
