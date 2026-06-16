import { headers } from "next/headers";
import { NextResponse } from "next/server";
import { createServerSupabaseClient } from "@/lib/supabase/server";

// Stripe requires the raw body for signature verification
const STRIPE_WEBHOOK_SECRET = process.env.STRIPE_WEBHOOK_SECRET || "";

export async function POST(request: Request) {
  const body = await request.text();
  const headersList = await headers();
  const signature = headersList.get("stripe-signature") || "";

  // In production, use stripe.webhooks.constructEvent to verify the signature
  // const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);
  // const event = stripe.webhooks.constructEvent(body, signature, STRIPE_WEBHOOK_SECRET);

  let event: { type: string; data: Record<string, unknown> };
  try {
    event = JSON.parse(body);
  } catch {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  const supabase = await createServerSupabaseClient();

  try {
    switch (event.type) {
      case "checkout.session.completed": {
        const session = event.data as {
          customer_email?: string;
          metadata?: { user_id?: string };
        };
        const userId = session.metadata?.user_id;

        if (userId) {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          await (supabase as any)
            .from("profiles")
            .update({
              subscription_tier: "pro",
              subscription_status: "active",
              updated_at: new Date().toISOString(),
            })
            .eq("user_id", userId);
        }
        break;
      }

      case "customer.subscription.updated": {
        const subscription = event.data as {
          customer: string;
          status: string;
          metadata?: { user_id?: string };
        };
        const userId = subscription.metadata?.user_id;

        if (userId) {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          await (supabase as any)
            .from("profiles")
            .update({
              subscription_status: subscription.status,
              updated_at: new Date().toISOString(),
            })
            .eq("user_id", userId);
        }
        break;
      }

      case "customer.subscription.deleted": {
        const subscription = event.data as {
          customer: string;
          metadata?: { user_id?: string };
        };
        const userId = subscription.metadata?.user_id;

        if (userId) {
          // eslint-disable-next-line @typescript-eslint/no-explicit-any
          await (supabase as any)
            .from("profiles")
            .update({
              subscription_tier: "free",
              subscription_status: "inactive",
              updated_at: new Date().toISOString(),
            })
            .eq("user_id", userId);
        }
        break;
      }

      default:
        // Unhandled event type — acknowledge receipt
        break;
    }

    return NextResponse.json({ received: true });
  } catch (error) {
    console.error("Stripe webhook error:", error);
    return NextResponse.json(
      { error: "Webhook processing failed" },
      { status: 500 }
    );
  }
}
