"use client";

import React, { useState } from "react";
import Link from "next/link";
import { ShoppingBag, ArrowLeft, Search, Filter } from "lucide-react";

interface Product {
  id: string;
  name: string;
  category: string;
  price: number;
}

const ALL_PRODUCTS: Product[] = [
  {"id": "prd_01", "name": "Edge AI Inference Accelerator P1000", "category": "Hardware", "price": 499.00},
  {"id": "prd_02", "name": "Momus Enterprise License", "category": "Software", "price": 1200.00},
  {"id": "prd_03", "name": "Autonomous QA Probe V2", "category": "Hardware", "price": 249.50},
  {"id": "prd_04", "name": "Vault Encrypted Storage 1TB", "category": "Cloud", "price": 89.00},
];

export default function PlaygroundProductsPage() {
  const [category, setCategory] = useState("All");
  const [search, setSearch] = useState("");
  // [INTENTIONAL DEFECT: Category dropdown state change does not filter products array]
  const [products] = useState<Product[]>(ALL_PRODUCTS);

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-5xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 04]: FILTER BUG & REFLECTED XSS
        </span>
      </header>

      <main className="max-w-5xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-6 border-b-2 border-black gap-4">
          <div className="flex items-center gap-2">
            <ShoppingBag size={18} />
            <h1 className="font-mono font-black text-base uppercase">Product Catalog & Inventory</h1>
          </div>

          <div className="flex items-center gap-2">
            {/* [INTENTIONAL DEFECT: Dropdown changes state value but does not filter cards] */}
            <select
              id="select-category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="border-2 border-black p-2 font-mono text-xs bg-white focus:outline-none"
            >
              <option value="All">All Categories</option>
              <option value="Hardware">Hardware (Defect: Does not filter)</option>
              <option value="Software">Software (Defect: Does not filter)</option>
              <option value="Cloud">Cloud (Defect: Does not filter)</option>
            </select>

            <div className="relative">
              <input
                id="search-input"
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search catalog…"
                className="border-2 border-black p-2 pl-7 font-mono text-xs focus:outline-none"
              />
              <Search size={12} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-neutral-400" />
            </div>
          </div>
        </div>

        {/* [INTENTIONAL DEFECT: Reflected unescaped query dangerously rendered in DOM] */}
        {search && (
          <div className="mb-4 p-2 bg-neutral-100 border border-black font-mono text-xs">
            Search query results for:{" "}
            <span
              id="reflected-search-output"
              dangerouslySetInnerHTML={{ __html: search }}
              className="font-bold text-red-600"
            />
          </div>
        )}

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {products.map((p) => (
            <div key={p.id} className="border-2 border-black p-4 flex flex-col justify-between bg-neutral-50">
              <div>
                <span className="font-mono text-[10px] bg-neutral-200 px-1 py-0.5 uppercase border border-neutral-400">
                  {p.category}
                </span>
                <h3 className="font-bold text-sm mt-2">{p.name}</h3>
              </div>
              <div className="mt-4 pt-3 border-t border-black flex items-center justify-between">
                <span className="font-mono font-black text-sm">${p.price.toFixed(2)}</span>
                <button
                  id={`btn-cart-${p.id}`}
                  className="bg-black text-white px-2.5 py-1 text-[11px] font-mono hover:bg-neutral-800 transition"
                >
                  Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
