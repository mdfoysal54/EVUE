"""Read-only Django route and commerce-contract inventory. Run via manage.py shell."""
import json
from django.urls import URLPattern, URLResolver, get_resolver
from django.conf import settings

KEYWORDS = ('cart', 'checkout', 'order', 'payment', 'pay', 'shipping', 'return', 'auth', 'product', 'variant', 'wishlist', 'site', 'control', 'refund')

def walk(patterns, prefix=''):
    for p in patterns:
        route = prefix + str(p.pattern)
        if isinstance(p, URLResolver):
            yield from walk(p.url_patterns, route)
        elif isinstance(p, URLPattern):
            cb = p.callback
            yield {'route': route, 'name': p.name, 'view': f'{cb.__module__}.{getattr(cb, "__name__", cb.__class__.__name__)}'}

routes = list(walk(get_resolver().url_patterns))
relevant = [r for r in routes if any(k in r['route'].lower() for k in KEYWORDS)]
print(json.dumps({'root_urlconf': settings.ROOT_URLCONF, 'route_count': len(routes), 'commerce_routes': relevant}, indent=2, default=str))
