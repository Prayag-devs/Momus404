"use client";

import React, { useState } from "react";
import Link from "next/link";
import { PackageCheck, ArrowLeft, Trash2, AlertTriangle } from "lucide-react";

interface Order {
  id: string;
  customer: string;
  total: number;
  status: string;
}

const DEFAULT_ORDERS: Order[] = [
  {"id": "ORD-9021", "customer": "Global QA Labs", "total": 1699.00, "status": "Delivered"},
  {"id": "ORD-9022", "customer": "Apex Robotics", "total": 499.00, "status": "Processing"},
  {"id": "ORD-9023", "customer": "Vector Corp", "total": 249.50, "status": "Pending"},
];

export default function PlaygroundOrdersPage() {
  const [orders, setOrders] = useState<Order[]>(DEFAULT_ORDERS);
  const [hasDataError, setHasDataError] = useState(false);
  const [deletedWrongOrder, setDeletedWrongOrder] = useState<string | null>(null);

  // [INTENTIONAL DEFECT: Data fetching error simulator]
  const triggerDataFetchError = () => {
    setHasDataError(true);
  };

  // [INTENTIONAL DEFECT: Cancel button deletes first row instead of targeted row]
  const handleCancelOrder = (targetId: string) => {
    // Buggy implementation deletes index 0 regardless of targetId
    if (orders.length > 0) {
      const deleted = orders[0];
      setOrders(orders.slice(1));
      setDeletedWrongOrder(`[INDEX DEFECT]: Clicked cancel for '${targetId}', but deleted '${deleted.id}' (${deleted.customer})!`);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-5xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 08]: DATA FETCH & INDEX BUG
        </span>
      </header>

      <main className="max-w-5xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b-2 border-black gap-3">
          <div className="flex items-center gap-2">
            <PackageCheck size={18} />
            <h1 className="font-mono font-black text-base uppercase">Order Fulfillment Tracking</h1>
          </div>

          <button
            id="btn-simulate-data-error"
            onClick={triggerDataFetchError}
            className="border-2 border-black bg-red-50 text-red-800 px-3 py-1 text-xs font-mono font-bold hover:bg-red-100 transition"
          >
            Simulate Data Fetch Failure
          </button>
        </div>

        {deletedWrongOrder && (
          <div id="wrong-order-alert" className="mb-4 p-2.5 bg-red-50 border border-red-600 font-mono text-xs text-red-900">
            {deletedWrongOrder}
          </div>
        )}

        {hasDataError ? (
          <div id="data-fetch-error-box" className="p-8 text-center border-2 border-red-600 bg-red-50 font-mono text-xs text-red-900">
            <p className="font-bold text-sm">Failed to Load Orders: Unexpected Token &lt; in JSON at Position 0</p>
            <p className="mt-1 text-neutral-600">Upstream billing API returned malformed HTML error payload instead of JSON.</p>
          </div>
        ) : (
          <div className="overflow-x-auto border-2 border-black">
            <table className="w-full text-left font-mono text-xs border-collapse">
              <thead className="bg-black text-white">
                <tr>
                  <th className="p-2 border border-neutral-700">Order ID</th>
                  <th className="p-2 border border-neutral-700">Customer</th>
                  <th className="p-2 border border-neutral-700">Total</th>
                  <th className="p-2 border border-neutral-700">Status</th>
                  <th className="p-2 border border-neutral-700 text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((o) => (
                  <tr key={o.id} className="border-b border-black hover:bg-neutral-50">
                    <td className="p-2 font-bold">{o.id}</td>
                    <td className="p-2">{o.customer}</td>
                    <td className="p-2 font-black">${o.total.toFixed(2)}</td>
                    <td className="p-2">
                      <span className="px-1.5 py-0.5 border border-black bg-neutral-100">{o.status}</span>
                    </td>
                    <td className="p-2 text-center">
                      <button
                        id={`btn-cancel-${o.id}`}
                        onClick={() => handleCancelOrder(o.id)}
                        className="border border-black px-2 py-0.5 text-[10px] bg-red-100 hover:bg-red-200 transition"
                      >
                        Cancel Order
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>
    </div>
  );
}
