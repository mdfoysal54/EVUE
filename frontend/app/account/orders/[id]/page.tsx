"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

export interface TrackingEvent {
  status: string;
  note: string;
  at: string;
}

export interface ShippingInfo {
  status: string;
  courier?: string;
  tracking_number?: string;
  events: TrackingEvent[];
}

export interface Tracking {
  id: string;
  payment_status: string;
  currency: string;
  total: number | string;
  shipping?: ShippingInfo | null;
}

export interface ReturnRequestResult {
  status: string;
}

interface OrderTrackingPageProps {
  onGetTracking?: (orderId: string) => Promise<Tracking>;
  onRequestReturn?: (orderId: string, reason: string) => Promise<ReturnRequestResult>;
}

export default function OrderTrackingPage({
  onGetTracking,
  onRequestReturn,
}: OrderTrackingPageProps) {
  const params = useParams<{ id: string }>();
  const [order, setOrder] = useState<Tracking | null>(null);
  const [error, setError] = useState<string>("");
  const [reason, setReason] = useState<string>("");
  const [notice, setNotice] = useState<string>("");

  async function load() {
    if (!params.id) return;

    try {
      let data: Tracking;

      if (onGetTracking) {
        data = await onGetTracking(params.id);
      } else {
        const response = await fetch(`/api/orders/${params.id}/tracking`);
        if (!response.ok) {
          throw new Error(`Failed to load order tracking (${response.status})`);
        }
        data = (await response.json()) as Tracking;
      }

      setOrder(data);
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Unable to load order");
    }
  }

  useEffect(() => {
    void load();
  }, [params.id]);

  async function submitReturn() {
    if (!params.id) return;

    try {
      let result: ReturnRequestResult;

      if (onRequestReturn) {
        result = await onRequestReturn(params.id, reason);
      } else {
        const response = await fetch(`/api/orders/${params.id}/return`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ reason }),
        });

        if (!response.ok) {
          throw new Error(`Failed to submit return request (${response.status})`);
        }

        result = (await response.json()) as ReturnRequestResult;
      }

      setNotice(`Return request ${result.status}`);
      setError("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Return request failed");
    }
  }

  return (
    <main
      className="evu-panel"
      style={{ maxWidth: 720, margin: "0 auto", padding: 24 }}
    >
      <h1>Order tracking</h1>
      <button type="button" onClick={() => void load()}>
        Refresh status
      </button>

      {error && <p role="alert">{error}</p>}

      {order && (
        <section>
          <p>Order {order.id}</p>
          <h2>Payment: {order.payment_status}</h2>
          <p>
            Total: {order.currency} {order.total}
          </p>

          {order.shipping ? (
            <>
              <h2>Delivery: {order.shipping.status}</h2>
              {order.shipping.courier && <p>Courier: {order.shipping.courier}</p>}
              {order.shipping.tracking_number && (
                <p>Tracking number: {order.shipping.tracking_number}</p>
              )}
              <ol>
                {order.shipping.events.map((e, i) => (
                  <li key={i}>
                    {e.status} — {e.note} ({new Date(e.at).toLocaleString()})
                  </li>
                ))}
              </ol>

              {order.payment_status === "paid" &&
                order.shipping.status === "delivered" && (
                  <div>
                    <h3>Request a return</h3>
                    <textarea
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      placeholder="Tell us why you want to return this item"
                    />
                    <button
                      type="button"
                      disabled={reason.trim().length < 10}
                      onClick={() => void submitReturn()}
                    >
                      Submit return request
                    </button>
                    {notice && <p role="status">{notice}</p>}
                  </div>
                )}
            </>
          ) : (
            <p>Shipping information will appear after payment initiation.</p>
          )}
        </section>
      )}
    </main>
  );
}