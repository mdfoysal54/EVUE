import {api} from "@/lib/client-api";

export type Tracking = {
  id: string;
  payment_status: string;
  total: string;
  currency: string;
  shipping: null | {
    status: string;
    courier: string;
    tracking_number: string;
    events: {status: string; note: string; at: string}[];
  };
};
export type ShippingQuote = {city: string; shipping_fee: string; currency: string; estimate_only: boolean; notice: string};
export const getShippingQuote = (city: string) => api<ShippingQuote>(`shipping/quote/?city=${encodeURIComponent(city)}`);
export const startPayment = (id: string, delivery: {recipient: string; phone: string; address: string; city: string}) =>
  api<{payment_url: string; transaction_id: string}>(`orders/${encodeURIComponent(id)}/pay/`, "POST", delivery);
export const getTracking = (id: string) => api<Tracking>(`orders/${encodeURIComponent(id)}/tracking/`);
export const requestReturn = (purchase_id: string, reason: string) =>
  api<{id: number; status: string}>("returns/", "POST", {purchase_id, reason});