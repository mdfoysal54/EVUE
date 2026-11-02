
import Link from "next/link";
import { notFound } from "next/navigation";
import VariantSelector from "@/components/VariantSelector";
import WishlistButton from "@/components/WishlistButton";
import { getProduct, money } from "@/lib/catalog";

interface ProductPageProps {
  params: { slug: string } | Promise<{ slug: string }>;
}

export default async function ProductPage({ params }: ProductPageProps) {
  const { slug } = await params;
  const product = await getProduct(slug);

  if (!product) notFound();

  return (
    <main className="product-page">
      <div className="detail-image">
        {product.image_url ? (
          <img src={product.image_url} alt={product.name} />
        ) : (
          <div className="product-placeholder">
            <span>EVU</span>
            <small>THE COLLECTION</small>
          </div>
        )}
      </div>

      <div className="detail-content">
        <Link className="eyebrow" href="/shop">
          ← BACK TO THE COLLECTION
        </Link>

        <div className="detail-title">
          <span className="eyebrow">
            {product.category || "THE EVU EDIT"}
          </span>

          <h1>{product.name}</h1>

          <div className="detail-price">
            From {money(product.price, product.currency || "BDT")}{" "}
            <WishlistButton id={product.id} />
          </div>
        </div>

        <p className="detail-description">
          {product.description ||
            "Explore this piece from the EVU collection."}
        </p>

        <VariantSelector productId={product.id} />
      </div>
    </main>
  );
}
