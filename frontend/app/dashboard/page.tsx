"use client";

import VerificationPage from "../verification/page";

// Export the verification page on /dashboard as well so both /verification and /dashboard paths work
export default function DashboardPage() {
  return <VerificationPage />;
}
