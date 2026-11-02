"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowUpRight, ShoppingBag, X } from "lucide-react";
import { notifyBag, useBag } from "@/components/BagProvider";

interface BagDrawerProps {
  open: boolean;
  onClose: () => void;
  onRemoveItem?: (id: string) => Promise<void>;
}

export default function BagDrawer({ open, onClose, onRemoveItem }: BagDrawerProps) {
  const { items, refresh } = useBag();
  const [error, setError] = useState<string>("");

  useEffect(() => {
    if (open) {
      void refresh();
    }
  }, [open, refresh]);

  useEffect(() => {
    if (!open) return;

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onClose();
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => {
      window.removeEventListener("keydown", handleKeyDown);
    };
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  const total = items.reduce(
    (sum, item) => sum + Number(item.price || 0) * (item.quantity || 0),
    0
  );

  async function handleRemove(id: string) {
    try {
      if (onRemoveItem) {
        await onRemoveItem(id);
      } else {
        const response = await fetch("/api/cart", {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ variant_id: id }),
        });

        if (!response.ok) {
          throw new Error(`Failed to remove item (${response.status})`);
        }
      }

      notifyBag();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  return (
    <div className="overlay-layer">
      <button
        type="button"
        className="overlay-scrim"
        aria-label="Close bag"
        onClick={onClose}
      />

      <aside
        className="bag-drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Shopping bag"
      >
        <div className="drawer-top">
          <div>
            <span className="eyebrow">YOUR EDIT</span>
            <h2>The shopping bag</h2>
          </div>
          <button
            type="button"
            className="icon-btn"
            aria-label="Close"
            onClick={onClose}
          >
            <X size={20} />
          </button>
        </div>

        <div className="drawer-items">
          {items.length > 0 ? (
            items.map((item) => (
              <div className="drawer-item" key={item.variant_id}>
                <div className="mini-image">EVU</div>
                <div>
                  <strong>{item.product}</strong>
                  <p>
                    {item.sku} · {item.quantity} × BDT {item.price}
                  </p>
                  <button
                    type="button"
                    className="text-button"
                    onClick={() => void handleRemove(item.variant_id)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))
          ) : (
            <div className="drawer-empty">
              <ShoppingBag size={32} strokeWidth={1} />
              <h3>Nothing in your bag yet.</h3>
              <p>Your next favorite piece is waiting.</p>
              <Link href="/shop" onClick={onClose}>
                EXPLORE COLLECTION <ArrowUpRight size={15} />
              </Link>
            </div>
          )}
        </div>

        {error && (
          <p role="alert" className="evu-error">
            {error}
          </p>
        )}

        {items.length > 0 && (
          <div className="drawer-bottom">
            <div className="subtotal">
              <span>Estimated subtotal</span>
              <strong>
                BDT {total.toLocaleString("en-BD", { minimumFractionDigits: 2 })}
              </strong>
            </div>
            <p>Payment is not enabled yet.</p>
            <Link href="/checkout" className="dark-button" onClick={onClose}>
              RESERVE UNPAID <ArrowUpRight size={16} />
            </Link>
            <Link href="/cart" className="view-bag" onClick={onClose}>
              VIEW FULL BAG
            </Link>
          </div>
        )}
      </aside>
    </div>
  );
}