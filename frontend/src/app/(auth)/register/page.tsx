"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { motion } from "framer-motion";
import Link from "next/link";
import { Eye, EyeOff, UserPlus, Chrome, Github, Loader2, Check } from "lucide-react";
import { useAuth } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";

const registerSchema = z
  .object({
    displayName: z
      .string()
      .min(2, "Name must be at least 2 characters")
      .max(50, "Name must be at most 50 characters")
      .optional()
      .or(z.literal("")),
    email: z.string().email("Please enter a valid email address"),
    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
      .regex(/[a-z]/, "Password must contain at least one lowercase letter")
      .regex(/[0-9]/, "Password must contain at least one number"),
    confirmPassword: z.string(),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  });

type RegisterFormData = z.infer<typeof registerSchema>;

const passwordRequirements = [
  { label: "At least 8 characters", test: (p: string) => p.length >= 8 },
  { label: "One uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
  { label: "One lowercase letter", test: (p: string) => /[a-z]/.test(p) },
  { label: "One number", test: (p: string) => /[0-9]/.test(p) },
];

export default function RegisterPage() {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [password, setPassword] = useState("");
  const { signUpWithEmail, signInWithGoogle, signInWithGithub, isLoading } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      displayName: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = async (data: RegisterFormData) => {
    await signUpWithEmail(data.email, data.password, data.displayName || undefined);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-secondary-900 dark:text-white">
          Create your account
        </h1>
        <p className="mt-2 text-sm text-secondary-500 dark:text-secondary-400">
          Start your free crypto intelligence journey
        </p>
      </div>

      {/* OAuth Buttons */}
      <div className="space-y-3">
        <Button
          variant="outline"
          className="w-full gap-3 h-11"
          onClick={signInWithGoogle}
          disabled={isLoading}
        >
          <Chrome className="h-5 w-5" />
          Continue with Google
        </Button>
        <Button
          variant="outline"
          className="w-full gap-3 h-11"
          onClick={signInWithGithub}
          disabled={isLoading}
        >
          <Github className="h-5 w-5" />
          Continue with GitHub
        </Button>
      </div>

      {/* Divider */}
      <div className="my-6 flex items-center gap-3">
        <Separator className="flex-1" />
        <span className="text-xs text-secondary-400 dark:text-secondary-500 font-medium">
          OR
        </span>
        <Separator className="flex-1" />
      </div>

      {/* Email/Password Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        {/* Display Name */}
        <div>
          <label
            htmlFor="displayName"
            className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1.5"
          >
            Display name{" "}
            <span className="text-secondary-400 font-normal">(optional)</span>
          </label>
          <Input
            id="displayName"
            type="text"
            placeholder="John Doe"
            disabled={isLoading}
            error={errors.displayName?.message}
            {...register("displayName")}
          />
          {errors.displayName && (
            <motion.p
              className="mt-1.5 text-xs text-red-500"
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {errors.displayName.message}
            </motion.p>
          )}
        </div>

        {/* Email */}
        <div>
          <label
            htmlFor="email"
            className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1.5"
          >
            Email address
          </label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="name@example.com"
            disabled={isLoading}
            error={errors.email?.message}
            {...register("email")}
          />
          {errors.email && (
            <motion.p
              className="mt-1.5 text-xs text-red-500"
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {errors.email.message}
            </motion.p>
          )}
        </div>

        {/* Password */}
        <div>
          <label
            htmlFor="password"
            className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1.5"
          >
            Password
          </label>
          <div className="relative">
            <Input
              id="password"
              type={showPassword ? "text" : "password"}
              autoComplete="new-password"
              placeholder="Create a strong password"
              disabled={isLoading}
              error={errors.password?.message}
              {...register("password", {
                onChange: (e) => setPassword(e.target.value),
              })}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-400 hover:text-secondary-600 dark:hover:text-secondary-300 transition-colors"
              tabIndex={-1}
            >
              {showPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
          {errors.password && (
            <motion.p
              className="mt-1.5 text-xs text-red-500"
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {errors.password.message}
            </motion.p>
          )}

          {/* Password Requirements */}
          {password.length > 0 && (
            <motion.div
              className="mt-2 space-y-1"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              transition={{ duration: 0.2 }}
            >
              {passwordRequirements.map((req) => {
                const met = req.test(password);
                return (
                  <div
                    key={req.label}
                    className={`flex items-center gap-2 text-xs ${
                      met
                        ? "text-green-600 dark:text-green-400"
                        : "text-secondary-400"
                    }`}
                  >
                    <div
                      className={`flex h-3.5 w-3.5 items-center justify-center rounded-full border ${
                        met
                          ? "border-green-500 bg-green-500 text-white"
                          : "border-secondary-300 dark:border-secondary-600"
                      }`}
                    >
                      {met && <Check className="h-2.5 w-2.5" />}
                    </div>
                    {req.label}
                  </div>
                );
              })}
            </motion.div>
          )}
        </div>

        {/* Confirm Password */}
        <div>
          <label
            htmlFor="confirmPassword"
            className="block text-sm font-medium text-secondary-700 dark:text-secondary-300 mb-1.5"
          >
            Confirm password
          </label>
          <div className="relative">
            <Input
              id="confirmPassword"
              type={showConfirmPassword ? "text" : "password"}
              autoComplete="new-password"
              placeholder="Confirm your password"
              disabled={isLoading}
              error={errors.confirmPassword?.message}
              {...register("confirmPassword")}
            />
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-secondary-400 hover:text-secondary-600 dark:hover:text-secondary-300 transition-colors"
              tabIndex={-1}
            >
              {showConfirmPassword ? (
                <EyeOff className="h-4 w-4" />
              ) : (
                <Eye className="h-4 w-4" />
              )}
            </button>
          </div>
          {errors.confirmPassword && (
            <motion.p
              className="mt-1.5 text-xs text-red-500"
              initial={{ opacity: 0, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
            >
              {errors.confirmPassword.message}
            </motion.p>
          )}
        </div>

        <Button
          type="submit"
          className="w-full h-11 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white"
          disabled={isLoading}
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <>
              <UserPlus className="h-4 w-4 mr-2" />
              Create Account
            </>
          )}
        </Button>
      </form>

      {/* Login Link */}
      <p className="mt-6 text-center text-sm text-secondary-500 dark:text-secondary-400">
        Already have an account?{" "}
        <Link
          href="/login"
          className="text-blue-600 dark:text-blue-400 hover:underline font-medium"
        >
          Sign in
        </Link>
      </p>
    </motion.div>
  );
}
