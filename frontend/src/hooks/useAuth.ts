"use client";

import { useCallback } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "@/store/authStore";
import { createClient } from "@/lib/supabase/client";
import { toast } from "sonner";

export function useAuth() {
  const router = useRouter();
  const { user, session, isLoading, isInitialized, setUser, setSession, setLoading, reset } =
    useAuthStore();
  const supabase = createClient();

  const signInWithEmail = useCallback(
    async (email: string, password: string) => {
      try {
        setLoading(true);
        const { data, error } = await supabase.auth.signInWithPassword({
          email,
          password,
        });

        if (error) {
          // Provide clearer messages for common errors
          const friendlyMessage =
            error.message === "Failed to fetch"
              ? "Unable to reach authentication server. This usually means the Supabase project is paused. Visit supabase.com/dashboard to restore it."
              : error.message;
          toast.error(friendlyMessage);
          return { success: false, error: friendlyMessage };
        }

        setUser(data.user);
        setSession(data.session);
        router.push("/dashboard");
        router.refresh();
        toast.success("Welcome back!");
        return { success: true };
      } catch (err) {
        const cause = err instanceof Error ? err.message : "Failed to sign in";
        const message =
          cause === "Failed to fetch"
            ? "Unable to reach authentication server. Check your internet connection or verify the Supabase project is active."
            : cause;
        toast.error(message);
        return { success: false, error: message };
      } finally {
        setLoading(false);
      }
    },
    [supabase, setLoading, setUser, setSession, router]
  );

  const signUpWithEmail = useCallback(
    async (email: string, password: string, displayName?: string) => {
      try {
        setLoading(true);
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            data: {
              display_name: displayName || email.split("@")[0],
            },
          },
        });

        if (error) {
          const friendlyMessage =
            error.message === "Failed to fetch"
              ? "Unable to reach authentication server. This usually means the Supabase project is paused. Visit supabase.com/dashboard to restore it."
              : error.message;
          toast.error(friendlyMessage);
          return { success: false, error: friendlyMessage };
        }

        if (data.user && data.session) {
          setUser(data.user);
          setSession(data.session);
          router.push("/dashboard");
          router.refresh();
          toast.success("Account created successfully!");
        } else {
          toast.success("Check your email for the confirmation link!");
        }

        return { success: true };
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to create account";
        toast.error(message);
        return { success: false, error: message };
      } finally {
        setLoading(false);
      }
    },
    [supabase, setLoading, setUser, setSession, router]
  );

  const signInWithGoogle = useCallback(async () => {
    try {
      setLoading(true);
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: `${window.location.origin}/auth/callback`,
        },
      });

      if (error) {
        // "provider is not enabled" = Google not turned on in
        // Supabase Dashboard → Authentication → Providers
        toast.error(error.message);
        return { success: false, error: error.message };
      }

      return { success: true };
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to sign in with Google";
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  }, [supabase, setLoading]);

  const signOut = useCallback(async () => {
    try {
      setLoading(true);
      const { error } = await supabase.auth.signOut();

      if (error) {
        toast.error(error.message);
        return { success: false, error: error.message };
      }

      reset();
      router.push("/login");
      router.refresh();
      toast.success("Signed out successfully");
      return { success: true };
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to sign out";
      toast.error(message);
      return { success: false, error: message };
    } finally {
      setLoading(false);
    }
  }, [supabase, setLoading, reset, router]);

  const resetPassword = useCallback(
    async (email: string) => {
      try {
        setLoading(true);
        const { error } = await supabase.auth.resetPasswordForEmail(email, {
          redirectTo: `${window.location.origin}/reset-password`,
        });

        if (error) {
          toast.error(error.message);
          return { success: false, error: error.message };
        }

        toast.success("Password reset link sent to your email");
        return { success: true };
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to send reset email";
        toast.error(message);
        return { success: false, error: message };
      } finally {
        setLoading(false);
      }
    },
    [supabase, setLoading]
  );

  return {
    user,
    session,
    isLoading,
    isInitialized,
    isAuthenticated: !!user,
    signInWithEmail,
    signUpWithEmail,
    signInWithGoogle,
    signOut,
    resetPassword,
  };
}
