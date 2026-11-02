"use client";
import {useEffect, useState} from "react";
import Link from "next/link";
import {addVariant, getVariants, type Variant} from "@/lib/variant-api";
import {notifyBag} from "@/components/BagProvider";
export default function AddToBag({id}: {id: string}) {
  const [variants, setVariants] = useState<Variant[]>([]);
  const [variantId, setVariantId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);
  useEffect(() => {
    let active = true;
    getVariants(id).then(result => {if (active) setVariants(result.variants);})
      .catch(() => {if (active) setStatus("Variants unavailable. Please retry.");});
    return () => {active = false;};
  }, [id]);
  async function add() {
    if (!variantId) {setStatus("Choose a size and color first."); return;}
    setBusy(true); setStatus("");
    try {await addVariant(variantId, quantity); notifyBag(); setStatus("Added to your bag.");}
    catch (e) {setStatus(e instanceof Error ? e.message : "Unable to add to bag");}
    finally {setBusy(false);}
  }
  return <div className="purchase-controls">
    <label>Size and color <select value={variantId} onChange={e => setVariantId(e.target.value)}>
      <option value="">Choose a variant</option>
      {variants.map(v => <option key={v.id} value={v.id}>{v.size} / {v.color} — {v.currency} {v.price}</option>)}
    </select></label>
    <label>Quantity <input type="number" min={1} max={20} value={quantity} onChange={e => setQuantity(Math.max(1, Math.min(20, Number(e.target.value) || 1)))}/></label>
    <button disabled={busy || !variantId} onClick={add}>{busy ? "Adding…" : "Add to bag"}</button>
    <p role="status">{status} {status.toLowerCase().includes("auth") && <Link href="/account">Sign in</Link>}</p>
  </div>;
}