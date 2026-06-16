"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import {
  User,
  Bell,
  Shield,
  Palette,
  Globe,
  CreditCard,
  LogOut,
  Moon,
  Sun,
  Monitor,
  ChevronRight,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import { useAuth } from "@/hooks/useAuth";

const settingsSections = [
  { id: "profile", label: "Profile", icon: User },
  { id: "notifications", label: "Notifications", icon: Bell },
  { id: "appearance", label: "Appearance", icon: Palette },
  { id: "security", label: "Security", icon: Shield },
  { id: "billing", label: "Billing", icon: CreditCard },
];

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState("profile");
  const { signOut, user } = useAuth();

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-secondary-900 dark:text-white sm:text-3xl">
          Settings
        </h1>
        <p className="mt-1 text-sm text-secondary-500 dark:text-secondary-400">
          Manage your account preferences and configuration
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Settings Navigation */}
        <div className="lg:w-64 shrink-0">
          <Card className="glass-card p-2">
            <nav className="space-y-1">
              {settingsSections.map((section) => (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    activeSection === section.id
                      ? "bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-400"
                      : "text-secondary-600 dark:text-secondary-400 hover:bg-secondary-50 dark:hover:bg-secondary-800/50"
                  }`}
                >
                  <section.icon className="h-4 w-4" />
                  {section.label}
                  {activeSection === section.id && (
                    <ChevronRight className="h-4 w-4 ml-auto" />
                  )}
                </button>
              ))}
            </nav>
          </Card>
        </div>

        {/* Settings Content */}
        <div className="flex-1">
          <Card className="glass-card p-6">
            {activeSection === "profile" && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <h2 className="text-lg font-semibold text-secondary-900 dark:text-white">
                  Profile Information
                </h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1.5">
                      Display Name
                    </label>
                    <Input placeholder="Your display name" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1.5">
                      Email
                    </label>
                    <Input value={user?.email ?? ""} disabled />
                    <p className="mt-1 text-xs text-secondary-400">
                      Email cannot be changed. Contact support for assistance.
                    </p>
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button size="sm">Save Changes</Button>
                </div>
              </motion.div>
            )}

            {activeSection === "appearance" && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <h2 className="text-lg font-semibold text-secondary-900 dark:text-white">
                  Appearance
                </h2>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-secondary-900 dark:text-white">
                      Theme
                    </p>
                    <p className="text-xs text-secondary-500 dark:text-secondary-400">
                      Choose your preferred color scheme
                    </p>
                  </div>
                  <ThemeToggle />
                </div>
                <Separator />
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-secondary-900 dark:text-white">
                      Reduce Motion
                    </p>
                    <p className="text-xs text-secondary-500 dark:text-secondary-400">
                      Minimize animations and transitions
                    </p>
                  </div>
                  <div className="h-6 w-10 rounded-full bg-secondary-200 dark:bg-secondary-700 cursor-pointer" />
                </div>
              </motion.div>
            )}

            {activeSection === "notifications" && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <h2 className="text-lg font-semibold text-secondary-900 dark:text-white">
                  Notification Preferences
                </h2>
                <div className="space-y-4">
                  {[
                    { label: "Price Alerts", desc: "Get notified when coins hit your target prices" },
                    { label: "AI Analysis Complete", desc: "Notifications when multi-agent analysis finishes" },
                    { label: "Portfolio Updates", desc: "Weekly portfolio performance summaries" },
                    { label: "Market News Digest", desc: "Daily crypto market news roundup" },
                  ].map((item) => (
                    <div key={item.label} className="flex items-center justify-between">
                      <div>
                        <p className="text-sm font-medium text-secondary-900 dark:text-white">
                          {item.label}
                        </p>
                        <p className="text-xs text-secondary-500 dark:text-secondary-400">
                          {item.desc}
                        </p>
                      </div>
                      <div className="h-6 w-10 rounded-full bg-blue-500 cursor-pointer" />
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {activeSection === "security" && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <h2 className="text-lg font-semibold text-secondary-900 dark:text-white">
                  Security
                </h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1.5">
                      Current Password
                    </label>
                    <Input type="password" placeholder="Enter current password" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1.5">
                      New Password
                    </label>
                    <Input type="password" placeholder="Enter new password" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1.5">
                      Confirm New Password
                    </label>
                    <Input type="password" placeholder="Confirm new password" />
                  </div>
                </div>
                <div className="flex justify-end">
                  <Button size="sm">Update Password</Button>
                </div>

                <Separator />

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-secondary-900 dark:text-white">
                      Two-Factor Authentication
                    </p>
                    <p className="text-xs text-secondary-500 dark:text-secondary-400">
                      Add an extra layer of security to your account
                    </p>
                  </div>
                  <Button variant="outline" size="sm">
                    Enable 2FA
                  </Button>
                </div>
              </motion.div>
            )}

            {activeSection === "billing" && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
                className="space-y-6"
              >
                <h2 className="text-lg font-semibold text-secondary-900 dark:text-white">
                  Billing
                </h2>
                <div className="p-4 rounded-xl bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-blue-900 dark:text-blue-300">
                        Free Plan
                      </p>
                      <p className="text-xs text-blue-700 dark:text-blue-400 mt-0.5">
                        5 AI analyses per day, basic market data
                      </p>
                    </div>
                    <Badge variant="neutral">Current Plan</Badge>
                  </div>
                </div>
                <Button className="w-full bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700">
                  Upgrade to Pro
                </Button>
              </motion.div>
            )}
          </Card>

          {/* Logout */}
          <div className="mt-6">
            <Button
              variant="outline"
              className="w-full text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 border-red-200 dark:border-red-900"
              onClick={() => signOut()}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign Out
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
