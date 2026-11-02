"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

export interface BagItem {
  variant_id: string;
  product: string;
  sku: string;
  quantity: number;
  price: number;
}

interface BagContextType {
  items: BagItem[];
  count: number;
  loading: boolean;
  refresh: () => Promise<void>;
}

const BAG_EVENT = "cart:updated";

const BagContext = createContext<BagContextType>({
  items: [],
  count: 0,
  loading: false,
  refresh: async () => {},
});

interface BagProviderProps {
  children: ReactNode;
  fetchCart?: () => Promise<{ items?: BagItem[] }>;
}

export function BagProvider({ children, fetchCart }: BagProviderProps) {
  const [items, setItems] = useState<BagItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      if (fetchCart) {
        const res = await fetchCart();
        setItems(res.items || []);
      } else {
        const res = await fetch("/api/proxy/v2/cart/", { method: "GET", credentials: "same-origin" });
        if (!res.ok) throw new Error("Failed to fetch cart");
        const data = await res.json();
        setItems(data.items || []);
      }
    } catch {
      // Preserve the last known cart on transient API failures.
      // Authentication errors should be handled by the account UI.
    } finally {
      setLoading(false);
    }
  }, [fetchCart]);

  useEffect(() => {
    void refresh();

    const handleUpdate = () => {
      void refresh();
    };

    window.addEventListener(BAG_EVENT, handleUpdate);
    return () => {
      window.removeEventListener(BAG_EVENT, handleUpdate);
    };
  }, [refresh]);

  const count = items.reduce((total, item) => total + (item.quantity || 0), 0);

  return (
    <BagContext.Provider value={{ items, count, loading, refresh }}>
      {children}
    </BagContext.Provider>
  );
}

export const useBag = (): BagContextType => useContext(BagContext);

export const notifyBag = (): void => {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event(BAG_EVENT));
  }
};