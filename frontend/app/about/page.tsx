import Link from "next/link";

export default function About() {
  return (
    <main className="editorial-page">
      <span className="eyebrow">ABOUT THE HOUSE</span>
      
      <h1>
        Considered.<br />
        <em>Always.</em>
      </h1>

      <div className="about-copy">
        <p>
          EVU is an emerging contemporary fashion concept exploring personal
          style, restraint and the beauty of a thoughtful wardrobe.
        </p>
        <p>
          We are building a more expressive place to discover pieces that fit
          your life. Details about materials, manufacturing and sourcing will be
          published as they are verified.
        </p>

        <Link className="dark-button" href="/shop">
          EXPLORE THE COLLECTION ↗
        </Link>
      </div>
    </main>
  );
}