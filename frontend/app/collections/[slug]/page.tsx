import { notFound } from "next/navigation";
import CollectionGrid from "@/components/CollectionGrid";
import type { Product } from "@/lib/catalog";

const api = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
export default async function CollectionPage({ params, searchParams }: { params: { slug: string }; searchParams: { page?: string } }) {
  const page = Math.max(1, Math.min(10000, Number(searchParams.page) || 1));
  const slug = encodeURIComponent(params.slug);
  const response = await fetch(`${api}/api/catalog/collections/${slug}/products/?page=${page}`, { next: { revalidate: 60 } }).catch(() => null);
  if (response?.status === 404) notFound();
  if (!response?.ok) return <main className="shop-page"><h1>Collection unavailable</h1><p>Please try again later.</p></main>;
  const data: { results: Product[]; next: string | null; previous: string | null; count: number } = await response.json();
  return <main className="shop-page"><div className="shop-heading"><span className="eyebrow">EVU COLLECTIONS</span><h1>{params.slug.replace(/-/g, " ")}</h1><p>{data.count} pieces</p></div><CollectionGrid products={data.results}/>
    <nav aria-label="Collection pagination" style={{ display: "flex", gap: "1rem", marginTop: "2rem" }}>
      {data.previous && <a href={`/collections/${slug}?page=${page - 1}`}>Previous</a>}
      {data.next && <a href={`/collections/${slug}?page=${page + 1}`}>Next</a>}
    </nav>
  </main>;
}