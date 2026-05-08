from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User
from django.conf import settings

import requests

from .models import Product, Category, Order, OrderItem, CartItem, Profile, Feedback
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    OrderSerializer,
    CartItemSerializer,
    ProfileSerializer,
    FeedbackSerializer,
    OrderCreateSerializer
)

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

        # Telegram notification (TO‘G‘RI JOY)
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

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CartViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer



class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


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