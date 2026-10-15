import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import CartItem, Order, Stock
from .services import CheckoutError, create_order, cancel_order

def auth_required(request):
    return request.user.is_authenticated and request.user.is_active

def parse(request):
    try:
        data = json.loads(request.body)
        return data if isinstance(data, dict) else None
    except (ValueError, UnicodeDecodeError):
        return None

def serialize_order(order):
    return {"id": str(order.pk), "status": order.status, "currency": order.currency,
            "total": str(order.total), "expires_at": order.expires_at.isoformat(),
            "items": [{"name": x.name, "quantity": x.quantity, "unit_price": str(x.unit_price)} for x in order.items.all()]}

@require_http_methods(["GET", "POST", "DELETE"])
def cart(request):
    if not auth_required(request):
        return JsonResponse({"error":"Authentication required"}, status=401)
    if request.method == "POST":
        data = parse(request)
        if not data or not isinstance(data.get("product_id"), str) or type(data.get("quantity")) is not int or not 1 <= data["quantity"] <= 20:
            return JsonResponse({"error":"Invalid product or quantity"},status=400)
        from catalog.models import Product
        try:
            product = Product.objects.get(pk=data["product_id"], active=True)
        except (Product.DoesNotExist, ValueError, TypeError):
            return JsonResponse({"error":"Product unavailable"},status=404)
        if not Stock.objects.filter(product=product).exists():
            return JsonResponse({"error":"Product unavailable"},status=409)
        CartItem.objects.update_or_create(user=request.user, product=product, defaults={"quantity":data["quantity"]})
    elif request.method == "DELETE":
        data = parse(request)
        if not data or not isinstance(data.get("product_id"),str):
            return JsonResponse({"error":"Invalid product"},status=400)
        CartItem.objects.filter(user=request.user, product_id=data["product_id"]).delete()
    items = CartItem.objects.filter(user=request.user).select_related("product")
    return JsonResponse({"items":[{"product_id":str(i.product_id),"name":i.product.name,"quantity":i.quantity,"unit_price":str(i.product.price),"currency":i.product.currency} for i in items]})

@require_http_methods(["GET", "POST"])
def orders(request):
    if not auth_required(request):
        return JsonResponse({"error":"Authentication required"},status=401)
    if request.method == "POST":
        try:
            order = create_order(request.user)
        except CheckoutError as exc:
            return JsonResponse({"error":str(exc)},status=409)
        return JsonResponse(serialize_order(order),status=201)
    return JsonResponse({"orders":[serialize_order(o) for o in Order.objects.filter(user=request.user).prefetch_related("items")[:50]]})

@require_http_methods(["GET", "POST"])
def order_detail(request, order_id):
    if not auth_required(request):
        return JsonResponse({"error":"Authentication required"},status=401)
    try:
        if request.method == "POST":
            order = cancel_order(request.user, order_id)
        else:
            order = Order.objects.prefetch_related("items").get(pk=order_id,user=request.user)
    except Order.DoesNotExist:
        return JsonResponse({"error":"Not found"},status=404)
    except CheckoutError as exc:
        return JsonResponse({"error":str(exc)},status=409)
    return JsonResponse(serialize_order(order))
