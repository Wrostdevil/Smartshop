import React from 'react';
import { Filter, RotateCcw, Check, DollarSign, Tag, ShieldCheck } from 'lucide-react';
import { CATEGORIES as FALLBACK_CATS, BRANDS as FALLBACK_BRANDS } from '../data/mockProducts';

export default function FilterSidebar({
  selectedCategory,
  setSelectedCategory,
  selectedBrand,
  setSelectedBrand,
  maxPrice,
  setMaxPrice,
  inStockOnly,
  setInStockOnly,
  resetFilters,
  categories,
  brands,
  priceCeil = 2000,
}) {
  const cats = categories?.length ? categories : FALLBACK_CATS;
  const brandList = brands?.length ? brands : FALLBACK_BRANDS;
  return (
    <aside className="w-full lg:w-64 bg-slate-800/40 border border-slate-700/60 rounded-2xl p-5 space-y-6 backdrop-blur-sm">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-slate-700/60 pb-3">
        <div className="flex items-center gap-2 font-bold text-slate-200 text-sm">
          <Filter className="w-4 h-4 text-indigo-400" />
          <span>Filter Catalog</span>
        </div>
        <button
          onClick={resetFilters}
          className="text-xs text-slate-400 hover:text-indigo-300 flex items-center gap-1 transition-colors"
          title="Reset all filters"
        >
          <RotateCcw className="w-3 h-3" /> Reset
        </button>
      </div>

      {/* Category Filter */}
      <div className="space-y-2.5">
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
          <Tag className="w-3.5 h-3.5 text-indigo-400" /> Categories
        </label>
        <div className="space-y-1">
          {cats.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`w-full text-left px-3 py-2 rounded-xl text-xs font-medium transition-all flex items-center justify-between ${
                selectedCategory === cat
                  ? 'bg-indigo-600/90 text-white font-bold shadow-sm'
                  : 'text-slate-300 hover:bg-slate-700/50 hover:text-white'
              }`}
            >
              <span>{cat}</span>
              {selectedCategory === cat && <Check className="w-3.5 h-3.5 text-white" />}
            </button>
          ))}
        </div>
      </div>

      {/* Price Range Slider */}
      <div className="space-y-3 border-t border-slate-700/60 pt-4">
        <div className="flex items-center justify-between">
          <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <DollarSign className="w-3.5 h-3.5 text-indigo-400" /> Max Price
          </label>
          <span className="text-xs font-mono font-bold text-indigo-400 bg-indigo-500/10 px-2 py-0.5 rounded border border-indigo-500/20">
            ${maxPrice}
          </span>
        </div>
        <input
          type="range"
          min="200"
          max={priceCeil}
          step="50"
          value={Math.min(maxPrice, priceCeil)}
          onChange={(e) => setMaxPrice(Number(e.target.value))}
          className="w-full accent-indigo-500 bg-slate-700 h-1.5 rounded-lg cursor-pointer"
        />
        <div className="flex justify-between text-[10px] text-slate-500 font-mono">
          <span>$200</span>
          <span>${priceCeil}</span>
        </div>
      </div>

      {/* Brand Selector */}
      <div className="space-y-2.5 border-t border-slate-700/60 pt-4">
        <label className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
          Brand
        </label>
        <select
          value={selectedBrand}
          onChange={(e) => setSelectedBrand(e.target.value)}
          className="w-full bg-slate-900 border border-slate-700 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
        >
          {brandList.map((brand) => (
            <option key={brand} value={brand}>
              {brand}
            </option>
          ))}
        </select>
      </div>

      {/* Stock Availability Toggle */}
      <div className="border-t border-slate-700/60 pt-4">
        <label className="flex items-center justify-between cursor-pointer group">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-medium text-slate-300 group-hover:text-white transition-colors">
              In Stock Only
            </span>
          </div>
          <input
            type="checkbox"
            checked={inStockOnly}
            onChange={(e) => setInStockOnly(e.target.checked)}
            className="w-4 h-4 accent-indigo-600 rounded bg-slate-900 border-slate-700 cursor-pointer"
          />
        </label>
      </div>
    </aside>
  );
}
