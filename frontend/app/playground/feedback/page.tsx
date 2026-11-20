"use client";

import React, { useState } from "react";
import Link from "next/link";
import { MessageSquareWarning, ArrowLeft, Star, Send } from "lucide-react";

export default function PlaygroundFeedbackPage() {
  const [rating, setRating] = useState(0);
  const [comments, setComments] = useState("");
  const [submitted, setSubmitted] = useState(false);

  // [INTENTIONAL DEFECT: pointer-events: none on star rating container prevents clicks]
  const handleStarClick = (score: number) => {
    setRating(score);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 11]: POINTER-EVENTS CSS DEFECT
        </span>
      </header>

      <main className="max-w-xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex items-center gap-2 border-b-2 border-black pb-3 mb-5">
          <MessageSquareWarning size={18} />
          <h1 className="font-mono font-black text-base uppercase">Customer Satisfaction Survey</h1>
        </div>

        {submitted && (
          <div id="feedback-success-banner" className="mb-4 p-3 bg-emerald-50 border border-emerald-600 font-mono text-xs text-emerald-900">
            ✓ Feedback submitted! Selected Rating: {rating} Stars.
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block font-mono text-xs font-bold mb-2">
              Overall Platform Satisfaction Rating
            </label>
            {/* [INTENTIONAL DEFECT: pointer-events-none disables all click events on stars] */}
            <div
              id="star-rating-container"
              className="flex items-center gap-2 pointer-events-none opacity-90 p-2 border border-dashed border-red-400 bg-red-50"
            >
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  type="button"
                  key={star}
                  id={`star-btn-${star}`}
                  onClick={() => handleStarClick(star)}
                  className="p-1 hover:text-amber-500 transition"
                >
                  <Star
                    size={22}
                    className={rating >= star ? "fill-amber-400 text-amber-500" : "text-neutral-400"}
                  />
                </button>
              ))}
              <span className="font-mono text-[10px] text-red-700 ml-2">
                [CSS DEFECT]: pointer-events-none blocks user clicks
              </span>
            </div>
          </div>

          <div>
            <label className="block font-mono text-xs font-bold mb-1" htmlFor="input-comments">
              Detailed Comments (Unbounded Text Input Buffer)
            </label>
            <textarea
              id="input-comments"
              rows={4}
              value={comments}
              onChange={(e) => setComments(e.target.value)}
              placeholder="Tell us what you think…"
              className="w-full border-2 border-black p-2 font-mono text-xs focus:outline-none"
            />
            <p className="font-mono text-[10px] text-neutral-400 mt-0.5">
              Current length: {comments.length} characters (No upper limit enforced)
            </p>
          </div>

          <button
            id="btn-submit-feedback"
            type="submit"
            className="w-full bg-black text-white hover:bg-neutral-800 transition font-mono text-xs font-bold py-3 flex items-center justify-center gap-2 uppercase tracking-wider"
          >
            <Send size={13} /> Submit Feedback Survey
          </button>
        </form>
      </main>
    </div>
  );
}
