"use client";

import { useEffect, useMemo, useState } from "react";
import { addVariant, getVariants, type Variant } from "@/lib/variant-api";

type Props = { productId: string };

function money(value: string, currency: string) {
  const amount = Number(value);
  if (!Number.isFinite(amount)) return `${currency} ${value}`;
  try {
    return new Intl.NumberFormat("en-BD", { style: "currency", currency }).format(amount);
  } catch {
    return `${currency} ${amount.toFixed(2)}`;
  }
}

export default function VariantSelector({ productId }: Props) {
  const [variants, setVariants] = useState<Variant[]>([]);
  const [selectedId, setSelectedId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [retry, setRetry] = useState(0);

  useEffect(() => {
    let active = true;
    setLoading(true);
    setError("");
    setMessage("");
    setVariants([]);
    setSelectedId("");
    getVariants(productId)
      .then((data) => {
        if (!active) return;
        const list = Array.isArray(data.variants) ? data.variants : [];
        setVariants(list);
        setSelectedId(list[0]?.id ?? "");
      })
      .catch((cause) => {
        if (active) setError(cause instanceof Error ? cause.message : String(cause));
      })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [productId, retry]);

  const selected = variants.find((v) => v.id === selectedId);
  const sizes = useMemo(() => Array.from(new Set(variants.map((v) => v.size || "One size"))), [variants]);
  const colors = useMemo(() => Array.from(new Set(variants.map((v) => v.color || "Standard"))), [variants]);
  const selectedSize = selected?.size || "One size";
  const selectedColor = selected?.color || "Standard";

  function selectSize(size: string) {
    const match = variants.find((v) => (v.size || "One size") === size && (v.color || "Standard") === selectedColor)
      ?? variants.find((v) => (v.size || "One size") === size);
    if (match) { setSelectedId(match.id); setMessage(""); }
  }

  function selectColor(color: string) {
    const match = variants.find((v) => (v.color || "Standard") === color && (v.size || "One size") === selectedSize)
      ?? variants.find((v) => (v.color || "Standard") === color);
    if (match) { setSelectedId(match.id); setMessage(""); }
  }

  async function submit() {
    if (!selected || busy) return;
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await addVariant(selected.id, quantity);
      window.dispatchEvent(new Event("evu:bag-updated"));
      setMessage(`${quantity} item${quantity === 1 ? "" : "s"} added to your bag.`);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : String(cause));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="evu-variant-picker" aria-label="Choose product options">
      {loading && <p role="status">Loading available options…</p>}
      {!loading && variants.length === 0 && (
        <p>No purchasable variants are available for this product.</p>
      )}
      {variants.length > 0 && (
        <>
          <fieldset className="evu-option-group">
            <legend>Size: <strong>{selectedSize}</strong></legend>
            <div className="evu-option-row">
              {sizes.map((size) => (
                <button key={size} type="button" aria-pressed={size === selectedSize}
                  className="evu-option" onClick={() => selectSize(size)}>{size}</button>
              ))}
            </div>
          </fieldset>
          <fieldset className="evu-option-group">
            <legend>Color: <strong>{selectedColor}</strong></legend>
            <div className="evu-option-row">
              {colors.map((color) => (
                <button key={color} type="button" aria-pressed={color === selectedColor}
                  className="evu-option" onClick={() => selectColor(color)}>{color}</button>
              ))}
            </div>
          </fieldset>
          {selected && (
            <p className="evu-variant-summary">
              <strong>{money(selected.price, selected.currency)}</strong>
              <span>SKU: {selected.sku}</span>
            </p>
          )}
          <label className="evu-quantity-label" htmlFor="evu-quantity">Quantity</label>
          <input id="evu-quantity" type="number" min={1} max={20} step={1} value={quantity}
            onChange={(event) => {
              const value = Number(event.target.value);
              setQuantity(Number.isFinite(value) ? Math.max(1, Math.min(20, Math.floor(value))) : 1);
            }} />
          <button type="button" className="evu-button" disabled={!selected || busy} onClick={submit}>
            {busy ? "Adding…" : "Add to bag"}
          </button>
        </>
      )}
      {error && <p role="alert" className="evu-error">{error} <button type="button" onClick={() => setRetry((n) => n + 1)}>Retry loading</button></p>}
      {message && <p role="status">{message}</p>}
      <p className="evu-variant-note">Availability is confirmed by the server when you add to your bag and check out.</p>
    </section>
  );
}
