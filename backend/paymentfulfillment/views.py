from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from variantcommerce.models import Purchase
from .models import PaymentAttempt, Delivery
from .services import PaymentError, prepare_payment, verify_and_finalize
from .gateway import GatewayError, initiate

class StartPayment(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, purchase_id):
        try:
            attempt, delivery = prepare_payment(request.user, purchase_id, request.data)
            base = getattr(settings, 'EVU_PUBLIC_BACKEND_URL', '').rstrip('/')
            if not base.startswith('https://') and not getattr(settings, 'DEBUG', False):
                raise GatewayError('Public HTTPS callback URL required')
            if not base:
                raise GatewayError('EVU_PUBLIC_BACKEND_URL is required')
            url, session = initiate(attempt, delivery, base)
            attempt.gateway_session = session
            attempt.save(update_fields=['gateway_session'])
            return Response({'payment_url': url, 'transaction_id': attempt.transaction_id})
        except Purchase.DoesNotExist:
            raise Http404
        except (PaymentError, GatewayError) as exc:
            return Response({'error': str(exc)}, status=409)

@method_decorator(csrf_exempt, name='dispatch')
class GatewayIPN(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        validation_id = request.data.get('val_id')
        try:
            purchase = verify_and_finalize(validation_id)
        except (PaymentError, GatewayError) as exc:
            return Response({'error': str(exc)}, status=409)
        return Response({'received': True, 'order_id': str(purchase.pk)})

@method_decorator(csrf_exempt, name='dispatch')
class GatewayReturn(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    def post(self, request):
        # Browser redirects are NOT payment verification. IPN performs server-to-server validation.
        return Response({'message': 'Payment response received. Check your order status after verification.'})
    def get(self, request):
        return Response({'message': 'Payment status pending gateway verification. Sign in to check your order.'})

class OrderTracking(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, purchase_id):
        purchase = Purchase.objects.filter(pk=purchase_id, user=request.user).first()
        if not purchase:
            raise Http404
        delivery = Delivery.objects.filter(purchase=purchase).first()
        data = {'id': str(purchase.pk), 'payment_status': purchase.status, 'total': str(purchase.total), 'currency': purchase.currency, 'shipping': None}
        if delivery:
            data['shipping'] = {'status': delivery.status, 'courier': delivery.courier, 'tracking_number': delivery.tracking_number,
                'events': [{'status': e.status, 'note': e.note, 'at': e.created_at.isoformat()} for e in delivery.events.all()]}
        return Response(data)
