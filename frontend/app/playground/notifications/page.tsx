"use client";

import React, { useState } from "react";
import Link from "next/link";
import { BellRing, ArrowLeft, CheckCircle2 } from "lucide-react";

interface NotificationItem {
  id: string;
  title: string;
  bodyHtml: string;
  read: boolean;
}

const INITIAL_NOTIFICATIONS: NotificationItem[] = [
  {
    id: "notif_01",
    title: "Security Alert: New Device Login",
    bodyHtml: "Sign-in detected from IP 192.168.1.42 (Edge-P1000).",
    read: false,
  },
  {
    id: "notif_02",
    title: "Payload Alert (Stored Injection)",
    // [INTENTIONAL DEFECT: Unescaped HTML rendering leads to stored script injection demonstration]
    bodyHtml: "Warning: User supplied comment <img src=x onerror=alert('STORED_XSS_DEMO') /> received.",
    read: false,
  },
  {
    id: "notif_03",
    title: "Telemetry Sync Complete",
    bodyHtml: "Weekly benchmark completed: 94 cases passing.",
    read: true,
  },
];

export default function PlaygroundNotificationsPage() {
  const [notifications, setNotifications] = useState<NotificationItem[]>(INITIAL_NOTIFICATIONS);

  // [INTENTIONAL DEFECT: Dead click handler does nothing]
  const handleMarkAllRead = () => {
    // Intentional dead click bug: does not update notification state
  };

  const handleMarkSingle = (id: string) => {
    setNotifications((prev) =>
      prev.map((n) => (n.id === id ? { ...n, read: true } : n))
    );
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans p-4 sm:p-8">
      <header className="max-w-2xl mx-auto flex items-center justify-between pb-4 border-b-2 border-black mb-6">
        <Link href="/playground" className="font-mono text-xs flex items-center gap-1 font-bold">
          <ArrowLeft size={14} /> Back to Playground
        </Link>
        <span className="font-mono text-xs bg-red-100 text-red-800 border border-red-500 px-2 py-0.5">
          [PAGE 09]: DEAD BUTTON & STORED XSS
        </span>
      </header>

      <main className="max-w-2xl mx-auto border-2 border-black bg-white p-6 shadow-[6px_6px_0px_0px_#000000]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 mb-5 border-b-2 border-black gap-3">
          <div className="flex items-center gap-2">
            <BellRing size={18} />
            <h1 className="font-mono font-black text-base uppercase">System Notifications</h1>
            <span id="unread-count-badge" className="bg-red-600 text-white font-mono text-[10px] px-1.5 py-0.5 font-bold">
              {unreadCount} Unread
            </span>
          </div>

          {/* [INTENTIONAL DEFECT: Mark All Read is a dead button with no functional effect] */}
          <button
            id="btn-mark-all-read"
            onClick={handleMarkAllRead}
            className="border-2 border-black bg-neutral-100 hover:bg-neutral-200 px-3 py-1 text-xs font-mono font-bold transition"
          >
            Mark All as Read (Dead Button)
          </button>
        </div>

        <div className="space-y-3">
          {notifications.map((n) => (
            <div
              key={n.id}
              className={`border-2 border-black p-3.5 transition ${n.read ? "bg-white opacity-70" : "bg-neutral-50"}`}
            >
              <div className="flex items-center justify-between mb-1">
                <h3 className="font-bold text-xs">{n.title}</h3>
                {!n.read && (
                  <button
                    id={`btn-mark-read-${n.id}`}
                    onClick={() => handleMarkSingle(n.id)}
                    className="border border-black px-2 py-0.5 text-[10px] font-mono hover:bg-black hover:text-white transition"
                  >
                    Mark Read
                  </button>
                )}
              </div>
              {/* [INTENTIONAL DEFECT: Stored unescaped HTML injection] */}
              <div
                id={`notif-body-${n.id}`}
                dangerouslySetInnerHTML={{ __html: n.bodyHtml }}
                className="font-mono text-xs text-neutral-600 mt-1"
              />
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
