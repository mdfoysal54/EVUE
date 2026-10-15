import Link from "next/link";
import type { Product } from "@/lib/catalog";
import { money } from "@/lib/catalog";
import WishlistButton from "@/components/WishlistButton";

interface ProductCardProps {
  product: Product;
  index?: number;
}

export default function ProductCard({
  product,
  index = 0,
}: ProductCardProps) {
  return (
    <article className="editorial-product">
      <div className="editorial-product-image">
        <Link
          href={`/product/${encodeURIComponent(product.slug)}`}
          aria-label={`View ${product.name}`}
        >
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} loading="lazy" />
          ) : (
            <div className="product-placeholder">
              <span>EVU</span>
              <small>THE COLLECTION</small>
            </div>
          )}
        </Link>

        <div className="product-index">
          {String(index + 1).padStart(2, "0")}
        </div>

        <WishlistButton id={product.id} />

        <Link
          className="quick-view"
          href={`/product/${encodeURIComponent(product.slug)}`}
        >
          DISCOVER PIECE ↗
        </Link>
      </div>

      <div className="product-text">
        <div>
          <span className="eyebrow">{product.category || "THE EDIT"}</span>
          <Link href={`/product/${encodeURIComponent(product.slug)}`}>
            <h3>{product.name}</h3>
          </Link>
        </div>
        <p>{money(product.price, product.currency)}</p>
      </div>
    </article>
  );
}