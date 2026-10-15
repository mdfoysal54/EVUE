"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api, type CartItem } from "@/lib/client-api";

export default function Cart() {
  const [items, setItems] = useState<CartItem[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function refresh() {
    try {
      const data = await api<{ items: CartItem[] }>("commerce/cart/");
      setItems(data.items);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  useEffect(() => {
    void refresh();
  }, []);

  async function remove(id: string) {
    setBusy(true);
    try {
      await api("commerce/cart/", "DELETE", { product_id: id });
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="evu-panel">
      <p className="eyebrow">YOUR SELECTION</p>
      <h1>Shopping bag</h1>

      {items.length > 0 ? (
        <div className="evu-cart-list">
          {items.map((item) => (
            <div className="evu-cart-row" key={item.product_id}>
              <div className="evu-cart-details">
                <strong>{item.name}</strong>
                <p>
                  {item.quantity} × {item.currency} {item.unit_price}
                </p>
              </div>

              <button
                type="button"
                className="evu-remove-button"
                disabled={busy}
                onClick={() => remove(item.product_id)}
              >
                Remove
              </button>
            </div>
          ))}

          <Link className="evu-button" href="/checkout">
            Continue to checkout →
          </Link>
        </div>
      ) : (
        !error && (
          <p className="evu-empty-state">
            Your bag is empty.{" "}
            <Link href="/shop" className="evu-text-link">
              Explore the collection →
            </Link>
          </p>
        )
      )}

      {error && (
        <p role="alert" className="evu-error">
          {error}{" "}
          <Link href="/account" className="evu-text-link">
            Account
          </Link>
        </p>
      )}
    </main>
  );
}