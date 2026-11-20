"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Users, ArrowLeft, Shield, AlertTriangle } from "lucide-react";

interface UserItem {
  id: string;
  name: string;
  email: string;
  role: string;
  status: string;
}

const INITIAL_USERS: UserItem[] = [
  {"id": "usr_01", "name": "Alice Johnson", "email": "alice@corp.local", "role": "Admin", "status": "Active"},
  {"id": "usr_02", "name": "Bob Smith", "email": "bob@corp.local", "role": "Editor", "status": "Active"},
  {"id": "usr_03", "name": "Charlie Davis", "email": "charlie@corp.local", "role": "Viewer", "status": "Pending"},
  {"id": "usr_04", "name": "Diana Prince", "email": "diana@corp.local", "role": "Editor", "status": "Suspended"},
];

export default function PlaygroundUsersPage() {
  const [users, setUsers] = useState<UserItem[]>(INITIAL_USERS);
  const [pageSize, setPageSize] = useState("10");
  const [idorLog, setIdorLog] = useState<string | null>(null);

  // [INTENTIONAL DEFECT: Broken Dropdown]
  // Changing page size dropdown wipes the list to empty instead of paginating
  const handlePageSizeChange = (val: string) => {
    setPageSize(val);
    if (val === "25" || val === "50") {
      setUsers([]); // Intentional data wiping defect on dropdown change
    } else {
      setUsers(INITIAL_USERS);
    }
  };

  // [INTENTIONAL DEFECT: IDOR Role Toggle]
  // Allows any client to elevate any user ID to SuperAdmin without session check
  const handleElevateRole = (userId: string) => {
    setUsers((prev) =>
      prev.map((u) => (u.id === userId ? { ...u, role: "SuperAdmin" } : u))
    );
    setIdorLog(`[IDOR TRIGGERED]: User ${userId} elevated to SuperAdmin without token verification.`);
  };

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-5xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 03]: DROPDOWN BUG & IDOR
        </span>
      </header>

      <main className="max-w-5xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-4 border-b-2 border-black gap-3">
          <div className="flex items-center gap-2">
            <Users size={18} />
            <h1 className="font-mono font-black text-base uppercase">User Management Directory</h1>
          </div>

          <div className="flex items-center gap-2">
            <label htmlFor="select-page-size" className="font-mono text-xs text-neutral-500">
              Page Size:
            </label>
            {/* [INTENTIONAL DEFECT: Dropdown wipes data on 25 or 50] */}
            <select
              id="select-page-size"
              value={pageSize}
              onChange={(e) => handlePageSizeChange(e.target.value)}
              className="border-2 border-black p-1.5 font-mono text-xs bg-white focus:outline-none"
            >
              <option value="10">10 per page</option>
              <option value="25">25 per page (Buggy: Wipes Table)</option>
              <option value="50">50 per page (Buggy: Wipes Table)</option>
            </select>
          </div>
        </div>

        {idorLog && (
          <div id="idor-alert" className="mb-4 p-2.5 bg-amber-50 border border-amber-600 font-mono text-xs text-amber-900">
            {idorLog}
          </div>
        )}

        <div className="overflow-x-auto border-2 border-black">
          <table className="w-full text-left font-mono text-xs border-collapse">
            <thead className="bg-black text-white">
              <tr>
                <th className="p-2 border border-neutral-700">User ID</th>
                <th className="p-2 border border-neutral-700">Name</th>
                <th className="p-2 border border-neutral-700">Email</th>
                <th className="p-2 border border-neutral-700">Role</th>
                <th className="p-2 border border-neutral-700 text-center">Action (IDOR)</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={5} className="p-6 text-center text-red-600 font-bold">
                    [DROPDOWN BUG TRIGGERED]: Table emptied after selecting page size {pageSize}!
                  </td>
                </tr>
              ) : (
                users.map((u) => (
                  <tr key={u.id} className="border-b border-black hover:bg-neutral-50">
                    <td className="p-2 text-neutral-500">{u.id}</td>
                    <td className="p-2 font-bold">{u.name}</td>
                    <td className="p-2">{u.email}</td>
                    <td className="p-2">
                      <span className={`px-1.5 py-0.5 border ${u.role === "SuperAdmin" ? "bg-red-100 border-red-600 text-red-900 font-bold" : "bg-neutral-100 border-black"}`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="p-2 text-center">
                      <button
                        id={`btn-elevate-${u.id}`}
                        onClick={() => handleElevateRole(u.id)}
                        className="border border-black px-2 py-0.5 text-[10px] bg-neutral-100 hover:bg-black hover:text-white transition"
                      >
                        Elevate Role
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
