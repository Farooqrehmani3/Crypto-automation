export interface UserPreferences {
  theme: "light" | "dark" | "system";
  defaultCurrency: string;
  defaultTimeframe: string;
  emailNotifications: boolean;
  pushNotifications: boolean;
  priceAlerts: boolean;
  analysisAlerts: boolean;
  portfolioUpdates: boolean;
  newsDigest: boolean;
  language: string;
  timezone: string;
}

export interface UserProfile {
  id: string;
  userId: string;
  displayName: string | null;
  avatarUrl: string | null;
  bio: string | null;
  timezone: string;
  preferences: UserPreferences;
  createdAt: string;
  updatedAt: string;
  email: string;
  emailVerified: boolean;
  subscriptionTier: "free" | "pro" | "enterprise";
  subscriptionStatus: "active" | "canceled" | "past_due" | "trialing" | "inactive";
  subscriptionEndDate: string | null;
}
