from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User


from rest_framework.viewsets import ModelViewSet
from .models import Category,Cart,CartItem,Feedback,Product,Payment,Profile,Wishlist,OrderItem,Order
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProfileSerializer,
    CartSerializer,
    CartItemSerializer,
    OrderSerializer,
    OrderItemSerializer,
    WishlistSerializer,
    FeedbackSerializer,
    PaymentSerializer,
    OrderCreateSerializer
)
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from django.conf import settings


@csrf_exempt
def telegram_webhook(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))

            message = data.get("message")
            if not message:
                return JsonResponse({"ok": False})

            chat_id = message["chat"]["id"]
            text = message.get("text", "")

            send_message(chat_id, f"✔ Bot ishlayapti: {text}")

            return JsonResponse({"ok": True})

        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)})

    return JsonResponse({"ok": False})
def send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    requests.post(url, data={
        "chat_id": chat_id,
        "text": text
    })


class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer





class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


class CartItemViewSet(ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class CreateOrderView(APIView):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_ids = serializer.validated_data['product_ids']

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            total_price=0
        )

        total = 0

        for pid in product_ids:
            product = Product.objects.get(id=pid)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1
            )

            total += product.price

        order.total_price = total
        order.save()

        try:
            requests.get(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                params={
                    "chat_id": settings.TELEGRAM_ADMIN_ID,
                    "text": f"🛒 Yangi buyurtma!\nID: {order.id}\nSumma: {total}"
                }
            )
        except Exception as e:
            print("Telegram error:", e)

        return Response({
            "message": "Order created",
            "order_id": order.id,
            "total": total
        })


class WishlistViewSet(ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer


class LastSoldViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.filter(orderitem__isnull=False).order_by("-id")[:7]


class TopProductsViewSet(ModelViewSet):
    serializer_class = ProductSerializer

    def get_queryset(self):
        return Product.objects.all().order_by("-id")[:10]

class CreateOrderView(APIView):
    def post(self, request):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_ids = serializer.validated_data['product_ids']

        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=serializer.validated_data['full_name'],
            phone_number=serializer.validated_data['phone_number'],
            total_amount=0
        )

        total = 0

        for pid in product_ids:
            product = Product.objects.get(id=pid)

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )

            total += product.price

        order.total_amount = total
        order.save()

        try:
            requests.get(
                f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage",
                params={
                    "chat_id": settings.TELEGRAM_ADMIN_ID,
                    "text": f"🛒 Yangi buyurtma!\nID: {order.id}\nSumma: {total}"
                }
            )
        except Exception as e:
            print("Telegram error:", e)

        return Response({
            "message": "Order created",
            "order_id": order.id,
            "total": total
        })



class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class FeedbackCreateView(generics.CreateAPIView):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer


class RegisterView(generics.CreateAPIView):
    def post(self, request):
        user = User.objects.create_user(
            username=request.data['username'],
            password=request.data['password']
        )
        return Response({"message": "User created"})


class LoginView(generics.GenericAPIView):
    def post(self, request):
        return Response({"message": "Login endpoint"})

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class LoginView(generics.GenericAPIView):
    def post(self, request):
        user = authenticate(
            username=request.data['username'],
            password=request.data['password']
        )

        if user:
            return Response({"message": "Login success"})
        return Response({"message": "Invalid credentials"}, status=400)