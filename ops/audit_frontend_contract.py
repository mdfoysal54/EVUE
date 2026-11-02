"""Read-only Next.js endpoint inventory with redaction; Python 3.10+."""
from pathlib import Path
import argparse
import json
import re

parser = argparse.ArgumentParser()
parser.add_argument('--frontend', type=Path, default=Path('frontend'))
parser.add_argument('--output', type=Path, default=Path('ops/frontend-endpoints.json'))
args = parser.parse_args()
if not args.frontend.is_dir():
    parser.error(f'Frontend directory not found: {args.frontend}')
ignore = {'node_modules', '.next', 'dist', 'build', '.git', 'coverage'}
pattern = re.compile(r'''(?:(?:fetch|axios\.(?:get|post|put|patch|delete))\s*\(\s*|\bapi\s*(?:<[^>]+>)?\s*\(\s*)(["'`])([^"'`\n]{1,250})\1''')
rows = []
for file in args.frontend.rglob('*'):
    if not file.is_file() or file.suffix not in {'.ts', '.tsx', '.js', '.jsx'} or any(part in ignore for part in file.parts):
        continue
    if file.stat().st_size > 1024 * 1024:
        continue
    text = file.read_text(encoding='utf-8', errors='replace')
    for match in pattern.finditer(text):
        endpoint = match.group(2)
        if '?' in endpoint:
            endpoint = endpoint.split('?', 1)[0] + '?[query omitted]'
        if not (endpoint.startswith('/') or endpoint.startswith('v1/') or endpoint.startswith('v2/') or endpoint.startswith('api/')):
            continue
        rows.append({'file': str(file.relative_to(args.frontend)), 'line': text.count('\n', 0, match.start()) + 1, 'endpoint': endpoint})
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text(json.dumps(sorted(rows, key=lambda r: (r['file'], r['line'])), indent=2) + '\n', encoding='utf-8')
print(f'Wrote {len(rows)} literal endpoint references to {args.output}. Dynamic URLs require manual review.')
