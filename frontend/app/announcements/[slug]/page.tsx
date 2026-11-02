import Link from "next/link";
import { notFound } from "next/navigation";

interface AnnouncementItem {
  body: string;
  cta_label?: string;
  cta_url?: string;
  title: string;
}

interface AnnouncementDetailProps {
  params: {
    slug: string;
  };
}

const API_BASE_URL =
  process.env.API_INTERNAL_URL || "http://127.0.0.1:8000";

async function getAnnouncement(slug: string): Promise<AnnouncementItem | null> {
  try {
    const encodedSlug = encodeURIComponent(slug);
    const response = await fetch(
      `${API_BASE_URL}/api/operations/announcements/${encodedSlug}/`,
      {
        next: { revalidate: 60 },
      }
    );

    if (!response.ok) {
      return null;
    }

    return await response.json();
  } catch {
    return null;
  }
}

function isInternalUrl(url?: string): boolean {
  return Boolean(url && url.startsWith("/") && !url.startsWith("//"));
}

export default async function AnnouncementDetail({
  params,
}: AnnouncementDetailProps) {
  const item = await getAnnouncement(params.slug);

  if (!item) {
    notFound();
  }

  return (
    <main className="editorial-page">
      <span className="eyebrow">EVU / NEWS</span>

      <h1>{item.title}</h1>

      <p style={{ whiteSpace: "pre-wrap" }}>{item.body}</p>

      {isInternalUrl(item.cta_url) && (
        <Link href={item.cta_url!}>
          {item.cta_label || "Explore"}
        </Link>
      )}
    </main>
  );
}