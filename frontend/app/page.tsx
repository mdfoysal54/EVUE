import Link from "next/link";
import { ArrowUpRight, ArrowDownRight } from "lucide-react";
import { getProducts } from "@/lib/catalog";
import ProductCard from "@/components/ProductCard";

export default async function Home() {
  const products = await getProducts();

  return (
    <main>
      {/* 1. HERO SECTION */}
      <section className="home-hero">
        <div className="hero-container">
          <div className="hero-left">
            <div className="hero-edition">
              <span className="dot" /> THE EVU EDITION{" "}
              <span>— 2026 / 27</span>
            </div>

            <h1>
              Style that<br />
              <em>speaks</em><br />
              softly<span className="hero-period">.</span>
            </h1>

            <p className="hero-lede">
              An expression of modern elegance. Thoughtful silhouettes, effortless
              confidence, and pieces to make your own.
            </p>

            <div className="hero-cta-row">
              <Link className="dark-button" href="/shop">
                EXPLORE COLLECTION <ArrowUpRight size={17} />
              </Link>
              <Link className="text-link" href="/editorial">
                DISCOVER OUR STORY <ArrowUpRight size={15} />
              </Link>
            </div>

            <div className="hero-bottom">
              <span>01 — 04 / THE NEW PERSPECTIVE</span>
              <span>
                SCROLL TO EXPLORE <ArrowDownRight size={15} />
              </span>
            </div>
          </div>

          <div className="hero-visual">
            <div className="hero-photo">
              <div className="hero-art-inner">
                <span>EVU</span>
                <i>
                  THE ART OF<br />
                  BEING YOU
                </i>
              </div>
            </div>
            <div className="hero-visual-label">
              <span>THE MODERN MUSE</span>
              <span>AN EDITORIAL STUDY · Nº 001</span>
            </div>
          </div>
        </div>
      </section>

      {/* 2. INTRO BANNER STRIP */}
      <section className="intro-strip">
        <span>CONSIDERED BY DESIGN</span>
        <span>MADE FOR REAL LIFE</span>
        <span>AN EXPRESSION OF YOU</span>
      </section>

      {/* 3. FEATURED CURATION */}
      <section className="featured-section">
        <div className="section-top">
          <div>
            <span className="eyebrow">01 / THE CURATION</span>
            <h2>
              The pieces<br />
              <em>you return to.</em>
            </h2>
          </div>

          <div>
            <p>
              Discover a thoughtful edit of modern wardrobe essentials — each
              chosen for its effortless versatility.
            </p>
            <Link className="underlined-link" href="/shop">
              SHOP ALL PIECES <ArrowUpRight size={16} />
            </Link>
          </div>
        </div>

        {products.length ? (
          <div className="editorial-grid">
            {products.slice(0, 4).map((p, i) => (
              <ProductCard key={p.id} product={p} index={i} />
            ))}
          </div>
        ) : (
          <div className="empty-editorial">
            <span>THE COLLECTION IS COMING</span>
            <h3>
              Something considered<br />
              <em>is on its way.</em>
            </h3>
            <p>Our next edit is being curated. Check back for new arrivals.</p>
          </div>
        )}
      </section>

      {/* 4. STORY / PHILOSOPHY SPLIT */}
      <section className="story-split">
        <div className="story-visual">
          <div className="story-visual-word">EVU</div>
          <span>02 / THE PHILOSOPHY</span>
        </div>

        <div className="story-copy">
          <span className="eyebrow">BEYOND THE EVERYDAY</span>
          <h2>
            Less noise.<br />
            More <em>meaning.</em>
          </h2>
          <p>
            We believe style is personal. An invitation to dress with intention,
            embrace individuality and find beauty in the details.
          </p>
          <Link className="underlined-link" href="/about">
            EXPLORE THE HOUSE <ArrowUpRight size={16} />
          </Link>
        </div>
      </section>

      {/* 5. EDITORIAL QUOTE */}
      <section className="quote-section">
        <span className="eyebrow">THE EVU POINT OF VIEW</span>
        <blockquote>
          “Elegance is not about being noticed. It’s about being <em>remembered.</em>”
        </blockquote>
        <span>AN EXPLORATION OF PERSONAL STYLE</span>
      </section>

      {/* 6. CLOSING CTA */}
      <section className="closing-section">
        <div>
          <span className="eyebrow">03 / YOUR NEXT CHAPTER</span>
          <h2>
            Find your<br />
            <em>signature.</em>
          </h2>
        </div>
        <Link
          className="round-arrow"
          href="/shop"
          aria-label="Explore collection"
        >
          <ArrowUpRight size={32} />
        </Link>
      </section>
    </main>
  );
}