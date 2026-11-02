import Link from "next/link";

type Collection = { name: string; slug: string; description: string; image_url: string | null };
const api = process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";
export default async function CollectionsPage() {
  let collections: Collection[] = [];
  try {
    const response = await fetch(`${api}/api/catalog/collections/`, { next: { revalidate: 60 } });
    if (!response.ok) throw new Error("Collections unavailable");
    const payload = await response.json();
    collections = Array.isArray(payload) ? payload : payload.results || [];
  } catch { /* Show a graceful unavailable state. */ }
  return <main className="shop-page"><div className="shop-heading"><span className="eyebrow">THE EVU EDIT</span><h1>Collections</h1></div>
    {collections.length ? <div className="editorial-grid">{collections.map(c => <article key={c.slug}><Link href={`/collections/${encodeURIComponent(c.slug)}`}><h2>{c.name}</h2><p>{c.description}</p><span>EXPLORE COLLECTION</span></Link></article>)}</div> : <p>No collections are currently available.</p>}
  </main>;
}