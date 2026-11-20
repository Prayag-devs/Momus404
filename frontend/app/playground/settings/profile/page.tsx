"use client";

import React, { useState } from "react";
import Link from "next/link";
import { UserCheck, ArrowLeft, Loader2, UploadCloud } from "lucide-react";

export default function PlaygroundProfileSettingsPage() {
  const [name, setName] = useState("Alex Developer");
  const [email, setEmail] = useState("alex@corp.local");
  const [isSaving, setIsSaving] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);

  // [INTENTIONAL DEFECT: Save button spinner never finishes loading]
  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    // Never calls setIsSaving(false) — infinite loading lock defect
  };

  // [INTENTIONAL DEFECT: Accepts any file type without extension/MIME validation]
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file.name);
    }
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 06]: STUCK SPINNER & UPLOAD FLAW
        </span>
      </header>

      <main className="max-w-xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex items-center gap-2 border-b-2 border-black pb-3 mb-5">
          <UserCheck size={18} />
          <h1 className="font-mono font-black text-base uppercase">User Profile & Avatar Settings</h1>
        </div>

        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block font-mono text-xs font-bold mb-1" htmlFor="profile-name">
              Display Name
            </label>
            <input
              id="profile-name"
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full border-2 border-black p-2 font-mono text-xs focus:outline-none"
            />
          </div>

          <div>
            <label className="block font-mono text-xs font-bold mb-1" htmlFor="profile-email">
              Notification Email
            </label>
            <input
              id="profile-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border-2 border-black p-2 font-mono text-xs focus:outline-none"
            />
          </div>

          <div>
            <span className="block font-mono text-xs font-bold mb-1">
              Avatar Upload (No File Extension Restriction)
            </span>
            <div className="border-2 border-dashed border-black p-4 text-center bg-neutral-50">
              <UploadCloud size={20} className="mx-auto mb-1 text-neutral-500" />
              <input
                id="avatar-upload"
                type="file"
                onChange={handleFileUpload}
                className="font-mono text-xs"
              />
              {uploadedFile && (
                <p id="uploaded-filename" className="font-mono text-xs text-red-600 font-bold mt-2">
                  [SECURITY FLAW]: Unrestricted file accepted: {uploadedFile}
                </p>
              )}
            </div>
          </div>

          {/* [INTENTIONAL DEFECT: Stuck spinner locks UI permanently upon click] */}
          <button
            id="btn-save-profile"
            type="submit"
            disabled={isSaving}
            className="w-full bg-black text-white hover:bg-neutral-800 transition font-mono text-xs font-bold py-3 flex items-center justify-center gap-2"
          >
            {isSaving ? (
              <>
                <Loader2 size={13} className="animate-spin" />
                <span id="stuck-spinner-label">Saving Changes (Permanent Spinner Lock)…</span>
              </>
            ) : (
              "Save Profile Changes"
            )}
          </button>
        </form>
      </main>
    </div>
  );
}
