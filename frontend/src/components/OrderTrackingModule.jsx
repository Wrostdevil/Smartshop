import React, { useState } from 'react';
import { Truck, CheckCircle2, Clock, MapPin, Package, Search, Loader2 } from 'lucide-react';
import { api } from '../lib/api';

export default function OrderTrackingModule({ latestOrderId, isLiveApi }) {
  const [orderIdInput, setOrderIdInput] = useState(latestOrderId || 'ORD-2026-8941');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [activeOrder, setActiveOrder] = useState({
    orderId: latestOrderId || 'ORD-2026-8941',
    date: 'Today, 11:40 AM',
    status: 'IN_TRANSIT',
    currentStep: 3,
    items: [{ name: 'Dell Inspiron 15 AI Edition', qty: 1, price: 949 }],
    trackingHistory: [
      { title: 'Order Placed', time: '11:40 AM', done: true },
      { title: 'Warehouse Processing', time: '11:45 AM', done: true },
      { title: 'Shipped from Distribution Hub', time: '12:15 PM', done: true },
      { title: 'In Transit to Local Fulfillment', time: 'Estimated 3:00 PM', done: false },
      { title: 'Out for Delivery', time: 'Pending', done: false }
    ],
    warehouse: 'East Coast Automated Fulfillment Center (Hub #4)',
    carrier: 'ShopSmart AI Express Logistics'
  });

  // Keep in sync when a fresh checkout sets a new order id.
  React.useEffect(() => {
    if (latestOrderId && latestOrderId !== activeOrder.orderId) {
      setOrderIdInput(latestOrderId);
      lookupOrder(latestOrderId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [latestOrderId]);

  const lookupOrder = async (id) => {
    const target = (id ?? orderIdInput ?? '').trim();
    if (!target) return;
    if (!isLiveApi) {
      setActiveOrder((prev) => ({ ...prev, orderId: target }));
      return;
    }
    setLoading(true);
    setError('');
    try {
      // FastAPI backend: GET {base}/orders/{order_number} (Postgres order + tracking)
      const o = await api.order(target);
      setActiveOrder({
        orderId: o.orderId || o.order_number || target,
        date: o.date || '',
        status: o.status || 'PROCESSING',
        currentStep: o.currentStep ?? 3,
        items: o.items || [],
        trackingHistory: o.trackingHistory?.length ? o.trackingHistory : [
          { title: 'Order Placed', time: o.date || '', done: true },
          { title: 'Warehouse Processing', time: 'Confirmed', done: true },
          { title: 'Shipped from Distribution Hub', time: 'In progress', done: true },
          { title: 'In Transit to Local Fulfillment', time: 'Estimated today', done: false },
          { title: 'Out for Delivery', time: 'Pending', done: false },
        ],
        warehouse: o.warehouse || 'East Coast Automated Fulfillment Center (Hub #4)',
        carrier: o.carrier || 'ShopSmart AI Express Logistics',
        totals: { subtotal: o.subtotal, shipping: o.shipping, tax: o.tax, total: o.total },
      });
    } catch {
      setError(`Order ${target} not found on backend — showing last known status.`);
      setActiveOrder((prev) => ({ ...prev, orderId: target }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="bg-gradient-to-r from-slate-900 via-indigo-900/50 to-slate-900 border border-slate-800 rounded-3xl p-6 relative overflow-hidden">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-xs font-bold text-indigo-400 uppercase tracking-wider">
            <Truck className="w-4 h-4" /> Operations & Fulfillment
          </div>
          <h2 className="text-2xl font-extrabold text-white">Live Order Tracking & Shipment Status</h2>
          <p className="text-xs text-slate-300">Monitor real-time warehouse dispatch and delivery event streams for placed orders.</p>
        </div>
      </div>

      <div className="bg-slate-800/60 border border-slate-700/60 rounded-2xl p-4 flex gap-2">
        <input type="text" value={orderIdInput} onChange={(e) => setOrderIdInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && lookupOrder()}
          placeholder="Enter Order ID (e.g. ORD-2026-8941)..."
          className="flex-1 bg-slate-900 border border-slate-700 rounded-xl px-4 py-2.5 text-xs text-slate-100 font-mono focus:outline-none focus:border-indigo-500" />
        <button onClick={() => lookupOrder()} disabled={loading}
          className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2.5 rounded-xl font-bold text-xs flex items-center gap-1.5 shadow-md disabled:opacity-50">
          {loading ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Search className="w-3.5 h-3.5" />} Track Order
        </button>
      </div>
      {error && <p className="text-xs text-amber-300">{error}</p>}

      {activeOrder && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-6">
          <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 pb-4">
            <div>
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Tracking ID</span>
              <span className="text-lg font-mono font-extrabold text-white">{activeOrder.orderId}</span>
              {activeOrder.totals && (
                <span className="text-[11px] font-mono text-slate-400 block mt-1">
                  ${activeOrder.totals.total} total • {activeOrder.items?.length || 0} item(s) • {activeOrder.date}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              <span className="bg-indigo-500/20 text-indigo-300 font-mono text-xs font-bold px-3 py-1 rounded-full border border-indigo-500/30 flex items-center gap-1.5">
                <Clock className="w-3.5 h-3.5" /> Status: {activeOrder.status}
              </span>
            </div>
          </div>

          {activeOrder.items?.length > 0 && (
            <div className="space-y-1.5">
              {activeOrder.items.map((it, i) => (
                <div key={i} className="flex justify-between text-xs text-slate-300 bg-slate-950 px-3 py-2 rounded-lg border border-slate-800">
                  <span>{it.name} <span className="text-slate-500">× {it.qty}</span></span>
                  <span className="font-mono">${it.price}</span>
                </div>
              ))}
            </div>
          )}

          <div className="py-4">
            <div className="relative flex items-center justify-between">
              <div className="absolute top-1/2 left-0 right-0 h-1 bg-slate-800 -translate-y-1/2 -z-0" />
              <div className="absolute top-1/2 left-0 h-1 bg-indigo-500 -translate-y-1/2 transition-all duration-500"
                style={{ width: `${(activeOrder.currentStep / (activeOrder.trackingHistory.length - 1)) * 100}%` }} />
              {activeOrder.trackingHistory.map((step, idx) => (
                <div key={idx} className="relative z-10 flex flex-col items-center space-y-1">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-xs transition-all ${
                    step.done ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/40'
                      : idx === activeOrder.currentStep ? 'bg-amber-500 text-white animate-pulse ring-4 ring-amber-500/20'
                      : 'bg-slate-800 text-slate-500 border border-slate-700'}`}>
                    {step.done ? <CheckCircle2 className="w-4 h-4" /> : idx + 1}
                  </div>
                  <span className="text-[10px] font-semibold text-slate-300 text-center max-w-[90px]">{step.title}</span>
                  <span className="text-[9px] font-mono text-slate-500">{step.time}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-4 pt-4 border-t border-slate-800 text-xs">
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-slate-400 font-medium flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5 text-rose-400" /> Dispatch Warehouse</span>
              <p className="font-semibold text-slate-200">{activeOrder.warehouse}</p>
            </div>
            <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-1">
              <span className="text-slate-400 font-medium flex items-center gap-1.5"><Package className="w-3.5 h-3.5 text-indigo-400" /> Logistics Partner</span>
              <p className="font-semibold text-slate-200">{activeOrder.carrier}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
