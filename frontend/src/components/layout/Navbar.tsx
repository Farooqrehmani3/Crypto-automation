"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils/cn";
import { Button } from "@/components/ui/button";
import { SearchInput } from "@/components/shared/SearchInput";
import { ThemeToggle } from "@/components/shared/ThemeToggle";
import {
  Bell,
  Menu,
  Search,
  X,
  Command,
} from "lucide-react";

interface NavbarProps {
  onMenuClick?: () => void;
}

export function Navbar({ onMenuClick }: NavbarProps) {
  const router = useRouter();
  const [searchOpen, setSearchOpen] = useState(false);
  const [notifications] = useState(3);

  const handleSearch = (query: string) => {
    if (query.length >= 2) {
      router.push(`/coins/${query.toLowerCase()}`);
      setSearchOpen(false);
    }
  };

  return (
    <header className="sticky top-0 z-30 w-full border-b border-slate-200/60 dark:border-slate-800/60 bg-white/80 dark:bg-slate-950/80 backdrop-blur-xl">
      <div className="flex items-center h-16 px-4 gap-4">
        {/* Mobile menu trigger */}
        <Button
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          className="lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </Button>

        {/* Breadcrumb / Page Title */}
        <div className="hidden sm:block" />

        {/* Spacer */}
        <div className="flex-1" />

        {/* Search */}
        <div className="hidden md:flex items-center">
          <SearchInput
            placeholder="Search coins... (Ctrl+K)"
            onSearch={handleSearch}
            className="w-[320px]"
          />
        </div>

        {/* Mobile Search Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setSearchOpen(!searchOpen)}
          className="md:hidden"
        >
          <Search className="w-5 h-5" />
        </Button>

        {/* Command palette hint */}
        <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-slate-100 dark:bg-slate-800 text-xs text-slate-400 dark:text-slate-500 border border-slate-200 dark:border-slate-700">
          <Command className="w-3 h-3" />
          <span>K</span>
        </div>

        {/* Notifications */}
        <Button
          variant="ghost"
          size="icon"
          className="relative"
        >
          <Bell className="w-5 h-5" />
          {notifications > 0 && (
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-slate-950" />
          )}
        </Button>

        {/* Theme */}
        <div className="hidden sm:block">
          <ThemeToggle />
        </div>
      </div>

      {/* Mobile Search Overlay */}
      <AnimatePresence>
        {searchOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="md:hidden px-4 pb-4"
          >
            <div className="flex items-center gap-2">
              <SearchInput
                placeholder="Search coins..."
                onSearch={handleSearch}
                className="flex-1"
                autoFocus
              />
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setSearchOpen(false)}
              >
                <X className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
