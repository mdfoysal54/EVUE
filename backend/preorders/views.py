from django.core.exceptions import ValidationError
from django.http import Http404
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView
from .models import Release, PreorderRequest, WaitlistEntry
from .services import reserve_preorder, cancel_request

class PublicReleases(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    def get(self, request):
        qs = Release.objects.select_related('product').filter(public=True, reveal_at__lte=timezone.now(), product__active=True).exclude(state__in=['draft', 'cancelled']).order_by('opens_at')[:100]
        return Response([{'id': r.id, 'product_id': str(r.product_id), 'name': r.product.name, 'slug': r.product.slug, 'state': r.state, 'opens_at': r.opens_at, 'closes_at': r.closes_at, 'expected_ship_start': r.expected_ship_start, 'expected_ship_end': r.expected_ship_end, 'can_reserve': r.is_open() and r.reserved < r.allocation, 'remaining': max(0, r.allocation-r.reserved)} for r in qs])

class ReserveInput(serializers.Serializer):
    release_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, max_value=100)
    idempotency_key = serializers.CharField(min_length=8, max_length=80)

class Reserve(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def post(self, request):
        s = ReserveInput(data=request.data)
        s.is_valid(raise_exception=True)
        try:
            item, created = reserve_preorder(customer=request.user, **s.validated_data)
        except Release.DoesNotExist:
            raise Http404
        except ValidationError as exc:
            return Response({'error': exc.messages}, status=status.HTTP_409_CONFLICT)
        return Response({'id': str(item.id), 'status': item.status, 'quantity': item.quantity, 'payment_status': 'not_charged', 'message': 'Reservation request recorded; this is not a paid order.'}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class Cancel(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def post(self, request, pk):
        try:
            item, changed = cancel_request(request_id=pk, customer=request.user)
        except PreorderRequest.DoesNotExist:
            raise Http404
        return Response({'id': str(item.id), 'status': item.status, 'changed': changed})

class JoinWaitlist(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    def post(self, request, pk):
        try:
            release = Release.objects.get(pk=pk, public=True, product__active=True, reveal_at__lte=timezone.now())
        except Release.DoesNotExist:
            raise Http404
        entry, created = WaitlistEntry.objects.get_or_create(release=release, customer=request.user)
        return Response({'joined': True, 'created': created}, status=201 if created else 200)
