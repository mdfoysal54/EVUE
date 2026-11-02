from django.db import IntegrityError, transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import WishlistItem
from .serializers import AddWishlistSerializer, WishlistItemSerializer

class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = WishlistItem.objects.filter(customer=request.user).select_related("product")
        return Response(WishlistItemSerializer(items, many=True, context={"request": request}).data)

    def post(self, request):
        serializer = AddWishlistSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        try:
            with transaction.atomic():
                item, created = WishlistItem.objects.get_or_create(customer=request.user, product=product)
        except IntegrityError:
            item = WishlistItem.objects.get(customer=request.user, product=product)
            created = False
        return Response(WishlistItemSerializer(item, context={"request": request}).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

class WishlistItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):
        deleted, _ = WishlistItem.objects.filter(customer=request.user, product_id=product_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
