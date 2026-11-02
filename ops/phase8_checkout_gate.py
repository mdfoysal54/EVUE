"""Read-only EVU checkout readiness gate. Python 3.10+; stdlib only."""
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

DEFAULT_PATHS = ["/", "/api/catalog/products/"]

def fetch(url, timeout):
    request = urllib.request.Request(url, headers={"User-Agent": "EVU-Phase8-ReadOnly-Gate/1.0"}, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return {"url": url, "status": response.status, "content_type": response.headers.get("Content-Type", "")}
    except urllib.error.HTTPError as error:
        return {"url": url, "status": error.code, "error": str(error.reason)}
    except (urllib.error.URLError, TimeoutError) as error:
        return {"url": url, "status": None, "error": str(error)}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="http://127.0.0.1:8000")
    parser.add_argument("--frontend", default="http://127.0.0.1:3000")
    parser.add_argument("--output", default="ops/phase8-readiness.json")
    parser.add_argument("--timeout", type=float, default=10)
    args = parser.parse_args()
    results = [fetch(args.frontend.rstrip("/") + "/", args.timeout),
               fetch(args.backend.rstrip("/") + "/api/catalog/products/", args.timeout)]
    report = {"read_only": True, "checks": results,
              "pass": all(item["status"] == 200 for item in results),
              "warning": "HTTP 200 is not proof that checkout, payment or fulfillment works."}
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if report["pass"] else 1

if __name__ == "__main__":
    sys.exit(main())
