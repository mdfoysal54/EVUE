export type SiteSection = {
  page: string;
  section: string;
  heading: string;
  subtitle: string;
  overlay_opacity: number;
  desktop_background: string | null;
  mobile_background: string | null;
  dark_background: string | null;
};
type AppearanceResponse = { sections: SiteSection[] };
const API_BASE = process.env.API_INTERNAL_URL || 'http://127.0.0.1:8000';

export async function getHomeAppearance(): Promise<Record<string, SiteSection>> {
  try {
    const response = await fetch(`${API_BASE}/api/site/appearance/`, {
      next: { revalidate: 60 },
    });
    if (!response.ok) return {};
    const data = (await response.json()) as AppearanceResponse;
    if (!Array.isArray(data.sections)) return {};
    const sections: Record<string, SiteSection> = {};
    for (const section of data.sections) {
      if (section.page === 'home' && typeof section.section === 'string') {
        sections[section.section] = section;
      }
    }
    return sections;
  } catch (error) {
    console.error('Site appearance unavailable; using EVU defaults', error);
    return {};
  }
}
