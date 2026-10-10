import React from 'react';
import { Layers, X, ShoppingBag, Check, Star, ArrowLeft } from 'lucide-react';

export default function ComparisonPanel({ comparedProducts, onRemoveFromCompare, onAddToCart, onBackToStore }) {
  if (!comparedProducts || comparedProducts.length === 0) {
    return (
      <div className="max-w-4xl mx-auto py-16 px-4 text-center space-y-4">
        <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto text-indigo-400">
          <Layers className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-slate-100">No Products Selected for Comparison</h2>
        <p className="text-sm text-slate-400 max-w-md mx-auto">
          Browse the storefront catalog and check the <strong>"Compare"</strong> button on up to 4 products to compare their specs side-by-side!
        </p>
        <button
          onClick={onBackToStore}
          className="inline-flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-xl text-xs font-semibold shadow-lg shadow-indigo-600/20"
        >
          <ArrowLeft className="w-4 h-4" /> Return to Catalog
        </button>
      </div>
    );
  }

  // Get all unique spec keys across selected products
  const allSpecKeys = Array.from(
    new Set(comparedProducts.flatMap((p) => Object.keys(p.specs || {})))
  );

  return (
    <div className="space-y-6">
      {/* Top Header */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase tracking-wider">
            <Layers className="w-4 h-4" /> Feature Matrix Comparison
          </div>
          <h2 className="text-2xl font-extrabold text-white">Comparing {comparedProducts.length} Products</h2>
        </div>

        <button
          onClick={onBackToStore}
          className="flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 px-3.5 py-2 rounded-xl text-xs font-semibold transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Store
        </button>
      </div>

      {/* Comparison Table Grid */}
      <div className="overflow-x-auto border border-slate-800 rounded-2xl bg-slate-900/60 backdrop-blur-sm">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-slate-800 bg-slate-950/60">
              <th className="p-4 w-48 font-bold text-slate-400 uppercase tracking-wider">Product Specs</th>
              {comparedProducts.map((prod) => (
                <th key={prod.id} className="p-4 min-w-[220px] relative align-top">
                  <button
                    onClick={() => onRemoveFromCompare(prod.id)}
                    className="absolute top-2 right-2 p-1 rounded-full bg-slate-800 text-slate-400 hover:text-rose-400 hover:bg-slate-700"
                    title="Remove from comparison"
                  >
                    <X className="w-3.5 h-3.5" />
                  </button>

                  <div className="space-y-2 pr-6">
                    <img
                      src={prod.image}
                      alt={prod.name}
                      className="w-full h-28 object-cover rounded-xl border border-slate-800"
                    />
                    <span className="text-[10px] font-bold text-indigo-400 uppercase font-mono block">
                      {prod.brand}
                    </span>
                    <h4 className="font-bold text-slate-100 line-clamp-1">{prod.name}</h4>
                    <div className="font-extrabold font-mono text-base text-white">${prod.price}</div>
                    <button
                      onClick={() => onAddToCart(prod)}
                      className="w-full flex items-center justify-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white py-1.5 rounded-lg text-xs font-semibold"
                    >
                      <ShoppingBag className="w-3.5 h-3.5" /> Add to Cart
                    </button>
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800 text-slate-300">
            {/* Rating */}
            <tr>
              <td className="p-4 font-semibold text-slate-400 bg-slate-950/30">Rating</td>
              {comparedProducts.map((prod) => (
                <td key={prod.id} className="p-4">
                  <div className="flex items-center gap-1 text-amber-400 font-bold font-mono">
                    <Star className="w-3.5 h-3.5 fill-amber-400" />
                    <span>{prod.rating}</span>
                    <span className="text-slate-500 text-[10px]">({prod.reviewCount})</span>
                  </div>
                </td>
              ))}
            </tr>

            {/* Stock */}
            <tr>
              <td className="p-4 font-semibold text-slate-400 bg-slate-950/30">Availability</td>
              {comparedProducts.map((prod) => (
                <td key={prod.id} className="p-4 font-semibold">
                  <span className={prod.availability === 'LOW_STOCK' ? 'text-amber-400' : 'text-emerald-400'}>
                    {prod.availability === 'LOW_STOCK' ? `Low Stock (${prod.stockCount})` : 'In Stock'}
                  </span>
                </td>
              ))}
            </tr>

            {/* Spec rows */}
            {allSpecKeys.map((key) => (
              <tr key={key} className="hover:bg-slate-800/30 transition-colors">
                <td className="p-4 font-semibold text-slate-400 bg-slate-950/30 capitalize">
                  {key.replace(/([A-Z])/g, ' $1')}
                </td>
                {comparedProducts.map((prod) => (
                  <td key={prod.id} className="p-4 font-mono text-slate-200">
                    {prod.specs?.[key] || 'N/A'}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
