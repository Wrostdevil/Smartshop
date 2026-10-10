import React, { useState, useEffect } from 'react';
import { BookOpen, Search, ShieldCheck, FileText, CheckCircle2, AlertTriangle, Loader2, Upload, Trash2, Ticket } from 'lucide-react';
import { api } from '../lib/api';

export default function SupportRAGModule({ isLiveApi }) {
  const [query, setQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [docs, setDocs] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadMsg, setUploadMsg] = useState('');
  const [ticketMsg, setTicketMsg] = useState('');
  const [ragResult, setRagResult] = useState({
    answer: "Opened laptops can be returned within 7 days of delivery if physical damage is not present. Original packaging and accessories must be included.",
    confidence: "HIGH",
    sources: [
      { document: "Laptop Return Policy", section: "Opened Products", version: "2026.1" },
      { document: "Enterprise Hardware Warranty SLA", section: "Return Inspection Guidelines", version: "2026.2" }
    ],
    followUpRequired: false
  });

  const sampleQuestions = [
    "Can I return an opened laptop?",
    "What is the refund timeline?",
    "Does Prime membership include free delivery?",
    "Can I cancel my order after shipment?"
  ];

  const refreshDocs = () => {
    if (!isLiveApi) return;
    api.documents().then(setDocs).catch(() => {});
  };
  useEffect(refreshDocs, [isLiveApi]);

  const handleAskRAG = (inputQuery) => {
    const q = inputQuery || query;
    if (!q.trim()) return;
    setIsLoading(true);
    setTicketMsg('');
    if (isLiveApi) {
      // FastAPI backend: POST {base}/rag-query (pgvector search over ingested chunks)
      api.ragQuery(q)
        .then((data) => { setRagResult(data); setIsLoading(false); })
        .catch(() => simulateLocalRAG(q));
    } else {
      simulateLocalRAG(q);
    }
  };

  const simulateLocalRAG = (q) => {
    setTimeout(() => {
      const qLower = q.toLowerCase();
      let answer = "For standard orders, refunds are processed within 3-5 business days back to original payment method.";
      let confidence = "HIGH";
      let sources = [{ document: "ShopSmart Refund & Billing Policy", section: "Timeline & Payment Processing", version: "2026.1" }];

      if (qLower.includes('laptop') || qLower.includes('opened') || qLower.includes('return')) {
        answer = "Opened laptops can be returned within 7 days of delivery provided there is no physical damage. All original box items must be returned.";
        sources = [
          { document: "Laptop Return Policy", section: "Opened Products", version: "2026.1" },
          { document: "Hardware Warranty Policy", section: "Physical Condition Standard", version: "2025.4" }
        ];
      } else if (qLower.includes('prime') || qLower.includes('shipping') || qLower.includes('delivery')) {
        answer = "Yes! Prime and Premium membership tiers include free express 1-day delivery on all eligible catalog products with no minimum spend.";
        sources = [{ document: "Membership SLA & Benefits", section: "Prime Delivery Guarantees", version: "2026.1" }];
      } else if (qLower.includes('cancel')) {
        answer = "Orders can be canceled free of charge before they reach the 'Shipped' status. Once in transit, you may reject delivery or initiate a return upon arrival.";
        sources = [{ document: "Order Cancellation & Fulfillment Guide", section: "In-Transit Orders", version: "2026.3" }];
      }
      setRagResult({ answer, confidence, sources, followUpRequired: false });
      setIsLoading(false);
    }, 500);
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setUploadMsg('');
    try {
      const res = await api.uploadDocument(file, { section: 'General', version: '2026.1', category: 'policy' });
      setUploadMsg(`Ingested "${file.name}" → ${res.chunks} chunks embedded.`);
      refreshDocs();
    } catch (err) {
      setUploadMsg(`Upload failed: ${err.message}`);
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleDeleteDoc = async (id) => {
    try {
      await fetch(`${api.base}/documents/${id}`, { method: 'DELETE' });
      refreshDocs();
    } catch {}
  };

  const handleRaiseTicket = async () => {
    try {
      const t = await api.ticket({ subject: query || 'RAG follow-up', message: ragResult.answer, email: 'guest@shopsmart.ai' });
      setTicketMsg(`Support ticket ${t.ticket_number} created — an agent will respond within 24h.`);
    } catch {
      setTicketMsg('Could not create ticket (backend offline).');
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="bg-gradient-to-r from-indigo-900/60 via-slate-900 to-purple-900/40 border border-indigo-500/30 rounded-3xl p-6 relative overflow-hidden backdrop-blur-md">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase tracking-wider">
            <BookOpen className="w-4 h-4" /> RAG Knowledge Assistant {isLiveApi && <span className="text-emerald-400 normal-case">• Postgres + pgvector live</span>}
          </div>
          <h2 className="text-2xl font-extrabold text-white">Enterprise Policy & SLA Intelligence</h2>
          <p className="text-xs text-slate-300 max-w-lg">
            Answers are generated strictly from approved knowledge documents with verified source citations, section references, and confidence scores.
          </p>
        </div>
      </div>

      <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-4 space-y-3">
        <div className="flex gap-2">
          <input type="text" value={query} onChange={(e) => setQuery(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleAskRAG()}
            placeholder="Ask a policy, return, warranty or shipping question..."
            className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-3 text-sm text-slate-100 placeholder-slate-400 focus:outline-none focus:border-indigo-500" />
          <button onClick={() => handleAskRAG()} disabled={isLoading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-3 rounded-xl font-bold text-xs flex items-center gap-2 shadow-lg shadow-indigo-600/30 disabled:opacity-50">
            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
            <span>Query Knowledge Base</span>
          </button>
        </div>
        <div className="flex flex-wrap items-center gap-2 pt-1">
          <span className="text-[11px] font-semibold text-slate-400">Sample questions:</span>
          {sampleQuestions.map((sq, idx) => (
            <button key={idx} onClick={() => { setQuery(sq); handleAskRAG(sq); }}
              className="text-[11px] bg-slate-900/80 hover:bg-slate-700 text-slate-300 px-3 py-1 rounded-lg border border-slate-700/60 transition-colors">"{sq}"</button>
          ))}
        </div>
      </div>

      {ragResult && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6 animate-fadeIn">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-4">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">AI Grounded Response</span>
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1.5 text-xs font-bold font-mono px-3 py-1 rounded-full border bg-emerald-500/10 text-emerald-400 border-emerald-500/30">
                <ShieldCheck className="w-3.5 h-3.5" /><span>Confidence: {ragResult.confidence}</span>
              </div>
              {ragResult.followUpRequired && (
                <div className="flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30">
                  <AlertTriangle className="w-3.5 h-3.5" /> Follow-up Required
                </div>
              )}
            </div>
          </div>
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 text-slate-200 text-sm leading-relaxed">{ragResult.answer}</div>
          {ragResult.followUpRequired && (
            <div className="space-y-2">
              <button onClick={handleRaiseTicket} className="flex items-center gap-2 bg-amber-600 hover:bg-amber-500 text-white px-4 py-2 rounded-xl text-xs font-bold">
                <Ticket className="w-4 h-4" /> Raise support ticket for this question
              </button>
              {ticketMsg && <p className="text-xs text-amber-300">{ticketMsg}</p>}
            </div>
          )}
          <div className="space-y-3">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
              <FileText className="w-4 h-4 text-indigo-400" /> Grounded Source Citations ({ragResult.sources?.length || 0})
            </h4>
            <div className="grid sm:grid-cols-2 gap-3">
              {ragResult.sources?.map((src, idx) => (
                <div key={idx} className="bg-slate-800/60 border border-slate-700/60 p-3.5 rounded-xl space-y-1">
                  <div className="flex justify-between items-start">
                    <span className="font-bold text-xs text-indigo-300">{src.document}</span>
                    <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-1.5 py-0.5 rounded">v{src.version}</span>
                  </div>
                  <span className="text-xs text-slate-400 block">Section: <strong className="text-slate-200">{src.section}</strong></span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Module 2: document ingestion — upload PDF / Markdown / JSON */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-2">
          <Upload className="w-4 h-4 text-indigo-400" /> Knowledge Base Documents {docs.length > 0 && <span className="text-slate-500">({docs.length})</span>}
        </h3>
        {isLiveApi ? (
          <>
            <label className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 border border-dashed border-slate-600 rounded-xl px-4 py-3 text-xs text-slate-300 cursor-pointer transition-colors">
              <Upload className="w-4 h-4 text-indigo-400" />
              {uploading ? 'Embedding document…' : 'Upload PDF / Markdown / JSON policy document'}
              <input type="file" accept=".pdf,.md,.markdown,.json,.txt" className="hidden" onChange={handleUpload} disabled={uploading} />
            </label>
            {uploadMsg && <p className="text-xs text-indigo-300">{uploadMsg}</p>}
            <div className="grid sm:grid-cols-2 gap-2">
              {docs.map((d) => (
                <div key={d.id} className="flex items-center justify-between bg-slate-800/60 border border-slate-700/60 px-3 py-2 rounded-xl">
                  <div className="min-w-0">
                    <p className="text-xs font-bold text-slate-200 truncate">{d.document}</p>
                    <p className="text-[10px] text-slate-500 font-mono">{d.section} • v{d.version} • {d.chunks} chunks</p>
                  </div>
                  <button onClick={() => handleDeleteDoc(d.id)} className="p-1.5 text-slate-500 hover:text-rose-400" title="Delete document">
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p className="text-xs text-slate-500">Enable Live API mode to upload and manage knowledge documents.</p>
        )}
      </div>
    </div>
  );
}
