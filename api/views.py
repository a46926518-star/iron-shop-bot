
from rest_framework.viewsets import ModelViewSet
from rest_framework import generics, permissions, viewsets
from .models import Category, Product, Order, CartItem
from .serializers import (
    CategorySerializer, ProductSerializer, OrderSerializer,
    CartItemSerializer, RegisterSerializer
)
# Create your views here.
class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by('-id')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]


class ProductViewSet(ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class OrderListView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

class CartListView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)