from django.http import Http404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Variant, VariantCartItem, Purchase, VariantPreorder, PreorderAllocation
from .services import CommerceError,put_cart,cart_rows,reserve_checkout,cancel_purchase,reserve_preorder,cancel_preorder

def order_data(p):
    return {'id':str(p.pk),'status':p.status,'total':str(p.total),'currency':p.currency,'expires_at':p.expires_at.isoformat(), 'lines':[{'sku':x.variant.sku,'quantity':x.quantity,'price':str(x.unit_price),'location':x.inventory.location.code} for x in p.lines.select_related('variant','inventory__location')]}

class Variants(APIView):
    permission_classes=[]
    def get(self,request,product_id):
        qs=Variant.objects.filter(product_id=product_id,active=True,product__active=True).order_by('sku')[:100]
        return Response({'variants':[{'id':str(v.pk),'sku':v.sku,'size':v.size,'color':v.color,'price':str(v.price),'currency':v.product.currency} for v in qs.select_related('product')]})

class Cart(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request): return Response({'items':[{'variant_id':str(i.variant_id),'sku':i.variant.sku,'product':i.variant.product.name,'quantity':i.quantity,'price':str(i.variant.price)} for i in cart_rows(request.user)]})
    def post(self,request):
        try: put_cart(request.user,request.data.get('variant_id'),request.data.get('quantity'))
        except (CommerceError,ValueError,TypeError) as e: return Response({'error':str(e)},status=400)
        return self.get(request)
    def delete(self,request):
        VariantCartItem.objects.filter(user=request.user,variant_id=request.data.get('variant_id')).delete()
        return self.get(request)

class Checkout(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try: p,created=reserve_checkout(request.user,request.data.get('idempotency_key'))
        except CommerceError as e: return Response({'error':str(e)},status=409)
        return Response(order_data(p),status=201 if created else 200)

class Purchases(APIView):
    permission_classes=[IsAuthenticated]
    def get(self,request):
        return Response({'orders':[order_data(p) for p in Purchase.objects.filter(user=request.user).order_by('-created_at')[:30]]})

class CancelPurchase(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,pk):
        try: p=cancel_purchase(request.user,pk)
        except Purchase.DoesNotExist: raise Http404
        except CommerceError as e: return Response({'error':str(e)},status=409)
        return Response(order_data(p))

class Preorder(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request):
        try: item,created=reserve_preorder(request.user,request.data.get('allocation_id'),request.data.get('quantity'),request.data.get('idempotency_key'))
        except PreorderAllocation.DoesNotExist: raise Http404
        except (CommerceError,ValueError,TypeError) as e: return Response({'error':str(e)},status=409)
        return Response({'id':str(item.pk),'status':item.status,'quantity':item.quantity,'paid':False},status=201 if created else 200)

class CancelPreorder(APIView):
    permission_classes=[IsAuthenticated]
    def post(self,request,pk):
        try: item=cancel_preorder(request.user,pk)
        except VariantPreorder.DoesNotExist: raise Http404
        return Response({'id':str(item.pk),'status':item.status})
