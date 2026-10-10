/**
 * Central ShopSmart API client.
 * Base defaults to relative `/api` (Vite proxy in dev, nginx in compose).
 * Override with VITE_API_URL=http://localhost:8000 for direct calls.
 * Every helper falls back to `null` on network failure so UI can use mock data.
 */
const RAW_BASE = (import.meta.env.VITE_API_URL ?? '/api').replace(/\/$/, '');

async function req(path, opts = {}) {
  const url = `${RAW_BASE}${path}`;
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), 12000);
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      signal: ctrl.signal,
      ...opts,
      headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
    });
    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`API ${res.status}: ${text.slice(0, 200)}`);
    }
    return await res.json();
  } finally {
    clearTimeout(t);
  }
}

export const api = {
  base: RAW_BASE,
  health: () => req('/health').catch(() => null),
  products: (params = {}) => {
    const q = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v === undefined || v === null || v === '' || v === 'All') continue;
      q.set(k, String(v));
    }
    const qs = q.toString();
    return req(`/products${qs ? `?${qs}` : ''}`);
  },
  product: (slug) => req(`/products/${encodeURIComponent(slug)}`),
  meta: () => req('/products/meta'),
  recommend: (query, extra = {}) => req('/recommend', { method: 'POST', body: JSON.stringify({ query, ...extra }) }),
  ragQuery: (query) => req('/rag-query', { method: 'POST', body: JSON.stringify({ query }) }),
  policies: () => req('/policies').catch(() => []),
  documents: () => req('/documents').catch(() => []),
  uploadDocument: async (file, meta = {}) => {
    const form = new FormData();
    form.append('file', file);
    for (const [k, v] of Object.entries(meta)) form.append(k, v);
    const res = await fetch(`${RAW_BASE}/documents/upload`, { method: 'POST', body: form });
    if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
    return res.json();
  },
  cart: (sid) => req(`/cart/${encodeURIComponent(sid)}`),
  cartAdd: (sid, product_slug, quantity = 1) =>
    req(`/cart/${encodeURIComponent(sid)}/items`, { method: 'POST', body: JSON.stringify({ product_slug, quantity }) }),
  cartUpdate: (sid, slug, quantity) =>
    req(`/cart/${encodeURIComponent(sid)}/items/${encodeURIComponent(slug)}`, { method: 'PUT', body: JSON.stringify({ quantity }) }),
  cartRemove: (sid, slug) =>
    req(`/cart/${encodeURIComponent(sid)}/items/${encodeURIComponent(slug)}`, { method: 'DELETE' }),
  cartClear: (sid) => req(`/cart/${encodeURIComponent(sid)}`, { method: 'DELETE' }),
  checkout: (session_id, items, is_prime = true) =>
    req('/orders/checkout', { method: 'POST', body: JSON.stringify({ session_id, items, is_prime }) }),
  order: (orderNumber) => req(`/orders/${encodeURIComponent(orderNumber)}`),
  ticket: (payload) => req('/ticket', { method: 'POST', body: JSON.stringify(payload) }),
};

/** Stable guest session id persisted in localStorage. */
export function getSessionId() {
  let sid = localStorage.getItem('shopsmart_sid');
  if (!sid) {
    sid = `guest-${Math.random().toString(36).slice(2, 10)}`;
    localStorage.setItem('shopsmart_sid', sid);
  }
  return sid;
}

/** Backend product shape already matches the storefront; normalize defensively. */
export function normalizeProduct(p) {
  return {
    id: p.slug ?? p.id,
    slug: p.slug ?? p.id,
    name: p.name ?? p.product_name ?? 'Unnamed',
    brand: p.brand ?? '',
    category: p.category ?? 'General',
    price: Number(p.price ?? 0),
    originalPrice: p.originalPrice ?? p.original_price ?? null,
    rating: Number(p.rating ?? 4.5),
    reviewCount: p.reviewCount ?? p.review_count ?? 0,
    availability: p.availability ?? 'IN_STOCK',
    stockCount: p.stockCount ?? p.stock_count ?? 0,
    image: p.image ?? p.image_url ?? '',
    description: p.description ?? p.blurb ?? '',
    specs: p.specs ?? {},
    aiSummary: p.aiSummary ?? { pros: [], cons: [] },
    tags: p.tags ?? [],
  };
}
