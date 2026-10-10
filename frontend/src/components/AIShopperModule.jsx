import React, { useState } from 'react';
import { Sparkles, Send, CheckCircle2, DollarSign, Cpu, ShoppingBag, HelpCircle, Layers, ArrowRight, Loader2 } from 'lucide-react';
import { MOCK_PRODUCTS } from '../data/mockProducts';
import { api } from '../lib/api';

export default function AIShopperModule({ onAddToCart, onToggleCompare, comparedIds, isLiveApi, catalog = [] }) {
  const products = catalog.length ? catalog : MOCK_PRODUCTS;
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [aiResponse, setAiResponse] = useState({
    interpretedRequirement: "Laptop for Java development and AI learning",
    budget: 1000,
    recommendations: [
      {
        productId: "LAP101",
        productName: "Dell Inspiron 15 AI Edition",
        reason: "16GB RAM, Intel i7 processor, and NVMe SSD storage handle JVM multithreading & AI workloads within $1000 budget.",
        availability: "IN_STOCK",
        price: 949
      },
      {
        productId: "LAP103",
        productName: "Lenovo Legion Slim 5 AI",
        reason: "NVIDIA RTX 4060 provides hardware CUDA acceleration for PyTorch/TensorFlow deep learning tasks.",
        availability: "LOW_STOCK",
        price: 999
      }
    ],
    clarifyingQuestion: null
  });

  const samplePrompts = [
    "Suggest a laptop under $1000 for Java development and AI projects.",
    "Best noise-canceling headphones for deep focus work under $400.",
    "Show me smartphones with flagship cameras and generative AI features."
  ];

  const handleRunAiShopper = (inputQuery) => {
    const query = inputQuery || prompt;
    if (!query.trim()) return;

    setIsLoading(true);

    if (isLiveApi) {
      // FastAPI backend: POST {base}/recommend (Postgres catalog, intent scoring)
      api.recommend(query)
        .then((data) => {
          setAiResponse(data);
          setIsLoading(false);
        })
        .catch(() => {
          // Fallback to local intelligence if backend is not running yet
          simulateLocalAiResponse(query);
        });
    } else {
      simulateLocalAiResponse(query);
    }
  };

  const simulateLocalAiResponse = (query) => {
    setTimeout(() => {
      const qLower = query.toLowerCase();
      let budget = 1000;
      let matched = [products[0], products[2]].filter(Boolean);

      if (qLower.includes('headphone') || qLower.includes('audio') || qLower.includes('noise')) {
        budget = 400;
        matched = [products.find((p) => (p.category || '').toLowerCase().includes('audio')) || products[4]].filter(Boolean);
      } else if (qLower.includes('phone') || qLower.includes('mobile') || qLower.includes('samsung')) {
        budget = 1200;
        matched = [products.find((p) => (p.category || '').toLowerCase().includes('phone')) || products[3]].filter(Boolean);
      } else if (qLower.includes('vacuum') || qLower.includes('clean') || qLower.includes('home')) {
        budget = 900;
        matched = [products.find((p) => (p.category || '').toLowerCase().includes('home')) || products[5]].filter(Boolean);
      }

      setAiResponse({
        interpretedRequirement: query,
        budget: budget,
        recommendations: matched.map((m) => ({
          productId: m.slug || m.id,
          productName: m.name,
          reason: (m.aiSummary?.pros || []).join('. '),
          availability: m.availability,
          price: m.price
        })),
        clarifyingQuestion: null
      });
      setIsLoading(false);
    }, 600);
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-purple-900/60 via-indigo-900/60 to-slate-900 border border-purple-500/30 rounded-3xl p-6 relative overflow-hidden backdrop-blur-md">
        <div className="relative z-10 space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-amber-300 uppercase tracking-wider">
            <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" /> AI Shopping Co-Pilot
          </div>
          <h2 className="text-2xl font-extrabold text-white">Autonomous Intent-Based Product Discovery</h2>
          <p className="text-xs text-slate-300 max-w-xl">
            Describe your specific workload, budget, or feature preferences in plain English. Our AI agent extracts requirements and selects optimal products with explicit explanations.
          </p>
        </div>
      </div>

      {/* Input Prompt Card */}
      <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-4 space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleRunAiShopper()}
            placeholder="e.g. Suggest a laptop under $1000 for Java development and AI projects..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500"
          />
          <button
            onClick={() => handleRunAiShopper()}
            disabled={isLoading}
            className="bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white px-5 py-3 rounded-xl font-bold text-xs flex items-center gap-2 shadow-lg shadow-purple-600/30 transition-all active:scale-95 disabled:opacity-50"
          >
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            <span>Ask AI</span>
          </button>
        </div>

        {/* Preset Prompt Chips */}
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[11px] font-semibold text-slate-400">Try asking:</span>
          {samplePrompts.map((sp, idx) => (
            <button
              key={idx}
              onClick={() => {
                setPrompt(sp);
                handleRunAiShopper(sp);
              }}
              className="text-[11px] bg-slate-900/80 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded-lg border border-slate-700/60 transition-colors"
            >
              "{sp}"
            </button>
          ))}
        </div>
      </div>

      {/* AI Response Output Section */}
      {aiResponse && (
        <div className="space-y-6 animate-fadeIn">
          {/* Interpreted Requirement Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400">
                <Cpu className="w-5 h-5" />
              </div>
              <div>
                <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 block">Interpreted Intent</span>
                <span className="text-sm font-semibold text-slate-100">{aiResponse.interpretedRequirement}</span>
              </div>
            </div>

            {aiResponse.budget && (
              <div className="flex items-center gap-2 bg-slate-800 px-3.5 py-1.5 rounded-xl border border-slate-700">
                <DollarSign className="w-4 h-4 text-emerald-400" />
                <div>
                  <span className="text-[10px] text-slate-400 block -mb-0.5">Budget Limit</span>
                  <span className="text-xs font-bold font-mono text-emerald-300">${aiResponse.budget}</span>
                </div>
              </div>
            )}
          </div>

          {/* Recommendations List */}
          <div className="space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" /> AI Ranked Recommendations
            </h3>

            <div className="grid md:grid-cols-2 gap-4">
              {aiResponse.recommendations.map((rec, idx) => {
                const fullProd = products.find((p) => (p.slug || p.id) === rec.productId || p.id === rec.productId) || products[0];
                const isCompared = comparedIds.includes(fullProd.id);

                return (
                  <div
                    key={rec.productId}
                    className="bg-slate-800/60 border border-slate-700/80 hover:border-purple-500/50 rounded-2xl p-5 space-y-4 relative flex flex-col justify-between transition-all"
                  >
                    <div className="space-y-3">
                      {/* Rank tag */}
                      <div className="flex justify-between items-center">
                        <span className="bg-purple-500/20 text-purple-300 font-mono text-xs font-bold px-2.5 py-0.5 rounded-full border border-purple-500/30">
                          Rank #{idx + 1} Match
                        </span>
                        <span className="text-xs font-extrabold font-mono text-white">${rec.price}</span>
                      </div>

                      {/* Product name */}
                      <h4 className="font-bold text-slate-100 text-base">{rec.productName}</h4>

                      {/* AI Reasoning Box */}
                      <div className="bg-purple-950/40 p-3 rounded-xl border border-purple-500/30 text-xs text-purple-200 space-y-1">
                        <div className="font-bold flex items-center gap-1 text-amber-300">
                          <Sparkles className="w-3.5 h-3.5 text-amber-400" /> Why AI Recommends This:
                        </div>
                        <p className="leading-relaxed text-slate-300">{rec.reason}</p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="pt-3 border-t border-slate-700/50 flex items-center justify-between gap-2">
                      <button
                        onClick={() => onToggleCompare(fullProd.id)}
                        className={`flex items-center gap-1 text-xs font-semibold px-3 py-1.5 rounded-lg border ${
                          isCompared ? 'bg-indigo-600 text-white border-indigo-500' : 'bg-slate-900 text-slate-300 border-slate-700'
                        }`}
                      >
                        <Layers className="w-3.5 h-3.5" />
                        <span>{isCompared ? 'Comparing' : 'Compare Specs'}</span>
                      </button>

                      <button
                        onClick={() => onAddToCart(fullProd)}
                        className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-1.5 rounded-lg text-xs font-bold shadow-md shadow-indigo-600/20"
                      >
                        <ShoppingBag className="w-3.5 h-3.5" /> Add to Cart
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
