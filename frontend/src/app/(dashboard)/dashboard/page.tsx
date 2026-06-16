import type { Metadata } from "next";
import { DashboardView } from "@/components/dashboard/DashboardView";

export const metadata: Metadata = {
  title: "Dashboard",
  description: "Your crypto intelligence dashboard with real-time market overview and AI-powered insights.",
};

export default function DashboardPage() {
  return <DashboardView />;
}
