// Supabase Database type definitions
// Extend this with generated types from Supabase CLI: npx supabase gen types typescript

export type Json = string | number | boolean | null | { [key: string]: Json | undefined } | Json[];

export interface Database {
  public: {
    Tables: {
      profiles: {
        Row: {
          id: string;
          user_id: string;
          display_name: string | null;
          avatar_url: string | null;
          timezone: string | null;
          preferences: Json | null;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          display_name?: string | null;
          avatar_url?: string | null;
          timezone?: string | null;
          preferences?: Json | null;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          display_name?: string | null;
          avatar_url?: string | null;
          timezone?: string | null;
          preferences?: Json | null;
          created_at?: string;
          updated_at?: string;
        };
      };
      watchlist_items: {
        Row: {
          id: string;
          user_id: string;
          coin_id: string;
          coin_name: string;
          coin_symbol: string;
          added_at: string;
          notifications_enabled: boolean;
          price_alert_above: number | null;
          price_alert_below: number | null;
        };
        Insert: {
          id?: string;
          user_id: string;
          coin_id: string;
          coin_name: string;
          coin_symbol: string;
          added_at?: string;
          notifications_enabled?: boolean;
          price_alert_above?: number | null;
          price_alert_below?: number | null;
        };
        Update: {
          id?: string;
          user_id?: string;
          coin_id?: string;
          coin_name?: string;
          coin_symbol?: string;
          added_at?: string;
          notifications_enabled?: boolean;
          price_alert_above?: number | null;
          price_alert_below?: number | null;
        };
      };
      portfolio_assets: {
        Row: {
          id: string;
          user_id: string;
          coin_id: string;
          coin_name: string;
          coin_symbol: string;
          quantity: number;
          average_buy_price: number;
          created_at: string;
          updated_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          coin_id: string;
          coin_name: string;
          coin_symbol: string;
          quantity: number;
          average_buy_price: number;
          created_at?: string;
          updated_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          coin_id?: string;
          coin_name?: string;
          coin_symbol?: string;
          quantity?: number;
          average_buy_price?: number;
          created_at?: string;
          updated_at?: string;
        };
      };
      transactions: {
        Row: {
          id: string;
          user_id: string;
          portfolio_asset_id: string;
          type: string;
          quantity: number;
          price_per_unit: number;
          total_value: number;
          fee: number | null;
          notes: string | null;
          transaction_date: string;
          created_at: string;
        };
        Insert: {
          id?: string;
          user_id: string;
          portfolio_asset_id: string;
          type: string;
          quantity: number;
          price_per_unit: number;
          total_value: number;
          fee?: number | null;
          notes?: string | null;
          transaction_date?: string;
          created_at?: string;
        };
        Update: {
          id?: string;
          user_id?: string;
          portfolio_asset_id?: string;
          type?: string;
          quantity?: number;
          price_per_unit?: number;
          total_value?: number;
          fee?: number | null;
          notes?: string | null;
          transaction_date?: string;
          created_at?: string;
        };
      };
      analyses: {
        Row: {
          id: string;
          user_id: string;
          coin_id: string;
          analysis_type: string;
          result: Json;
          agent_outputs: Json;
          status: string;
          created_at: string;
          completed_at: string | null;
        };
        Insert: {
          id?: string;
          user_id: string;
          coin_id: string;
          analysis_type: string;
          result?: Json;
          agent_outputs?: Json;
          status?: string;
          created_at?: string;
          completed_at?: string | null;
        };
        Update: {
          id?: string;
          user_id?: string;
          coin_id?: string;
          analysis_type?: string;
          result?: Json;
          agent_outputs?: Json;
          status?: string;
          created_at?: string;
          completed_at?: string | null;
        };
      };
    };
    Views: Record<string, never>;
    Functions: Record<string, never>;
    Enums: Record<string, never>;
  };
}
