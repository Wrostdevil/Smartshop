import React, { useState, useEffect } from 'react';
import { Bot, X, Loader2, MessageSquare, Sparkles } from 'lucide-react';
import { api } from '../lib/api';
import SupportRAGModule from './SupportRAGModule';

export default function RAGBotWidget({ isLiveApi, backendUp }) {
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showWelcome, setShowWelcome] = useState(true);
  const liveMode = isLiveApi && backendUp;
  const messagesEndRef = React.useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [isOpen, isMinimized]);

  const handleToggle = () => {
    setIsOpen(!isOpen);
    if (isOpen) {
      setIsMinimized(false);
    }
    if (!isOpen) {
      setShowWelcome(false);
      setUnreadCount(0);
    }
  };

  const handleMinimize = () => {
    setIsMinimized(true);
    setUnreadCount(0);
  };

  const handleClose = () => {
    setIsOpen(false);
    setIsMinimized(false);
  };

  return (
    <>
      {/* Floating Bot Button - Bottom Left */}
      {!isOpen && (
        <button
          onClick={handleToggle}
          className="fixed bottom-6 left-6 z-50 w-14 h-14 rounded-full bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-2xl shadow-indigo-500/40 hover:from-indigo-500 hover:to-pink-400 hover:scale-105 transition-all duration-300 animate-pulse-slow"
          aria-label="Open RAG Assistant"
          title="Policy Assistant - Ask me anything about returns, shipping, warranties..."
        >
          <Bot className="w-7 h-7 text-white" />
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-[10px] font-bold w-5 h-5 rounded-full flex items-center justify-center animate-bounce">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>
      )}

      {/* Minimized Bar */}
      {isMinimized && (
        <div className="fixed bottom-6 left-6 z-50 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 flex items-center gap-3 shadow-2xl animate-slide-up">
          <Bot className="w-5 h-5 text-indigo-400" />
          <span className="text-sm font-medium text-slate-200 hidden sm:block">Policy Assistant</span>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsMinimized(false)}
              className="p-1.5 text-slate-400 hover:text-white transition-colors"
              aria-label="Expand"
            >
              <MessageSquare className="w-4 h-4" />
            </button>
            <button
              onClick={handleClose}
              className="p-1.5 text-slate-400 hover:text-white transition-colors"
              aria-label="Close"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Full Widget - Bottom Left Drawer/Modal */}
      {isOpen && !isMinimized && (
        <div className="fixed bottom-6 left-6 z-50 w-full max-w-md sm:max-w-lg lg:max-w-xl animate-slide-up">
          {/* Backdrop for mobile */}
          <div
            className="fixed inset-0 bg-black/50 lg:hidden"
            onClick={handleClose}
            aria-hidden="true"
          />

          <div className="relative bg-slate-950 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden flex flex-col h-[calc(100vh-3rem)] max-h-[700px] min-h-[500px]">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-slate-800 bg-gradient-to-r from-indigo-900/60 via-slate-900 to-purple-900/40">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-sm">Policy Assistant</h3>
                  <p className="text-[11px] text-slate-400 flex items-center gap-1.5">
                    <span className={`w-2 h-2 rounded-full ${liveMode ? 'bg-emerald-400' : 'bg-amber-400'}`} />
                    {liveMode ? 'Postgres + pgvector Live' : 'Mock Mode'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1">
                <button
                  onClick={handleMinimize}
                  className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                  aria-label="Minimize"
                >
                  <span className="block w-5 h-0.5 bg-current" />
                </button>
                <button
                  onClick={handleClose}
                  className="p-2 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
                  aria-label="Close"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden flex flex-col">
              {/* Welcome Screen */}
              {showWelcome && (
                <div className="flex-1 flex flex-col items-center justify-center p-6 text-center space-y-4">
                  <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-600/30 via-purple-600/30 to-pink-500/30 flex items-center justify-center">
                    <Bot className="w-8 h-8 text-indigo-400" />
                  </div>
                  <div className="space-y-2">
                    <h4 className="font-bold text-white text-lg">How can I help?</h4>
                    <p className="text-slate-400 text-sm max-w-xs">
                      Ask me about returns, shipping, warranties, Prime benefits, or any ShopSmart policy.
                    </p>
                  </div>
                  <div className="grid grid-cols-2 gap-2 w-full max-w-xs">
                    {[
                      "Can I return an opened laptop?",
                      "What is the refund timeline?",
                      "Does Prime include free delivery?",
                      "Can I cancel after shipment?"
                    ].map((q, i) => (
                      <button
                        key={i}
                        onClick={() => {
                          setShowWelcome(false);
                        }}
                        className="text-left p-3 bg-slate-800/60 border border-slate-700/60 rounded-xl hover:border-indigo-500/50 hover:bg-slate-800 transition-all text-xs text-slate-300"
                      >
                        "{q}"
                      </button>
                    ))}
                  </div>
                  <div className="flex items-center gap-2 text-[11px] text-slate-500 pt-2">
                    <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                    <span>Powered by RAG + pgvector • Grounded answers with citations</span>
                  </div>
                </div>
              )}

              {/* RAG Module */}
              {!showWelcome && (
                <div className="flex-1 flex flex-col min-h-0">
                  <SupportRAGModule 
                    isLiveApi={liveMode} 
                    onQueryStart={() => setShowWelcome(false)}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}