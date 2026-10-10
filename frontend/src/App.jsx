import React, { useState, useMemo, useEffect, useCallback, useRef } from 'react';
import Header from './components/Header';
import FilterSidebar from './components/FilterSidebar';
import ProductCard from './components/ProductCard';
import ProductDetailModal from './components/ProductDetailModal';
import ComparisonPanel from './components/ComparisonPanel';
import CartDrawer from './components/CartDrawer';
import AIShopperModule from './components/AIShopperModule';
import SupportRAGModule from './components/SupportRAGModule';
import OrderTrackingModule from './components/OrderTrackingModule';
import RAGBotWidget from './components/RAGBotWidget';
import { MOCK_PRODUCTS, USER_PROFILE, CATEGORIES as MOCK_CATS, BRANDS as MOCK_BRANDS } from './data/mockProducts';
import { api, getSessionId, normalizeProduct } from './lib/api';
import { Sparkles } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('store');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLiveApi, setIsLiveApi] = useState(true);
  const [backendUp, setBackendUp] = useState(false);

  // Storefront Filter state
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedBrand, setSelectedBrand] = useState('All');
  const [maxPrice, setMaxPrice] = useState(2000);
  const [inStockOnly, setInStockOnly] = useState(false);
  const [sortBy, setSortBy] = useState('recommended');

  // Live catalog state (falls back to mock when backend unreachable)
  const [liveProducts, setLiveProducts] = useState([]);
  const [catalogMeta, setCatalogMeta] = useState(null);
  const [catalogLoading, setCatalogLoading] = useState(false);
  const [apiError, setApiError] = useState('');

  const [cartItems, setCartItems] = useState([{ ...MOCK_PRODUCTS[0], quantity: 1 }]);
  const [wishlistIds, setWishlistIds] = useState(['LAP101']);
  const [comparedIds, setComparedIds] = useState(['LAP101', 'LAP102']);
  const [selectedDetailProduct, setSelectedDetailProduct] = useState(null);
  const [isCartOpen, setIsCartOpen] = useState(false);
  const [latestOrderId, setLatestOrderId] = useState('ORD-2026-8941');
  const sessionId = useRef(getSessionId());
  const searchTimer = useRef(null);

  const liveMode = isLiveApi && backendUp;
  const catalog = liveMode && liveProducts.length ? liveProducts : MOCK_PRODUCTS;
  const categories = catalogMeta?.categories?.length ? catalogMeta.categories : MOCK_CATS;
  const brands = catalogMeta?.brands?.length ? catalogMeta.brands : MOCK_BRANDS;

  // ---- Backend health probe (auto live/mock) ----
  useEffect(() => {
    let cancelled = false;
    api.health().then((h) => {
      if (cancelled) return;
      setBackendUp(!!h && (h.status === 'ok' || h.status === 'degraded'));
    });
    return () => { cancelled = true; };
  }, []);

  // ---- Catalog meta (categories/brands/price ceiling from Postgres) ----
  useEffect(() => {
    if (!isLiveApi) return;
    api.meta()
      .then((m) => { setCatalogMeta(m); setBackendUp(true); if (m?.priceCeil) setMaxPrice((prev) => Math.max(prev, 0) || m.priceCeil); })
      .catch(() => setBackendUp(false));
  }, [isLiveApi]);

  // ---- Catalog fetch (debounced; server-side filter/sort via Postgres) ----
  const fetchCatalog = useCallback(() => {
    if (!isLiveApi) return;
    setCatalogLoading(true);
    api.products({
      search: searchQuery.trim() || undefined,
      category: selectedCategory,
      brand: selectedBrand,
      max_price: maxPrice,
      in_stock_only: inStockOnly || undefined,
      sort: sortBy,
      limit: 50,
    })
      .then((body) => {
        setLiveProducts((body.products || []).map(normalizeProduct));
        setBackendUp(true);
        setApiError('');
      })
      .catch((e) => {
        setBackendUp(false);
        setApiError('Backend unreachable — showing local catalog.');
      })
      .finally(() => setCatalogLoading(false));
  }, [isLiveApi, searchQuery, selectedCategory, selectedBrand, maxPrice, inStockOnly, sortBy]);

  useEffect(() => {
    if (!isLiveApi) return;
    clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(fetchCatalog, 250);
    return () => clearTimeout(searchTimer.current);
  }, [fetchCatalog, isLiveApi]);

  // ---- Backend cart sync (session cart persisted in Postgres) ----
  const syncCartFromBackend = useCallback(async () => {
    if (!isLiveApi) return;
    try {
      const cart = await api.cart(sessionId.current);
      setBackendUp(true);
      const bySlug = new Map(catalog.map((p) => [p.slug || p.id, p]));
      const items = (cart.items || []).map((it) => {
        const full = bySlug.get(it.product_slug) || MOCK_PRODUCTS.find((p) => p.id === it.product_slug);
        return { ...(full || { id: it.product_slug, slug: it.product_slug, name: it.name, image: it.image, price: it.price, specs: {}, aiSummary: { pros: [], cons: [] } }), price: it.price, quantity: it.quantity };
      });
      setCartItems(items);
    } catch { setBackendUp(false); }
  }, [isLiveApi, catalog]);

  useEffect(() => { syncCartFromBackend(); }, [syncCartFromBackend]);

  // ---- Client-side filter (mock mode OR live empty fallback) ----
  const filteredProducts = useMemo(() => {
    if (liveMode && liveProducts.length) return liveProducts; // already server-filtered
    return MOCK_PRODUCTS.filter((prod) => {
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const hit = prod.name.toLowerCase().includes(q) || prod.brand.toLowerCase().includes(q)
          || prod.category.toLowerCase().includes(q) || prod.tags?.some((t) => t.toLowerCase().includes(q));
        if (!hit) return false;
      }
      if (selectedCategory !== 'All' && prod.category !== selectedCategory) return false;
      if (selectedBrand !== 'All' && prod.brand !== selectedBrand) return false;
      if (prod.price > maxPrice) return false;
      if (inStockOnly && prod.availability === 'OUT_OF_STOCK') return false;
      return true;
    }).sort((a, b) => {
      if (sortBy === 'price-low') return a.price - b.price;
      if (sortBy === 'price-high') return b.price - a.price;
      if (sortBy === 'rating') return b.rating - a.rating;
      return 0;
    });
  }, [liveMode, liveProducts, searchQuery, selectedCategory, selectedBrand, maxPrice, inStockOnly, sortBy]);

  // ---- Cart actions (live: Postgres session cart; mock: local state) ----
  const handleAddToCart = async (product) => {
    const slug = product.slug || product.id;
    if (liveMode) {
      try {
        const cart = await api.cartAdd(sessionId.current, slug, 1);
        setBackendUp(true);
        const bySlug = new Map(catalog.map((p) => [p.slug || p.id, p]));
        setCartItems((cart.items || []).map((it) => ({ ...(bySlug.get(it.product_slug) || product), price: it.price, quantity: it.quantity })));
        setIsCartOpen(true);
        return;
      } catch { setBackendUp(false); }
    }
    setCartItems((prev) => {
      const existing = prev.find((item) => (item.slug || item.id) === slug);
      if (existing) return prev.map((item) => ((item.slug || item.id) === slug ? { ...item, quantity: item.quantity + 1 } : item));
      return [...prev, { ...product, quantity: 1 }];
    });
    setIsCartOpen(true);
  };

  const handleUpdateQuantity = async (productId, newQty) => {
    const item = cartItems.find((i) => (i.slug || i.id) === productId);
    const slug = item?.slug || productId;
    if (liveMode) {
      try {
        const cart = newQty <= 0 ? await api.cartRemove(sessionId.current, slug) : await api.cartUpdate(sessionId.current, slug, newQty);
        const bySlug = new Map(catalog.map((p) => [p.slug || p.id, p]));
        setCartItems((cart.items || []).map((it) => ({ ...(bySlug.get(it.product_slug) || item), price: it.price, quantity: it.quantity })));
        return;
      } catch { setBackendUp(false); }
    }
    if (newQty <= 0) { handleRemoveCartItem(productId); return; }
    setCartItems((prev) => prev.map((i) => ((i.slug || i.id) === productId ? { ...i, quantity: newQty } : i)));
  };

  const handleRemoveCartItem = async (productId) => {
    const item = cartItems.find((i) => (i.slug || i.id) === productId);
    if (liveMode && item) {
      try {
        const cart = await api.cartRemove(sessionId.current, item.slug || productId);
        const bySlug = new Map(catalog.map((p) => [p.slug || p.id, p]));
        setCartItems((cart.items || []).map((it) => ({ ...(bySlug.get(it.product_slug) || item), price: it.price, quantity: it.quantity })));
        return;
      } catch { setBackendUp(false); }
    }
    setCartItems((prev) => prev.filter((i) => (i.slug || i.id) !== productId));
  };

  const handleToggleWishlist = (productId) => {
    setWishlistIds((prev) => (prev.includes(productId) ? prev.filter((id) => id !== productId) : [...prev, productId]));
  };

  const handleToggleCompare = (productId) => {
    setComparedIds((prev) => {
      if (prev.includes(productId)) return prev.filter((id) => id !== productId);
      if (prev.length >= 4) { alert('You can compare a maximum of 4 products at a time.'); return prev; }
      return [...prev, productId];
    });
  };

  const handleResetFilters = () => {
    setSelectedCategory('All');
    setSelectedBrand('All');
    setMaxPrice(catalogMeta?.priceCeil || 2000);
    setInStockOnly(false);
    setSearchQuery('');
  };

  // ---- Checkout (live: POST /orders/checkout -> Postgres order + tracking) ----
  const handleCheckout = async () => {
    if (liveMode && cartItems.length) {
      try {
        const order = await api.checkout(
          sessionId.current,
          cartItems.map((i) => ({ product_slug: i.slug || i.id, quantity: i.quantity })),
          true,
        );
        setLatestOrderId(order.orderId || order.order_number);
        setCartItems([]);
        setIsCartOpen(false);
        setActiveTab('orders');
        return;
      } catch (e) { setBackendUp(false); }
    }
    const newOrd = `ORD-2026-${Math.floor(1000 + Math.random() * 9000)}`;
    setLatestOrderId(newOrd);
    setCartItems([]);
    setIsCartOpen(false);
    setActiveTab('orders');
  };

  const comparedProducts = useMemo(() => catalog.filter((p) => comparedIds.includes(p.id || p.slug)), [catalog, comparedIds]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        cartCount={cartItems.reduce((acc, i) => acc + i.quantity, 0)}
        wishlistCount={wishlistIds.length}
        compareCount={comparedIds.length}
        setIsCartOpen={setIsCartOpen}
        isLiveApi={isLiveApi}
        backendUp={backendUp}
        setIsLiveApi={setIsLiveApi}
        userProfile={USER_PROFILE}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6 space-y-6">
        {apiError && isLiveApi && (
          <div className="bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs px-4 py-2 rounded-xl">{apiError}</div>
        )}
        {activeTab === 'store' && (
          <div className="space-y-6">
            <div className="relative bg-gradient-to-r from-indigo-900/60 via-purple-900/40 to-slate-900 border border-indigo-500/20 rounded-3xl p-6 sm:p-8 overflow-hidden backdrop-blur-md">
              <div className="relative z-10 max-w-2xl space-y-3">
                <div className="inline-flex items-center gap-1.5 bg-indigo-500/20 text-indigo-300 text-xs font-semibold px-3 py-1 rounded-full border border-indigo-500/30">
                  <Sparkles className="w-3.5 h-3.5 text-amber-400 animate-pulse" />
                  {liveMode ? 'Postgres + RAG Backend Connected' : 'ShopSmart AI Co-Pilot Available'}
                </div>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
                  Discover Products Powered by Intent & Agentic AI
                </h1>
                <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
                  Browse our catalog with intelligent filters or ask our AI Shopping Co-Pilot to analyze your technical specs and budget requirements.
                </p>
                <div className="pt-2 flex flex-wrap items-center gap-3">
                  <button onClick={() => setActiveTab('ai-shopper')} className="flex items-center gap-2 bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white px-4 py-2.5 rounded-xl font-bold text-xs shadow-lg shadow-purple-600/30 transition-all active:scale-95">
                    <Sparkles className="w-4 h-4 text-amber-400" /> Launch AI Shopper
                  </button>
                  <button onClick={() => setActiveTab('support')} className="flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-slate-200 px-4 py-2.5 rounded-xl font-semibold text-xs transition-colors">
                    View Policy RAG Assistant
                  </button>
                </div>
              </div>
            </div>

            <div className="flex flex-col lg:flex-row gap-6">
              <FilterSidebar
                selectedCategory={selectedCategory}
                setSelectedCategory={setSelectedCategory}
                selectedBrand={selectedBrand}
                setSelectedBrand={setSelectedBrand}
                maxPrice={maxPrice}
                setMaxPrice={setMaxPrice}
                inStockOnly={inStockOnly}
                setInStockOnly={setInStockOnly}
                resetFilters={handleResetFilters}
                categories={categories}
                brands={brands}
                priceCeil={catalogMeta?.priceCeil || 2000}
              />

              <div className="flex-1 space-y-4">
                <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center justify-between gap-4">
                  <div className="text-xs text-slate-400 font-medium">
                    Showing <strong className="text-slate-100">{filteredProducts.length}</strong> products
                    {catalogLoading && <span className="ml-2 text-indigo-400">syncing…</span>}
                  </div>
                  <div className="flex items-center gap-2">
                    <label className="text-xs text-slate-400 font-medium">Sort by:</label>
                    <select value={sortBy} onChange={(e) => setSortBy(e.target.value)} className="bg-slate-800 border border-slate-700 rounded-xl px-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500">
                      <option value="recommended">Featured / AI Recommended</option>
                      <option value="price-low">Price: Low to High</option>
                      <option value="price-high">Price: High to Low</option>
                      <option value="rating">Highest Customer Rating</option>
                    </select>
                  </div>
                </div>

                {filteredProducts.length === 0 ? (
                  <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-12 text-center space-y-3">
                    <p className="text-slate-400 text-sm">No products match your current search filters.</p>
                    <button onClick={handleResetFilters} className="text-xs text-indigo-400 font-bold hover:underline">Reset All Filters</button>
                  </div>
                ) : (
                  <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-5">
                    {filteredProducts.map((product) => (
                      <ProductCard
                        key={product.slug || product.id}
                        product={product}
                        onAddToCart={handleAddToCart}
                        onOpenDetails={setSelectedDetailProduct}
                        isWishlisted={wishlistIds.includes(product.id)}
                        onToggleWishlist={handleToggleWishlist}
                        isCompared={comparedIds.includes(product.id)}
                        onToggleCompare={handleToggleCompare}
                      />
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'ai-shopper' && (
          <AIShopperModule onAddToCart={handleAddToCart} onToggleCompare={handleToggleCompare} comparedIds={comparedIds} isLiveApi={liveMode} catalog={catalog} />
        )}
        {activeTab === 'support' && <SupportRAGModule isLiveApi={liveMode} />}
        {activeTab === 'compare' && (
          <ComparisonPanel comparedProducts={comparedProducts} onRemoveFromCompare={handleToggleCompare} onAddToCart={handleAddToCart} onBackToStore={() => setActiveTab('store')} />
        )}
        {activeTab === 'orders' && <OrderTrackingModule latestOrderId={latestOrderId} isLiveApi={liveMode} />}
      </main>

      <ProductDetailModal product={selectedDetailProduct} onClose={() => setSelectedDetailProduct(null)} onAddToCart={handleAddToCart} />
      <CartDrawer isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} cartItems={cartItems} onUpdateQuantity={handleUpdateQuantity} onRemoveItem={handleRemoveCartItem} onCheckout={handleCheckout} userProfile={USER_PROFILE} />

      {/* Floating RAG Bot Widget - Always available on all pages */}
      <RAGBotWidget isLiveApi={isLiveApi} backendUp={backendUp} />

      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-center text-xs text-slate-500">
        ShopSmart AI Autonomous Platform • Hackathon Edition {liveMode ? '• Postgres + RAG live' : '• Mock mode'}
      </footer>
    </div>
  );
}
