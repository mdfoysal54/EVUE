from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum, Q
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST
from .models import Announcement, Offer, Notification, TransactionRecord, NewsletterSubscription
from django.contrib.auth import get_user_model
from catalog.models import Product

def active_announcements():
    now = timezone.now()
    return Announcement.objects.filter(published=True).filter(
        Q(publish_from__isnull=True) | Q(publish_from__lte=now),
        Q(publish_until__isnull=True) | Q(publish_until__gt=now),
    ).order_by('-priority', '-created_at')

@require_GET
def announcements(request):
    placement = request.GET.get('placement', '')
    qs = active_announcements()
    if placement in ('bar', 'home'):
        qs = qs.filter(placement__in=(placement, 'both'))
    results = []
    for item in qs[:30]:
        results.append({'id': item.id, 'title': item.title, 'body': item.body,
            'slug': item.slug, 'kind': item.kind, 'placement': item.placement,
            'priority': item.priority, 'important': item.important,
            'image_url': request.build_absolute_uri(item.image.url) if item.image else '',
            'cta_label': item.cta_label, 'cta_url': item.cta_url,
            'created_at': item.created_at.isoformat()})
    return JsonResponse({'results': results})

@require_GET
def announcement_detail(request, slug):
    item = active_announcements().filter(slug=slug).first()
    if not item:
        return JsonResponse({'error': 'Not found'}, status=404)
    return JsonResponse({'id': item.id, 'title': item.title, 'body': item.body,
        'slug': item.slug, 'kind': item.kind, 'image_url': request.build_absolute_uri(item.image.url) if item.image else '',
        'cta_label': item.cta_label, 'cta_url': item.cta_url})

@require_POST
def subscribe_newsletter(request):
    import json
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        data = json.loads(request.body)
        email = str(data.get('email', '')).strip().lower()
        if not data.get('consent') or len(email) > 254:
            return JsonResponse({'error': 'Email and explicit consent required'}, status=400)
        validate_email(email)
    except (ValueError, TypeError, ValidationError, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid email or request'}, status=400)
    NewsletterSubscription.objects.update_or_create(email=email, defaults={'active': True})
    return JsonResponse({'message': 'Subscription request received'}, status=202)

@require_GET
def offers(request):
    now = timezone.now()
    return JsonResponse({'results': list(Offer.objects.filter(active=True, starts_at__lte=now, ends_at__gt=now).values('code','description','percent_off')[:30])})

@require_GET
def my_notifications(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error':'Authentication required'}, status=401)
    return JsonResponse({'results': list(Notification.objects.filter(user=request.user).order_by('-created_at').values('id','title','message','read','created_at')[:50])})

@require_GET
@staff_member_required
def reports(request):
    if not request.user.is_superuser:
        return JsonResponse({'error':'Forbidden'}, status=403)
    by_status = list(TransactionRecord.objects.values('status','currency').annotate(count=Count('id'), amount_minor=Sum('amount_minor')).order_by('status','currency'))
    return JsonResponse({'customers': get_user_model().objects.filter(is_staff=False).count(), 'blocked_customers':get_user_model().objects.filter(is_staff=False,is_active=False).count(), 'active_products':Product.objects.filter(active=True).count(), 'published_announcements':Announcement.objects.filter(published=True).count(), 'transactions_by_status_and_currency':by_status})