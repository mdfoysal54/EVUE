import CollectionGrid from "@/components/CollectionGrid";
import {getProducts} from "@/lib/catalog";
export default async function Shop(){const products=await getProducts();return <main className="shop-page"><div className="shop-heading"><span className="eyebrow">THE EVU EDIT / 2026</span><h1>Discover<br/><em>the collection.</em></h1><div className="shop-description"><p>A modern wardrobe, considered in every detail. Explore pieces designed for the way you live.</p><span>{String(products.length).padStart(2,"0")} PIECES</span></div></div><CollectionGrid products={products}/></main>}
