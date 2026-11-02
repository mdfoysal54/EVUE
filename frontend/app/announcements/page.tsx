import Link from "next/link";

interface Notice {
  id: number;
  title: string;
  body: string;
  slug: string | null;
  kind: string;
}

interface AnnouncementsResponse {
  results?: Notice[];
}

const API_BASE_URL =
  process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";

async function getAnnouncements(): Promise<Notice[]> {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/operations/announcements/`,
      {
        next: { revalidate: 60 },
      }
    );

    if (!response.ok) {
      return [];
    }

    const data: AnnouncementsResponse = await response.json();
    return data.results || [];
  } catch {
    return [];
  }
}

export default async function Announcements() {
  const items = await getAnnouncements();

  return (
    <main className="editorial-page">
      <span className="eyebrow">EVU / NEWS</span>
      <h1>Announcements</h1>

      {items.length > 0 ? (
        items.map((notice) => (
          <article key={notice.id} style={{ marginBottom: "2rem" }}>
            <span className="eyebrow">{notice.kind}</span>
            <h2>{notice.title}</h2>
            <p>
              {notice.body.length > 240
                ? `${notice.body.slice(0, 240)}...`
                : notice.body}
            </p>
            {notice.slug && (
              <Link href={`/announcements/${notice.slug}`}>
                Read more
              </Link>
            )}
          </article>
        ))
      ) : (
        <p>No current announcements.</p>
      )}
    </main>
  );
}