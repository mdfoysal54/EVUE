"""Guarded, idempotent source patch. Run from D:\\Ecommerce\\EVUE after backup.
Aborts if existing files differ from the audited baseline; never force overwrites.
"""
from pathlib import Path
import sys

root = Path.cwd()
page = root / 'frontend/app/page.tsx'
urls = root / 'backend/evu/urls.py'
if not page.is_file() or not urls.is_file():
    sys.exit('ERROR: Run from the EVU project root; expected frontend/app/page.tsx and backend/evu/urls.py')

source = page.read_text(encoding='utf-8')
if 'getHomeAppearance' in source:
    print('Homepage already appears integrated; no changes to homepage')
else:
    changes = [
      ('import ProductCard from "@/components/ProductCard";', 'import ProductCard from "@/components/ProductCard";\nimport { getHomeAppearance } from "@/lib/site-appearance";'),
      ('  const products = await getProducts();', '  const [products, home] = await Promise.all([getProducts(), getHomeAppearance()]);\n  const featured = products.filter((p) => p.featured);\n  const curated = (featured.length ? featured : products).slice(0, 4);'),
      ('            <h1>\n              Style that<br />\n              <em>speaks</em><br />\n              softly<span className="hero-period">.</span>\n            </h1>', '            <h1>{home.hero?.heading || <>Style that<br /><em>speaks</em><br />softly<span className="hero-period">.</span></>}</h1>'),
      ('              An expression of modern elegance. Thoughtful silhouettes, effortless\n              confidence, and pieces to make your own.', '              {home.hero?.subtitle || "An expression of modern elegance. Thoughtful silhouettes, effortless confidence, and pieces to make your own."}'),
      ('            <div className="hero-photo">', '            <div className="hero-photo" style={home.hero?.desktop_background ? {backgroundImage: `url(${home.hero.desktop_background})`, backgroundSize: "cover", backgroundPosition: "center"} : undefined}>'),
      ('            <h2>\n              The pieces<br />\n              <em>you return to.</em>\n            </h2>', '            <h2>{home.featured?.heading || <>The pieces<br /><em>you return to.</em></>}</h2>'),
      ('              Discover a thoughtful edit of modern wardrobe essentials — each\n              chosen for its effortless versatility.', '              {home.featured?.subtitle || "Discover a thoughtful edit of modern wardrobe essentials — each chosen for its effortless versatility."}'),
      ('{products.slice(0, 4).map((p, i) => (', '{curated.map((p, i) => ('),
      ('          <h2>\n            Less noise.<br />\n            More <em>meaning.</em>\n          </h2>', '          <h2>{home.story?.heading || <>Less noise.<br />More <em>meaning.</em></>}</h2>'),
      ('            We believe style is personal. An invitation to dress with intention,\n            embrace individuality and find beauty in the details.', '            {home.story?.subtitle || "We believe style is personal. An invitation to dress with intention, embrace individuality and find beauty in the details."}'),
      ('          “Elegance is not about being noticed. It’s about being <em>remembered.</em>”', '          {home.quote?.heading || <>“Elegance is not about being noticed. It’s about being <em>remembered.</em>”</>}'),
      ('          <h2>\n            Find your<br />\n            <em>signature.</em>\n          </h2>', '          <h2>{home.closing?.heading || <>Find your<br /><em>signature.</em></>}</h2>'),
    ]
    for before, after in changes:
        count = source.count(before)
        if count != 1:
            sys.exit(f'ABORT: Expected exactly one homepage snippet; found {count}: {before[:90]!r}. Your source has changed; merge manually.')
        source = source.replace(before, after, 1)
    page.write_text(source, encoding='utf-8')
    print('PATCHED frontend/app/page.tsx')

routes = urls.read_text(encoding='utf-8')
if 'sitecontrol.urls' in routes:
    print('Sitecontrol already registered; leaving root URLs unchanged')
else:
    needle = "    path('api/operations/', include('operations.urls'))," 
    if routes.count(needle) != 1:
        sys.exit('ABORT: root URL baseline differs; register api/site/ manually')
    routes = routes.replace(needle, needle + '\n    path("api/site/", include("sitecontrol.urls")),', 1)
    urls.write_text(routes, encoding='utf-8')
    print('PATCHED backend/evu/urls.py')
