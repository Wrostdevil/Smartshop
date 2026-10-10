import React from 'react';
import { 
  ShoppingBag, 
  Sparkles, 
  BookOpen, 
  Truck, 
  Heart, 
  SlidersHorizontal, 
  Search, 
  Crown, 
  Layers, 
  Server,
  Zap
} from 'lucide-react';

export default function Header({
  activeTab,
  setActiveTab,
  searchQuery,
  setSearchQuery,
  cartCount,
  wishlistCount,
  compareCount,
  setIsCartOpen,
  isLiveApi,
  backendUp,
  setIsLiveApi,
  userProfile
}) {
  const liveMode = isLiveApi && backendUp;
  return (
    <header className="sticky top-0 z-40 bg-slate-900/90 backdrop-blur-md border-b border-slate-800">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-indigo-900 via-purple-900 to-slate-900 px-4 py-1.5 text-xs text-slate-300 flex justify-between items-center border-b border-indigo-500/20">
        <div className="flex items-center gap-2">
          <span className="bg-indigo-500/20 text-indigo-300 font-semibold px-2 py-0.5 rounded border border-indigo-500/30 flex items-center gap-1">
            <Zap className="w-3 h-3 text-indigo-400 fill-indigo-400" /> Hackathon Demo
          </span>
          <span className="hidden sm:inline">ShopSmart AI Autonomous Platform</span>
        </div>
        
        {/* Backend API Toggle */}
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 bg-slate-800/80 px-2 py-1 rounded-full border border-slate-700">
            <Server className={`w-3.5 h-3.5 ${liveMode ? 'text-emerald-400' : 'text-amber-400'}`} />
            <span className="text-[11px] text-slate-300 font-medium">
              {liveMode ? 'FastAPI Connected' : isLiveApi ? 'Backend Offline' : 'Mock Data Mode'}
            </span>
            <button
              onClick={() => setIsLiveApi(!isLiveApi)}
              className={`w-7 h-4 flex items-center rounded-full p-0.5 transition-colors ${
                isLiveApi ? 'bg-emerald-600' : 'bg-slate-700'
              }`}
              title="Toggle between FastAPI Backend and Local Mock Data"
            >
              <div
                className={`bg-white w-3 h-3 rounded-full shadow-md transform transition-transform ${
                  isLiveApi ? 'translate-x-3' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* User Tier Pill */}
          <div className="flex items-center gap-1.5 bg-amber-500/10 text-amber-300 border border-amber-500/30 px-2 py-0.5 rounded-full font-medium">
            <Crown className="w-3.5 h-3.5 text-amber-400" />
            <span>{userProfile.tier} Member</span>
          </div>
        </div>
      </div>

      {/* Main Header Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-3.5 flex items-center justify-between gap-4">
        {/* Logo */}
        <div 
          onClick={() => setActiveTab('store')}
          className="flex items-center gap-2.5 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center shadow-lg shadow-indigo-500/25 group-hover:scale-105 transition-transform">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center gap-1">
              <span className="font-extrabold text-xl bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                ShopSmart
              </span>
              <span className="text-xs bg-indigo-500/20 text-indigo-300 px-1.5 py-0.5 rounded font-mono font-semibold border border-indigo-500/30">
                AI
              </span>
            </div>
            <p className="text-[11px] text-slate-400 -mt-1 font-medium">Autonomous Shopping Platform</p>
          </div>
        </div>

        {/* Global Search Bar */}
        <div className="flex-1 max-w-md hidden md:block relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search products, brands, specs or ask AI..."
            className="w-full bg-slate-800/80 border border-slate-700 rounded-xl pl-10 pr-4 py-2 text-sm text-slate-200 placeholder-slate-400 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all"
          />
        </div>

        {/* Navigation Tabs */}
        <nav className="hidden lg:flex items-center bg-slate-800/60 p-1 rounded-xl border border-slate-700/60">
          <button
            onClick={() => setActiveTab('store')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'store'
                ? 'bg-indigo-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            <ShoppingBag className="w-3.5 h-3.5" /> Storefront
          </button>
          
          <button
            onClick={() => setActiveTab('ai-shopper')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'ai-shopper'
                ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-pulse" /> AI Shopper
          </button>

          <button
            onClick={() => setActiveTab('support')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'support'
                ? 'bg-indigo-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" /> Policy RAG
          </button>

          <button
            onClick={() => setActiveTab('orders')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              activeTab === 'orders'
                ? 'bg-indigo-600 text-white shadow'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
            }`}
          >
            <Truck className="w-3.5 h-3.5" /> Order Tracking
          </button>
        </nav>

        {/* User Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Wishlist */}
          <button 
            className="p-2 rounded-xl text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition-colors relative"
            title="Wishlist"
          >
            <Heart className="w-5 h-5" />
            {wishlistCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-rose-500 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                {wishlistCount}
              </span>
            )}
          </button>

          {/* Compare */}
          <button
            onClick={() => setActiveTab('compare')}
            className={`p-2 rounded-xl transition-colors relative ${
              compareCount > 0 ? 'text-indigo-400 bg-indigo-500/10' : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
            }`}
            title="Compare Products"
          >
            <Layers className="w-5 h-5" />
            {compareCount > 0 && (
              <span className="absolute -top-1 -right-1 bg-indigo-500 text-white text-[10px] font-bold w-4 h-4 rounded-full flex items-center justify-center">
                {compareCount}
              </span>
            )}
          </button>

          {/* Cart Button */}
          <button
            onClick={() => setIsCartOpen(true)}
            className="flex items-center gap-2 bg-indigo-600 hover:bg-indigo-500 text-white px-3.5 py-2 rounded-xl font-semibold text-xs transition-all shadow-lg shadow-indigo-600/20 active:scale-95"
          >
            <ShoppingBag className="w-4 h-4" />
            <span className="hidden sm:inline">Cart</span>
            <span className="bg-indigo-950/60 px-1.5 py-0.5 rounded-md text-[11px] font-mono">
              {cartCount}
            </span>
          </button>
        </div>
      </div>

      {/* Mobile Tab Bar */}
      <div className="lg:hidden flex border-t border-slate-800 bg-slate-900/95 px-2 py-1.5 justify-around">
        <button
          onClick={() => setActiveTab('store')}
          className={`flex flex-col items-center gap-0.5 text-[10px] font-medium ${
            activeTab === 'store' ? 'text-indigo-400' : 'text-slate-400'
          }`}
        >
          <ShoppingBag className="w-4 h-4" /> Store
        </button>
        <button
          onClick={() => setActiveTab('ai-shopper')}
          className={`flex flex-col items-center gap-0.5 text-[10px] font-medium ${
            activeTab === 'ai-shopper' ? 'text-purple-400' : 'text-slate-400'
          }`}
        >
          <Sparkles className="w-4 h-4 text-amber-400" /> AI Assistant
        </button>
        <button
          onClick={() => setActiveTab('support')}
          className={`flex flex-col items-center gap-0.5 text-[10px] font-medium ${
            activeTab === 'support' ? 'text-indigo-400' : 'text-slate-400'
          }`}
        >
          <BookOpen className="w-4 h-4" /> Knowledge
        </button>
        <button
          onClick={() => setActiveTab('orders')}
          className={`flex flex-col items-center gap-0.5 text-[10px] font-medium ${
            activeTab === 'orders' ? 'text-indigo-400' : 'text-slate-400'
          }`}
        >
          <Truck className="w-4 h-4" /> Orders
        </button>
      </div>
    </header>
  );
}
