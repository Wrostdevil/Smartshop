import React from 'react';
import { X, Star, Sparkles, CheckCircle2, AlertCircle, ShoppingBag, ShieldCheck } from 'lucide-react';

export default function ProductDetailModal({ product, onClose, onAddToCart }) {
  if (!product) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
      <div className="bg-slate-900 border border-slate-800 rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl relative">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 rounded-full bg-slate-800/80 text-slate-400 hover:text-white hover:bg-slate-700 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header / Banner Image */}
        <div className="relative h-64 bg-slate-950 overflow-hidden">
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-slate-900/40 to-transparent" />
          
          <div className="absolute bottom-4 left-6 right-6 flex justify-between items-end">
            <div>
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-400 font-mono">
                {product.brand} • {product.category}
              </span>
              <h2 className="text-2xl font-extrabold text-white mt-0.5">{product.name}</h2>
            </div>
            <div className="text-right">
              <span className="text-2xl font-extrabold font-mono text-white">${product.price}</span>
            </div>
          </div>
        </div>

        {/* Body Content */}
        <div className="p-6 space-y-6">
          {/* Rating & Stock Badges */}
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div className="flex items-center gap-2">
              <div className="flex items-center text-amber-400 gap-1">
                <Star className="w-4 h-4 fill-amber-400" />
                <span className="font-bold font-mono text-sm">{product.rating}</span>
              </div>
              <span className="text-slate-400 text-xs">({product.reviewCount} verified ratings)</span>
            </div>

            <div className="flex items-center gap-2">
              <span className="flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                <ShieldCheck className="w-3.5 h-3.5" />
                {product.availability === 'LOW_STOCK' ? `Only ${product.stockCount} units remaining` : 'In Stock & Ready to Ship'}
              </span>
            </div>
          </div>

          {/* Description */}
          <div>
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-1">Product Overview</h4>
            <p className="text-sm text-slate-300 leading-relaxed">{product.description}</p>
          </div>

          {/* AI Pros & Cons Summary Card */}
          <div className="bg-gradient-to-br from-indigo-950/40 via-purple-950/20 to-slate-900 p-4 rounded-2xl border border-indigo-500/30 space-y-3">
            <div className="flex items-center gap-2 text-indigo-300 font-bold text-xs">
              <Sparkles className="w-4 h-4 text-amber-400 animate-pulse" />
              <span>ShopSmart AI Verdict & Analysis</span>
            </div>

            <div className="grid sm:grid-cols-2 gap-3 text-xs">
              {/* Pros */}
              <div className="space-y-1.5">
                <span className="text-emerald-400 font-semibold flex items-center gap-1">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Strengths
                </span>
                <ul className="space-y-1 text-slate-300">
                  {product.aiSummary.pros.map((pro, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-emerald-400 font-bold">•</span>
                      <span>{pro}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Cons */}
              <div className="space-y-1.5">
                <span className="text-amber-400 font-semibold flex items-center gap-1">
                  <AlertCircle className="w-3.5 h-3.5" /> Considerations
                </span>
                <ul className="space-y-1 text-slate-300">
                  {product.aiSummary.cons.map((con, idx) => (
                    <li key={idx} className="flex items-start gap-1.5">
                      <span className="text-amber-400 font-bold">•</span>
                      <span>{con}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Technical Specifications Table */}
          <div className="space-y-2">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400">Technical Specifications</h4>
            <div className="bg-slate-950 rounded-2xl overflow-hidden border border-slate-800 divide-y divide-slate-800 text-xs">
              {Object.entries(product.specs).map(([key, val]) => (
                <div key={key} className="flex px-4 py-2.5">
                  <span className="w-1/3 font-semibold text-slate-400 capitalize">
                    {key.replace(/([A-Z])/g, ' $1')}
                  </span>
                  <span className="w-2/3 text-slate-200 font-mono">{val}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Tags */}
          {product.tags && (
            <div className="flex flex-wrap gap-1.5 pt-2">
              {product.tags.map((tag) => (
                <span key={tag} className="text-[11px] bg-slate-800 text-slate-300 px-2.5 py-1 rounded-lg border border-slate-700">
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="p-4 bg-slate-950 border-t border-slate-800 flex items-center justify-between gap-4">
          <div>
            <span className="text-xs text-slate-400 block">Total Price</span>
            <span className="text-xl font-extrabold font-mono text-white">${product.price}</span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={onClose}
              className="px-4 py-2.5 rounded-xl bg-slate-800 text-slate-300 font-semibold text-xs hover:bg-slate-700 transition-colors"
            >
              Close
            </button>
            <button
              onClick={() => {
                onAddToCart(product);
                onClose();
              }}
              className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all active:scale-95"
            >
              <ShoppingBag className="w-4 h-4" /> Add to Shopping Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
