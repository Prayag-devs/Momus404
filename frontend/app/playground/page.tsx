"use client";

import React from "react";
import Link from "next/link";
import {
  ShieldAlert,
  ArrowRight,
  Lock,
  LayoutDashboard,
  Users,
  ShoppingBag,
  CreditCard,
  UserCheck,
  FileBarChart,
  PackageCheck,
  BellRing,
  Receipt,
  MessageSquareWarning,
  Search,
  UserPlus,
  KeyRound,
  FileText,
  AlertTriangle,
  Bug,
} from "lucide-react";

interface TargetPageDef {
  id: string;
  num: string;
  title: string;
  route: string;
  icon: React.ReactNode;
  category: "Auth" | "Analytics" | "E-Commerce" | "Settings" | "Security" | "Data";
  seededBugs: string[];
  testFocus: string;
}

const TARGET_PAGES: TargetPageDef[] = [
  {
    id: "p1",
    num: "01",
    title: "Authentication Portal",
    route: "/playground/auth/login",
    icon: <Lock size={18} />,
    category: "Auth",
    seededBugs: ["Bypass Mode: accepts any credentials", "Plaintext password stored in DOM data-attr"],
    testFocus: "Auth bypass regression, password masking, SQLi in username",
  },
  {
    id: "p2",
    num: "02",
    title: "Executive Analytics Dashboard",
    route: "/playground/dashboard",
    icon: <LayoutDashboard size={18} />,
    category: "Analytics",
    seededBugs: ["CSS Layout overlap: KPI widgets overflow grid container", "Date filter button unresponsive"],
    testFocus: "Visual layout regression, DOM bounding box, click handling",
  },
  {
    id: "p3",
    num: "03",
    title: "User Directory & RBAC",
    route: "/playground/users",
    icon: <Users size={18} />,
    category: "Data",
    seededBugs: ["Page size dropdown resets table state to empty", "IDOR vulnerability on role elevation"],
    testFocus: "Dropdown state synchronization, IDOR privilege escalation",
  },
  {
    id: "p4",
    num: "04",
    title: "Product Catalog & Inventory",
    route: "/playground/products",
    icon: <ShoppingBag size={18} />,
    category: "E-Commerce",
    seededBugs: ["Category filter dropdown does not filter cards", "Reflected XSS in search query param"],
    testFocus: "Filter state assertions, DOM sanitization, XSS detection",
  },
  {
    id: "p5",
    num: "05",
    title: "Billing & Order Checkout",
    route: "/playground/checkout",
    icon: <CreditCard size={18} />,
    category: "E-Commerce",
    seededBugs: ["Duplicate orders submitted on rapid button double-click", "Negative quantities accepted without validation"],
    testFocus: "Button debouncing/race condition, business logic boundaries",
  },
  {
    id: "p6",
    num: "06",
    title: "User Profile Preferences",
    route: "/playground/settings/profile",
    icon: <UserCheck size={18} />,
    category: "Settings",
    seededBugs: ["Save button spinner never finishes loading", "Unrestricted file upload (accepts executable scripts)"],
    testFocus: "Loading state timeout, file MIME validation security",
  },
  {
    id: "p7",
    num: "07",
    title: "Report Generation Center",
    route: "/playground/reports/export",
    icon: <FileBarChart size={18} />,
    category: "Data",
    seededBugs: ["Dropdown renders behind modal due to CSS z-index bug", "Generate PDF returns HTTP 500 error"],
    testFocus: "Z-index layer inspection, HTTP 500 error boundary handling",
  },
  {
    id: "p8",
    num: "08",
    title: "Order History & Tracking",
    route: "/playground/orders",
    icon: <PackageCheck size={18} />,
    category: "Data",
    seededBugs: ["Data fetching issue: intermittent JSON parse error", "Cancel order button deletes wrong row"],
    testFocus: "API failure resilience, button target indexing verification",
  },
  {
    id: "p9",
    num: "09",
    title: "Notification Alert Center",
    route: "/playground/notifications",
    icon: <BellRing size={18} />,
    category: "Data",
    seededBugs: ["'Mark All Read' button has dead onClick handler (no-op)", "Unescaped HTML in notification preview"],
    testFocus: "Button click assertion, stored XSS payload sanitization",
  },
  {
    id: "p10",
    num: "10",
    title: "Invoice & Receipt Ledger",
    route: "/playground/billing/invoices",
    icon: <Receipt size={18} />,
    category: "E-Commerce",
    seededBugs: ["Currency dropdown desyncs currency symbol from amount", "Path traversal in invoice download link"],
    testFocus: "Dropdown state verification, path traversal exploit detection",
  },
  {
    id: "p11",
    num: "11",
    title: "Customer Feedback Form",
    route: "/playground/feedback",
    icon: <MessageSquareWarning size={18} />,
    category: "Data",
    seededBugs: ["CSS pointer-events bug: star rating clicks do not register", "Textarea counter allows unlimited memory buffer"],
    testFocus: "CSS clickability inspection, form character limit boundaries",
  },
  {
    id: "p12",
    num: "12",
    title: "Global Search Engine",
    route: "/playground/search",
    icon: <Search size={18} />,
    category: "Security",
    seededBugs: ["Search suggestions dropdown disappears on mouse hover", "SQL injection in search parameter (' OR '1'='1)"],
    testFocus: "Hover interaction testing, SQL injection payload assertion",
  },
  {
    id: "p13",
    num: "13",
    title: "Team Invites & Roles",
    route: "/playground/team",
    icon: <UserPlus size={18} />,
    category: "Settings",
    seededBugs: ["Invite modal focus trapped: close backdrop button broken", "Email field accepts malformed email formats"],
    testFocus: "Modal dismissal assertions, input format regex validation",
  },
  {
    id: "p14",
    num: "14",
    title: "Webhooks & API Keys",
    route: "/playground/integrations",
    icon: <KeyRound size={18} />,
    category: "Security",
    seededBugs: ["API secret key exposed in cleartext DOM attribute", "Regenerate key button sends GET request (HTTP 405 error)"],
    testFocus: "DOM secret leak scanning, HTTP method correctness (405)",
  },
  {
    id: "p15",
    num: "15",
    title: "Compliance & Audit Trail",
    route: "/playground/audit-log",
    icon: <FileText size={18} />,
    category: "Security",
    seededBugs: ["Severity dropdown breaks table column flex alignment", "Negative pagination (page=-1) dumps entire unauth log"],
    testFocus: "CSS table layout verification, negative boundary indexing",
  },
];

export default function PlaygroundHubPage() {
  return (
    <div className="min-h-screen bg-neutral-100 text-black font-sans selection:bg-black selection:text-white p-4 sm:p-8">
      {/* Top Header */}
      <header className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between pb-6 mb-8 border-b-2 border-black gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="bg-black text-white px-2 py-0.5 font-mono text-xs font-black tracking-widest uppercase">
              LINKED TESTBED
            </span>
            <span className="font-mono text-xs text-neutral-500">15 TARGET MODULES</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-black tracking-tight mt-1">
            MOMUS404 QA Target Playground
          </h1>
          <p className="text-sm text-neutral-600 font-mono mt-0.5">
            Synthetic SaaS application with intentional UI, CSS, Dropdown, Button & Security defects.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/"
            className="border-2 border-black bg-white px-4 py-2 font-mono text-xs font-bold shadow-[2px_2px_0px_0px_#000000] hover:bg-black hover:text-white transition flex items-center gap-1.5"
          >
            Back to Orchestrator Console
          </Link>
        </div>
      </header>

      {/* Grid of 15 Target Pages */}
      <main className="max-w-7xl mx-auto space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {TARGET_PAGES.map((page) => (
            <div
              key={page.id}
              className="border-2 border-black bg-white p-5 flex flex-col justify-between shadow-[4px_4px_0px_0px_#000000] hover:shadow-[6px_6px_0px_0px_#000000] transition"
            >
              <div>
                <div className="flex items-center justify-between border-b border-neutral-300 pb-2 mb-3">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-black bg-black text-white px-1.5 py-0.5">
                      #{page.num}
                    </span>
                    <span className="font-mono text-xs text-neutral-500 uppercase">{page.category}</span>
                  </div>
                  <div className="text-neutral-700">{page.icon}</div>
                </div>

                <h2 className="font-bold text-base tracking-tight mb-1">{page.title}</h2>
                <code className="text-[11px] font-mono text-neutral-500 block mb-3 bg-neutral-50 px-1 py-0.5 border border-neutral-200">
                  {page.route}
                </code>

                <div className="space-y-1.5 mb-4">
                  <span className="font-mono text-[10px] font-bold text-neutral-500 uppercase flex items-center gap-1">
                    <Bug size={11} className="text-red-600" />
                    Seeded Defects:
                  </span>
                  {page.seededBugs.map((bug, bIdx) => (
                    <div
                      key={bIdx}
                      className="text-xs font-mono text-neutral-700 flex items-start gap-1.5 bg-red-50 p-1 border-l-2 border-red-500"
                    >
                      <span className="text-red-600 font-bold">✗</span>
                      <span>{bug}</span>
                    </div>
                  ))}
                </div>

                <div className="text-[11px] font-mono text-neutral-500 mb-4">
                  <span className="font-bold text-black">Target QA Focus:</span> {page.testFocus}
                </div>
              </div>

              <div className="pt-3 border-t border-neutral-200 flex items-center justify-between">
                <Link
                  href={page.route}
                  className="w-full bg-black text-white hover:bg-neutral-800 transition font-mono text-xs font-bold py-2 px-3 text-center flex items-center justify-center gap-1.5"
                >
                  Open Page in Browser <ArrowRight size={13} />
                </Link>
              </div>
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}
