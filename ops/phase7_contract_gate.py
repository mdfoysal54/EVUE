#!/usr/bin/env python3
"""EVU Phase 7: read-only offline audit of route and frontend inventories."""
import argparse
import json
import re
import sys
from pathlib import Path

PATH_RE = re.compile(r"(?<![\w])/(?:api/)?[A-Za-z0-9_{}<>./:-]+")
METHOD_RE = re.compile(r"\b(GET|POST|PUT|PATCH|DELETE)\b", re.I)


def load(path):
    with open(path, encoding="utf-8-sig") as stream:
        return json.load(stream)


def strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from strings(item)
    elif isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in {"path", "url", "route", "endpoint", "pattern", "api", "method"} and isinstance(item, str):
                yield item
            else:
                yield from strings(item)


def normalize(path):
    path = path.split("?", 1)[0].split("#", 1)[0].strip()
    path = re.sub(r"<[^>]+>|\{[^}]+\}|:[a-zA-Z_][\w]*", "{param}", path)
    path = re.sub(r"/+", "/", path)
    return path.rstrip("/") or "/"


def endpoints(obj):
    found = set()
    for line in strings(obj):
        for match in PATH_RE.finditer(line):
            p = normalize(match.group(0))
            if p.startswith("/api/") or p == "/api":
                found.add(p)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", type=Path, required=True, help="Phase 6 django-routes.json")
    ap.add_argument("--frontend", type=Path, required=True, help="Phase 6 frontend-endpoints.json")
    ap.add_argument("--output", type=Path, default=Path("ops/phase7-contract-report.json"))
    args = ap.parse_args()
    try:
        backend = endpoints(load(args.backend))
        frontend = endpoints(load(args.frontend))
    except (OSError, ValueError) as exc:
        ap.error(f"Unable to read JSON inventories: {exc}")
    # Dynamic routes, proxies and prefixes can cause false positives: report only.
    missing = sorted(frontend - backend)
    report = {
        "note": "Heuristic inventory only; verify route prefixes, dynamic segments, proxy rewrites and HTTP methods manually.",
        "backend_paths": sorted(backend),
        "frontend_paths": sorted(frontend),
        "frontend_paths_without_exact_backend_match": missing,
        "counts": {"backend": len(backend), "frontend": len(frontend), "unmatched": len(missing)},
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Saved {args.output}; backend={len(backend)} frontend={len(frontend)} unmatched={len(missing)}")
    if not backend or not frontend:
        print("WARNING: one inventory has zero recognized /api paths; check Phase 6 JSON structure.")
    return 0


if __name__ == "__main__":
    sys.exit(main())