export type Product = { id: string; name: string; slug: string; description: string; price: string; currency: string; image_url: string; category: string; featured: boolean };
type Page = { results: Product[] };
const base = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
export async function getProducts(): Promise<Product[]> {
  try {
    const response = await fetch(`${base}/api/catalog/products/`, { next: { revalidate: 60 } });
    if (!response.ok) throw new Error(`Catalog returned ${response.status}`);
    return ((await response.json()) as Page).results;
  } catch (error) {
    console.error("Catalog fetch failed", error);
    return [];
  }
}
export async function getProduct(slug: string): Promise<Product | null> {
  try {
    const response = await fetch(`${base}/api/catalog/products/${encodeURIComponent(slug)}/`, { next: { revalidate: 60 } });
    if (!response.ok) return null;
    return (await response.json()) as Product;
  } catch { return null; }
}
export function money(price: string, currency: string) { return new Intl.NumberFormat("en-BD", { style: "currency", currency }).format(Number(price)); }
