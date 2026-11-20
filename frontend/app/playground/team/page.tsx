"use client";

import React, { useState } from "react";
import Link from "next/link";
import { UserPlus, ArrowLeft, X, Mail } from "lucide-react";

export default function PlaygroundTeamPage() {
  const [modalOpen, setModalOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [invitedList, setInvitedList] = useState<string[]>(["sarah@corp.local", "kevin@corp.local"]);

  // [INTENTIONAL DEFECT: Backdrop and close button fail to close modal]
  const handleBrokenClose = () => {
    // Intentional bug: does not setModalOpen(false), trapping focus inside modal!
  };

  const handleSendInvite = (e: React.FormEvent) => {
    e.preventDefault();
    // [INTENTIONAL DEFECT: Accepts malformed email strings without regex validation]
    setInvitedList((prev) => [...prev, email]);
    setEmail("");
    setModalOpen(false); // Only submit closes it
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-4xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 13]: TRAPPED MODAL & EMAIL FLAW
        </span>
      </header>

      <main className="max-w-4xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b-2 border-black gap-3">
          <div className="flex items-center gap-2">
            <UserPlus size={18} />
            <h1 className="font-mono font-black text-base uppercase">Team Members & Access Invites</h1>
          </div>

          <button
            id="btn-open-invite-modal"
            onClick={() => setModalOpen(true)}
            className="border-2 border-black bg-black text-white px-3 py-1.5 text-xs font-mono font-bold hover:bg-neutral-800 transition"
          >
            + Invite New Member
          </button>
        </div>

        <div className="space-y-2">
          <h3 className="font-mono text-xs font-bold uppercase text-neutral-500">Active Invitations</h3>
          {invitedList.map((inv, idx) => (
            <div key={idx} className="border border-black p-2.5 bg-neutral-50 font-mono text-xs flex items-center justify-between">
              <span>{inv}</span>
              <span className="text-neutral-500 text-[10px]">Invite Pending</span>
            </div>
          ))}
        </div>

        {/* Modal with intentional trapped focus */}
        {modalOpen && (
          <div
            id="modal-backdrop"
            onClick={handleBrokenClose}
            className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
          >
            <div
              id="modal-dialog"
              onClick={(e) => e.stopPropagation()}
              className="bg-white border-4 border-black p-6 max-w-md w-full shadow-[8px_8px_0px_0px_#000000] relative"
            >
              <div className="flex items-center justify-between border-b-2 border-black pb-2 mb-4">
                <h3 className="font-mono font-black text-sm uppercase">Invite Collaborator</h3>
                {/* [INTENTIONAL DEFECT: Close button has broken handler] */}
                <button
                  id="btn-modal-close"
                  onClick={handleBrokenClose}
                  className="p-1 hover:bg-neutral-100 border border-black"
                  title="Close modal (Defect: Broken Click)"
                >
                  <X size={15} />
                </button>
              </div>

              <p className="font-mono text-[10px] text-red-600 mb-3 font-bold">
                [TRAPPED FOCUS BUG]: Modal close button and backdrop click do not dismiss this dialog!
              </p>

              <form onSubmit={handleSendInvite} className="space-y-3">
                <div>
                  <label className="block font-mono text-xs font-bold mb-1" htmlFor="input-invite-email">
                    Email Address (Accepts Malformed Format)
                  </label>
                  <input
                    id="input-invite-email"
                    type="text"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="invalid_email_string_without_at"
                    className="w-full border-2 border-black p-2 font-mono text-xs focus:outline-none"
                    required
                  />
                </div>

                <button
                  id="btn-submit-invite"
                  type="submit"
                  className="w-full bg-black text-white hover:bg-neutral-800 transition font-mono text-xs font-bold py-2.5"
                >
                  Send Invitation
                </button>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
