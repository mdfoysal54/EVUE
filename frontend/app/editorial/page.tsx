import Link from "next/link";

export default function Editorial() {
  return (
    <main className="editorial-page">
      <span className="eyebrow">THE EVU JOURNAL</span>

      <h1>
        Stories worth<br />
        <em>wearing.</em>
      </h1>

      <div className="editorial-feature">
        <div className="editorial-feature-art">EVU</div>

        <div>
          <span className="eyebrow">VOL. 01 / OUR POINT OF VIEW</span>
          <h2>
            Style begins<br />
            with intention.
          </h2>
          <p>
            Our journal is taking shape. Soon, discover the stories behind the
            edit, wardrobe inspiration and new perspectives on everyday
            elegance.
          </p>

          <Link className="underlined-link" href="/shop">
            DISCOVER THE COLLECTION ↗
          </Link>
        </div>
      </div>
    </main>
  );
}