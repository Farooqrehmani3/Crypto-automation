"use client";

import { useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAdminStore } from "@/store/adminStore";
import { getApiClient } from "@/lib/api/client";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function useAdminAuth() {
  const router = useRouter();
  const { admin, token, isLoading, isInitialized, setAdmin, setToken, setLoading, setInitialized, reset } =
    useAdminStore();

  // Verify admin token on mount
  useEffect(() => {
    const verifyToken = async () => {
      const stored = useAdminStore.getState();
      if (!stored.token) {
        setLoading(false);
        setInitialized(true);
        return;
      }

      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/auth/admin/verify`, {
          headers: { Authorization: `Bearer ${stored.token}` },
        });

        if (res.ok) {
          const json = await res.json();
          setAdmin(json.data);
        } else {
          // Token expired or invalid
          reset();
        }
      } catch {
        // Backend unreachable — keep stored token until we can verify
      } finally {
        setLoading(false);
        setInitialized(true);
      }
    };

    if (!isInitialized) {
      verifyToken();
    }
  }, [isInitialized, setAdmin, setToken, setLoading, setInitialized, reset]);

  const signIn = useCallback(
    async (username: string, password: string) => {
      try {
        setLoading(true);
        const res = await fetch(`${API_BASE_URL}/api/v1/auth/admin/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });

        if (!res.ok) {
          const error = await res.json().catch(() => ({ detail: "Invalid credentials" }));
          return { success: false, error: error.detail || "Invalid credentials" };
        }

        const json = await res.json();
        const { access_token, username: uname, role } = json.data;

        setToken(access_token);
        setAdmin({ username: uname, role, exp: 0 });
        router.push("/admin");
        return { success: true };
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to sign in";
        return { success: false, error: message };
      } finally {
        setLoading(false);
      }
    },
    [setLoading, setToken, setAdmin, router]
  );

  const signOut = useCallback(() => {
    reset();
    router.push("/admin/login");
  }, [reset, router]);

  return {
    admin,
    token,
    isLoading,
    isInitialized,
    isAuthenticated: !!admin && !!token,
    signIn,
    signOut,
  };
}
