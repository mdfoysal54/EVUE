from decimal import Decimal
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from variantcommerce.models import Purchase
from paymentfulfillment.models import Delivery
from .models import ShippingZone, ReturnRequest

class ShippingQuote(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        city = str(request.query_params.get("city", "")).strip()
        if not city or len(city) > 100:
            return Response({"error": "A valid city is required"}, status=400)
        zone = ShippingZone.objects.filter(city__iexact=city, active=True).first()
        if not zone:
            return Response({"error": "Shipping is not configured for this city"}, status=404)
        return Response({"city": zone.city, "shipping_fee": str(zone.fee), "currency": "BDT", "estimate_only": True,
                         "notice": "This fee is not included in the current payment amount. Do not collect it separately."})

class CustomerReturns(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rows = ReturnRequest.objects.filter(user=request.user).order_by("-created_at")[:50]
        return Response({"returns": [{"id": r.id, "purchase_id": str(r.purchase_id), "status": r.status,
                                       "reason": r.reason, "created_at": r.created_at.isoformat()} for r in rows]})

    def post(self, request):
        purchase_id = request.data.get("purchase_id")
        reason = str(request.data.get("reason", "")).strip()
        if not purchase_id or not 10 <= len(reason) <= 2000:
            return Response({"error": "purchase_id and a reason of 10–2000 characters are required"}, status=400)
        try:
            purchase = Purchase.objects.filter(pk=purchase_id, user=request.user, status=Purchase.State.PAID).first()
        except (ValueError, TypeError):
            purchase = None
        if not purchase:
            raise Http404
        delivery = Delivery.objects.filter(purchase=purchase, status=Delivery.State.DELIVERED).first()
        if not delivery:
            return Response({"error": "Returns may be requested after delivery"}, status=409)
        obj, created = ReturnRequest.objects.get_or_create(purchase=purchase, user=request.user,
                                                          defaults={"reason": reason})
        return Response({"id": obj.id, "status": obj.status, "created": created}, status=201 if created else 200)