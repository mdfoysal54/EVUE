import json
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

User = get_user_model()

def payload(request):
    try:
        data = json.loads(request.body)
        return data if isinstance(data, dict) else None
    except (ValueError, UnicodeDecodeError):
        return None

@ensure_csrf_cookie
@require_GET
def csrf(request):
    return JsonResponse({"status": "ok"})

@require_POST
def register(request):
    data = payload(request)
    if data is None:
        return JsonResponse({"error": "Invalid JSON object"}, status=400)
    username = data.get("username", "")
    email = data.get("email", "")
    password = data.get("password", "")
    if not all(isinstance(x, str) for x in (username, email, password)):
        return JsonResponse({"error": "Invalid input"}, status=400)
    username, email = username.strip(), email.strip().lower()
    if not (3 <= len(username) <= 150) or len(email) > 254 or "@" not in email:
        return JsonResponse({"error": "Invalid username or email"}, status=400)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({"error": "Account cannot be created"}, status=400)
    candidate = User(username=username, email=email)
    try:
        validate_password(password, user=candidate)
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password)
            from .models import CustomerProfile
            CustomerProfile.objects.create(user=user)
    except (ValidationError, IntegrityError) as exc:
        if isinstance(exc, ValidationError):
            return JsonResponse({"error": exc.messages}, status=400)
        return JsonResponse({"error": "Account cannot be created"}, status=400)
    return JsonResponse({"id": user.pk, "username": user.username}, status=201)

@require_POST
def sign_in(request):
    data = payload(request)
    if not data or not isinstance(data.get("username"), str) or not isinstance(data.get("password"), str):
        return JsonResponse({"error": "Invalid credentials"}, status=400)
    user = authenticate(request, username=data["username"], password=data["password"])
    if user is None or not user.is_active:
        return JsonResponse({"error": "Invalid credentials"}, status=401)
    login(request, user)
    return JsonResponse({"id": user.pk, "username": user.username})

@require_POST
def sign_out(request):
    logout(request)
    return JsonResponse({"status": "ok"})

@require_GET
def me(request):
    if not request.user.is_authenticated or not request.user.is_active:
        return JsonResponse({"error": "Authentication required"}, status=401)
    return JsonResponse({"id": request.user.pk, "username": request.user.username, "email": request.user.email})