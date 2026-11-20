"use client";

import React, { useState } from "react";
import Link from "next/link";
import { CreditCard, ArrowLeft, CheckCircle2, AlertTriangle } from "lucide-react";

export default function PlaygroundCheckoutPage() {
  const [quantity, setQuantity] = useState("1");
  const [card, setCard] = useState("4111 2222 3333 4444");
  const [orderCount, setOrderCount] = useState(0);
  const [lastTotal, setLastTotal] = useState<number | null>(null);

  // [INTENTIONAL DEFECT: No debouncing / disabled lock on place order button]
  // Allows rapid double-clicks to submit duplicate orders
  const handlePlaceOrder = () => {
    const q = parseInt(quantity, 10) || 0;
    // [INTENTIONAL DEFECT: Business logic bypass accepts negative quantity]
    const total = q * 499.0;
    setOrderCount((c) => c + 1);
    setLastTotal(total);
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 05]: BUTTON DUPING & LOGIC BUG
        </span>
      </header>

      <main className="max-w-xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex items-center gap-2 border-b-2 border-black pb-3 mb-5">
          <CreditCard size={18} />
          <h1 className="font-mono font-black text-base uppercase">Secure Express Checkout</h1>
        </div>

        {orderCount > 0 && (
          <div id="order-success-msg" className="mb-4 p-3 bg-emerald-50 border border-emerald-600 font-mono text-xs">
            <p className="font-bold text-emerald-900">
              ✓ Order Submitted! Total Submissions Registered: {orderCount}
            </p>
            <p className="text-neutral-700">Computed Grand Total: ${lastTotal?.toFixed(2)}</p>
            {lastTotal !== null && lastTotal < 0 && (
              <p className="text-red-700 font-bold mt-1">
                [LOGIC FLAW EXPLOITED]: Negative grand total accepted (${lastTotal.toFixed(2)})!
              </p>
            )}
            {orderCount > 1 && (
              <p className="text-red-700 font-bold mt-1">
                [BUTTON DUPING EXPLOITED]: {orderCount} duplicate orders placed without debouncing!
              </p>
            )}
          </div>
        )}

        <div className="space-y-4">
          <div>
            <label className="block font-mono text-xs font-bold mb-1" htmlFor="input-qty">
              Item Quantity (Try Negative Value e.g. -2)
            </label>
            <input
              id="input-qty"
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="w-full border-2 border-black p-2 font-mono text-xs focus:outline-none"
            />
          </div>

          <div>
            <label className="block font-mono text-xs font-bold mb-1" htmlFor="input-card">
              Payment Card Number
            </label>
            <input
              id="input-card"
              type="text"
              value={card}
              onChange={(e) => setCard(e.target.value)}
              className="w-full border-2 border-black p-2 font-mono text-xs focus:outline-none"
            />
          </div>

          <div className="pt-2 border-t border-black flex items-center justify-between font-mono text-xs">
            <span>Item Price: $499.00 each</span>
            <span className="font-black text-sm">
              Estimated: ${((parseInt(quantity, 10) || 0) * 499).toFixed(2)}
            </span>
          </div>

          {/* [INTENTIONAL DEFECT: Button is never disabled during submission; allows duplicate clicks] */}
          <button
            id="btn-place-order"
            type="button"
            onClick={handlePlaceOrder}
            className="w-full bg-black text-white hover:bg-neutral-800 transition font-mono text-xs font-bold py-3 uppercase tracking-wider"
          >
            Place Instant Order
          </button>
        </div>
      </main>
    </div>
  );
}
