from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.utils import timezone
from django.views.decorators.http import require_GET
from .models import Announcement, Offer, Notification, TransactionRecord
from django.contrib.auth import get_user_model
from catalog.models import Product

@require_GET
def announcements(request):
    return JsonResponse({'results': list(Announcement.objects.filter(published=True).order_by('-created_at').values('id','title','body','important','created_at')[:30])})

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