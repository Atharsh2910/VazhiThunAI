import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
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
  TOO_HARD:        { icon: '😵', label: 'Too Difficult — Adjusting path', color: 'text-red-700 bg-red-50 border-red-100' },
  TOO_EASY:        { icon: '👍', label: 'Too Easy — Finding harder resource', color: 'text-emerald-700 bg-emerald-50 border-emerald-100' },
  ALREADY_KNOWN:   { icon: '🔁', label: 'Verification requested', color: 'text-purple-700 bg-purple-50 border-purple-100' },
  REQUEST_FASTER:  { icon: '⚡', label: 'Generating faster path scenarios', color: 'text-blue-700 bg-blue-50 border-blue-100' },
  REQUEST_LIGHTER: { icon: '🪶', label: 'Creating lighter path simulation', color: 'text-amber-700 bg-amber-50 border-amber-100' },
  CHANGE_HOURS:    { icon: '⏱', label: 'Updating weekly hours', color: 'text-sky-700 bg-sky-50 border-sky-100' },
  CHANGE_DEADLINE: { icon: '📅', label: 'Updating deadline', color: 'text-teal-700 bg-teal-50 border-teal-100' },
  WHY_CHANGED:     { icon: '❓', label: 'Explaining path changes', color: 'text-slate-700 bg-slate-100 border-slate-200' },
  WHAT_IF:         { icon: '📊', label: 'Running simulation', color: 'text-blue-700 bg-blue-50 border-blue-100' },
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
      // Build history from current messages (exclude the one we just added, map to backend format)
      const history = messages
        .filter((m) => m.role === 'user' || m.role === 'ai')
        .slice(-6)
        .map((m) => ({
          role: m.role === 'ai' ? 'assistant' : 'user',
          content: m.text,
        }));

      const res = await adaptiveApi.generalChat(DEMO_LEARNER_ID, text, history);
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
      addMessage('ai', "I'm having trouble connecting to the backend right now. Please make sure the backend server is running on port 8001.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto h-[82vh] flex flex-col gap-4">
      <div className="flex flex-col gap-1">
        <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">AI Assistant</h1>
        <p className="text-sm text-slate-500">Chat to adapt your ML Engineer learning path</p>
      </div>

      <Card className="flex-grow flex flex-col overflow-hidden p-0 min-h-0 border border-slate-200">
        {/* Messages list */}
        <div className="flex-grow overflow-y-auto p-5 space-y-4">
          {messages.map((msg) => {
            if (msg.role === 'system') {
              const lbl = intentLabel(msg.intent);
              return (
                <div key={msg.id} className="flex justify-center my-2">
                  <span className={`text-xs px-3 py-1.5 rounded-full border font-semibold ${lbl?.color || 'bg-slate-100 text-slate-600 border-slate-200'}`}>
                    {msg.text}
                  </span>
                </div>
              );
            }

            return (
              <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[75%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-none'
                    : 'bg-slate-50 border border-slate-150 text-slate-800 rounded-tl-none'
                }`}>
                  {msg.role === 'ai' ? (
                    <div className="prose prose-sm max-w-none text-gray-800">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.text}</ReactMarkdown>
                    </div>
                  ) : (
                    <p className="whitespace-pre-line">{msg.text}</p>
                  )}

                  {/* Show adaptation inline result */}
                  {msg.adaptationResult?.success && msg.adaptationResult.adaptation_type !== 'NO_CHANGE' && (
                    <div className="mt-2.5 pt-2.5 border-t border-slate-200/60 text-xs">
                      <span className="text-blue-600 font-semibold">✓ Path updated — </span>
                      <a href="/path" className="text-blue-500 underline font-medium">View changes</a>
                    </div>
                  )}

                  {/* Show simulator trigger */}
                  {msg.requiresConfirmation && msg.simulationResult && (
                    <button
                      onClick={() => setShowSimulator(true)}
                      className="mt-2.5 block text-xs text-blue-600 font-semibold underline hover:text-blue-700"
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
              <div className="bg-slate-50 border border-slate-100 rounded-xl rounded-tl-none px-4 py-3">
                <div className="flex gap-1.5 items-center py-1">
                  {[0,1,2].map(i => (
                    <div key={i} className="w-2 h-2 bg-slate-400 rounded-full animate-bounce" style={{ animationDelay: `${i*0.15}s` }} />
                  ))}
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Quick prompts toolbar */}
        <div className="px-5 py-3 border-t border-slate-100 bg-slate-50/50">
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-hide">
            {QUICK_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                onClick={() => handleSend(prompt)}
                disabled={loading}
                className="flex-shrink-0 text-xs px-3.5 py-2 rounded-full border border-slate-200 text-slate-600 bg-white hover:bg-slate-50 hover:border-blue-300 hover:text-blue-600 transition-colors font-medium cursor-pointer"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Text Input area */}
        <div className="p-4 border-t border-slate-200 bg-white">
          <form onSubmit={(e) => { e.preventDefault(); handleSend(); }} className="flex gap-3">
            <input
              id="chat-input"
              type="text"
              className="flex-grow border border-slate-200 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white text-slate-900"
              placeholder="Type your message, e.g. 'Make it easier'..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
            />
            <Button 
              id="chat-send-btn" 
              type="submit" 
              className="px-6 py-2.5 rounded-lg text-sm font-semibold" 
              disabled={loading}
            >
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
