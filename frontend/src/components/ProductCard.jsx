import React from 'react';
import { Star, Heart, Layers, ShoppingBag, Sparkles, Check, Info } from 'lucide-react';

export default function ProductCard({
  product,
  onAddToCart,
  onOpenDetails,
  isWishlisted,
  onToggleWishlist,
  isCompared,
  onToggleCompare
}) {
  const isLowStock = product.availability === 'LOW_STOCK';

  return (
    <div className="group bg-slate-800/60 border border-slate-700/70 hover:border-indigo-500/50 rounded-2xl overflow-hidden flex flex-col justify-between transition-all duration-300 hover:shadow-xl hover:shadow-indigo-500/10 hover:-translate-y-1">
      <div>
        {/* Card Header & Image */}
        <div className="relative aspect-[4/3] overflow-hidden bg-slate-900">
          <img
            src={product.image}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />

          {/* Overlay Gradient */}
          <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-transparent to-transparent opacity-60" />

          {/* Badges Bar */}
          <div className="absolute top-3 left-3 right-3 flex justify-between items-start">
            <span
              className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-full border shadow-sm backdrop-blur-md ${
                isLowStock
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                  : 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
              }`}
            >
              {isLowStock ? `Low Stock (${product.stockCount})` : 'In Stock'}
            </span>

            {/* Wishlist Action */}
            <button
              onClick={() => onToggleWishlist(product.id)}
              className={`p-2 rounded-full backdrop-blur-md transition-colors ${
                isWishlisted
                  ? 'bg-rose-500 text-white shadow-lg'
                  : 'bg-slate-900/60 text-slate-300 hover:text-rose-400 hover:bg-slate-900'
              }`}
              title="Add to Wishlist"
            >
              <Heart className={`w-4 h-4 ${isWishlisted ? 'fill-white' : ''}`} />
            </button>
          </div>

          {/* Compare Selector Tag */}
          <div className="absolute bottom-3 left-3">
            <button
              onClick={() => onToggleCompare(product.id)}
              className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-xs font-semibold backdrop-blur-md border transition-all ${
                isCompared
                  ? 'bg-indigo-600 text-white border-indigo-400'
                  : 'bg-slate-900/70 text-slate-300 border-slate-700 hover:border-slate-500'
              }`}
            >
              {isCompared ? <Check className="w-3.5 h-3.5" /> : <Layers className="w-3.5 h-3.5 text-indigo-400" />}
              <span>{isCompared ? 'Comparing' : 'Compare'}</span>
            </button>
          </div>
        </div>

        {/* Card Body */}
        <div className="p-4 space-y-3">
          {/* Brand & Category */}
          <div className="flex items-center justify-between text-[11px]">
            <span className="font-semibold text-indigo-400 uppercase tracking-wider">{product.brand}</span>
            <span className="text-slate-400">{product.category}</span>
          </div>

          {/* Title */}
          <h3 
            onClick={() => onOpenDetails(product)}
            className="font-bold text-slate-100 text-sm line-clamp-1 hover:text-indigo-300 cursor-pointer transition-colors"
          >
            {product.name}
          </h3>

          {/* Rating */}
          <div className="flex items-center gap-2 text-xs">
            <div className="flex items-center text-amber-400 gap-0.5">
              <Star className="w-3.5 h-3.5 fill-amber-400" />
              <span className="font-bold font-mono">{product.rating}</span>
            </div>
            <span className="text-slate-500 text-[11px]">({product.reviewCount} reviews)</span>
          </div>

          {/* AI Key Feature Tag */}
          <div className="bg-slate-900/60 p-2 rounded-xl border border-slate-700/40 text-[11px] text-slate-300 flex items-start gap-2">
            <Sparkles className="w-3.5 h-3.5 text-purple-400 shrink-0 mt-0.5" />
            <p className="line-clamp-2 text-[11px] text-slate-300">
              {product.aiSummary.pros[0]}
            </p>
          </div>
        </div>
      </div>

      {/* Card Footer */}
      <div className="p-4 pt-0 border-t border-slate-700/40 mt-2 flex items-center justify-between gap-3">
        <div>
          <div className="flex items-baseline gap-1.5">
            <span className="font-extrabold text-lg text-slate-100 font-mono">${product.price}</span>
            {product.originalPrice && (
              <span className="text-xs text-slate-500 line-through font-mono">
                ${product.originalPrice}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-1.5">
          <button
            onClick={() => onOpenDetails(product)}
            className="p-2 rounded-xl bg-slate-700/50 hover:bg-slate-700 text-slate-300 transition-colors"
            title="View Full Specs & AI Summary"
          >
            <Info className="w-4 h-4" />
          </button>

          <button
            onClick={() => onAddToCart(product)}
            className="flex items-center gap-1.5 bg-indigo-600 hover:bg-indigo-500 text-white px-3 py-2 rounded-xl font-bold text-xs shadow-md shadow-indigo-600/20 active:scale-95 transition-all"
          >
            <ShoppingBag className="w-3.5 h-3.5" /> Add
          </button>
        </div>
      </div>
    </div>
  );
}
