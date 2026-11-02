import {NextResponse} from 'next/server';
export async function GET(request: Request) {
  const upstream = process.env.API_INTERNAL_URL || 'http://127.0.0.1:8000';
  const placement = new URL(request.url).searchParams.get('placement') || '';
  try {
    const res = await fetch(`${upstream}/api/operations/announcements/?placement=${encodeURIComponent(placement)}`, {cache:'no-store',signal:AbortSignal.timeout(8000)});
    if (!res.ok) throw new Error('Unavailable');
    return NextResponse.json(await res.json(), {headers:{'Cache-Control':'no-store'}});
  } catch { return NextResponse.json({results:[]}, {status:503}); }
}