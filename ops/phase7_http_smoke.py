#!/usr/bin/env python3
"""EVU Phase 7: safe GET-only HTTP smoke checks, no authentication or writes."""
import argparse
import json
import ssl
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--frontend", default="http://localhost:3000")
    ap.add_argument("--backend", default="http://127.0.0.1:8000")
    ap.add_argument("--output", type=Path, default=Path("ops/phase7-http-report.json"))
    args = ap.parse_args()
    targets = [("frontend", args.frontend, "/"), ("catalog", args.backend, "/api/catalog/products/")]
    results = []
    for name, base, path in targets:
        u = urllib.parse.urlparse(base)
        if u.scheme not in ("http", "https") or not u.hostname:
            ap.error(f"Invalid URL for {name}: {base}")
        url = base.rstrip("/") + path
        request = urllib.request.Request(url, method="GET", headers={"User-Agent": "EVU-Phase7-Smoke/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                status, error = response.status, None
        except urllib.error.HTTPError as exc:
            status, error = exc.code, str(exc)
        except (urllib.error.URLError, TimeoutError) as exc:
            status, error = None, str(exc)
        results.append({"check": name, "url": url, "status": status, "error": error, "ok": status == 200})
        print(f"{name}: {status if status is not None else error}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    if not all(item["ok"] for item in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()