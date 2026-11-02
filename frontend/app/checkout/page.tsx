"use client";
import {useState} from "react";
import {api} from "@/lib/client-api";
import {reserveOrder, type ReservedOrder} from "@/lib/variant-api";
import {getShippingQuote, startPayment, type ShippingQuote} from "@/lib/fulfillment-api";

type Delivery = {recipient: string; phone: string; address: string; city: string};
type Locked = {shipping_fee: string; grand_total: string; currency: string};
export default function CheckoutPage() {
  const [order, setOrder] = useState<ReservedOrder | null>(null);
  const [idempotencyKey, setKey] = useState("");
  const [delivery, setDelivery] = useState<Delivery>({recipient: "", phone: "", address: "", city: ""});
  const [estimate, setEstimate] = useState<ShippingQuote | null>(null);
  const [locked, setLocked] = useState<Locked | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function run(action: () => Promise<void>) {
    setBusy(true); setError("");
    try { await action(); } catch (e) {setError(e instanceof Error ? e.message : "Request failed");}
    finally {setBusy(false);}
  }
  async function reserve() {
    await run(async () => {
      const key = idempotencyKey || crypto.randomUUID(); setKey(key);
      setOrder(await reserveOrder(key)); setLocked(null); setEstimate(null);
      window.dispatchEvent(new Event("cart:updated"));
    });
  }
  async function estimateShipping() {
    await run(async () => {setEstimate(await getShippingQuote(delivery.city)); setLocked(null);});
  }
  async function lockShipping() {
    if (!order) return;
    await run(async () => {
      const result = await api<Locked>("commerce-control/shipping/lock/", "POST", {purchase_id: order.id, city: delivery.city});
      setLocked(result);
    });
  }
  async function pay() {
    if (!order || !locked) return;
    await run(async () => {
      if (Date.now() >= new Date(order.expires_at).getTime()) throw new Error("Reservation expired. Start again.");
      if (Object.values(delivery).some(x => !x.trim())) throw new Error("Complete delivery details");
      const result = await startPayment(order.id, delivery);
      const destination = new URL(result.payment_url);
      if (destination.protocol !== "https:" || !["sandbox.sslcommerz.com", "securepay.sslcommerz.com"].includes(destination.hostname)) {
        throw new Error("Untrusted payment destination");
      }
      window.location.assign(destination.href);
    });
  }
  return <main className="evu-panel" style={{maxWidth: 720, margin: "auto", padding: 24}}>
    <h1>Secure checkout</h1>
    {error && <p role="alert">{error}</p>}
    {!order ? <button disabled={busy} onClick={reserve}>Reserve items</button> : <>
      <p>Reservation: {order.id} — {order.currency} {order.total} merchandise</p>
      <p>Expires: {new Date(order.expires_at).toLocaleString()}</p>
      {(["recipient", "phone", "address", "city"] as const).map(field => <label key={field} style={{display: "block", marginBottom: 12}}>
        {field.toUpperCase()} <input required value={delivery[field]} onChange={e => {
          setDelivery(prev => ({...prev, [field]: e.target.value}));
          if (field === "city") {setLocked(null); setEstimate(null);}
        }}/>
      </label>)}
      <button disabled={busy || !delivery.city.trim() || !!locked} onClick={estimateShipping}>Estimate shipping</button>
      {estimate && <p>Estimated shipping: {estimate.currency} {estimate.shipping_fee}</p>}
      <button disabled={busy || !estimate || !!locked} onClick={lockShipping}>Lock shipping fee</button>
      {locked && <p>Final total: {locked.currency} {locked.grand_total} (including shipping)</p>}
      <button disabled={busy || !locked || Object.values(delivery).some(x => !x.trim())} onClick={pay}>Continue to SSLCommerz</button>
    </>}
  </main>;
}