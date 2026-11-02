"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

export interface CartItem {
  variant_id: string;
  product: string;
  sku: string;
  quantity: number;
  price: number;
}

interface CartProps {
  onFetchCart?: () => Promise<{ items: CartItem[] }>;
  onRemoveItem?: (id: string) => Promise<void>;
}

export default function Cart({ onFetchCart, onRemoveItem }: CartProps) {
  const [items, setItems] = useState<CartItem[]>([]);
  const [error, setError] = useState<string>("");
  const [busyId, setBusyId] = useState<string | null>(null);

  async function refresh() {
    try {
      if (!onFetchCart) return;
      const data = await onFetchCart();
      setItems(data.items);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function handleRemove(id: string) {
    setBusyId(id);
    try {
      if (onRemoveItem) {
        await onRemoveItem(id);
      }
      await refresh();
      window.dispatchEvent(new Event("cart:updated"));
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusyId(null);
    }
  }

  return (
    <main className="evu-panel">
      <p className="eyebrow">YOUR SELECTION</p>
      <h1>Shopping bag</h1>

      {items.length > 0 ? (
        <div className="evu-cart-list">
          {items.map((item) => (
            <div className="evu-cart-row" key={item.variant_id}>
              <div className="evu-cart-details">
                <strong>{item.product}</strong>
                <p>
                  {item.sku} · {item.quantity} × BDT {item.price}
                </p>
              </div>

              <button
                type="button"
                className="evu-remove-button"
                disabled={busyId === item.variant_id}
                onClick={() => handleRemove(item.variant_id)}
              >
                {busyId === item.variant_id ? "Removing..." : "Remove"}
              </button>
            </div>
          ))}

          <Link className="evu-button" href="/checkout">
            Continue to checkout →
          </Link>
        </div>
      ) : (
        !error && (
          <p>
            Your bag is empty.{" "}
            <Link href="/shop">Explore the collection →</Link>
          </p>
        )
      )}

      {error && (
        <p role="alert" className="evu-error">
          {error} <Link href="/account">Sign in</Link>
        </p>
      )}
    </main>
  );
}