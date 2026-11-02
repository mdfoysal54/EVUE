import Link from "next/link";
import CollectionGrid from "@/components/CollectionGrid";
import { searchProducts } from "@/lib/catalog";

const DEPARTMENTS = ["women", "men", "kids", "accessories"];
type Search = { q?: string; department?: string; category?: string; sort?: string; page?: string };
export default async function Shop({ searchParams }: { searchParams: Search | Promise<Search> }) {
  const params = await searchParams;
  const department = DEPARTMENTS.includes(params.department || "") ? params.department : undefined;
  const sort = ["newest", "price_asc", "price_desc", "name"].includes(params.sort || "") ? params.sort! : "newest";
  const page = Math.min(10000, Math.max(1, Number.parseInt(params.page || "1", 10) || 1));
  const q = (params.q || "").trim().slice(0, 120);
  const category = (params.category || "").trim().slice(0, 100);
  const result = await searchProducts({ q, department, category, sort, page });
  const link = (updates: Partial<Search>) => {
    const values: Search = { q, department, category, sort, page: String(page), ...updates };
    const qs = new URLSearchParams();
    Object.entries(values).forEach(([k, v]) => { if (v) qs.set(k, v); });
    return `/shop?${qs.toString()}`;
  };
  return <main className="shop-page">
    <div className="shop-heading"><span className="eyebrow">THE EVU EDIT</span><h1>Discover<br/><em>the collection.</em></h1>
      <div className="shop-description"><p>Explore pieces designed for the way you live.</p><span>{result.count} PIECES</span></div>
    </div>
    <form action="/shop" method="get" role="search" style={{display:"flex",gap:"0.75rem",flexWrap:"wrap",margin:"1rem 0"}}>
      <label htmlFor="shop-q">Search products</label>
      <input id="shop-q" name="q" type="search" defaultValue={q} maxLength={120} placeholder="Search EVU products" />
      {department && <input type="hidden" name="department" value={department} />}
      <label htmlFor="shop-sort">Sort by</label>
      <select id="shop-sort" name="sort" defaultValue={sort}>
        <option value="newest">Newest</option><option value="price_asc">Price: low to high</option>
        <option value="price_desc">Price: high to low</option><option value="name">Name</option>
      </select>
      <button type="submit">Apply</button>
    </form>
    <nav aria-label="Shop departments" style={{display:"flex",flexWrap:"wrap",gap:"1rem",margin:"1rem 0 2rem"}}>
      {["all",...DEPARTMENTS].map(d=><Link key={d} href={link({department:d==="all"?undefined:d,page:"1"})}
        aria-current={(department || "all")===d?"page":undefined} style={{textTransform:"capitalize",textDecoration:(department||"all")===d?"underline":"none"}}>{d}</Link>)}
    </nav>
    {result.results.length ? <CollectionGrid products={result.results}/> : <p>No products matched. Try a different search or department.</p>}
    <nav aria-label="Product pages" style={{display:"flex",justifyContent:"space-between",margin:"2rem 0"}}>
      {result.previous && page>1 ? <Link href={link({page:String(page-1)})}>Previous page</Link> : <span/>}
      <span>Page {page}</span>
      {result.next ? <Link href={link({page:String(page+1)})}>Next page</Link> : <span/>}
    </nav>
  </main>;
}
