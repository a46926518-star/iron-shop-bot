import json
import requests
from django.conf import settings
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import viewsets, generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action


from .models import (
    Category, Product, Master, Profile,
    Lead, Cart, CartItem, Order,
    OrderItem, Feedback, Wishlist, Payment
)
from .serializers import (
    CategorySerializer, ProductSerializer, ProfileSerializer,
    CartSerializer, CartItemSerializer, OrderSerializer,
    OrderItemSerializer, WishlistSerializer, FeedbackSerializer,
    PaymentSerializer, MasterSerializer, LeadSerializer
)
from django.shortcuts import render

def kanban_page(request):
    return render(request, 'kanban.html')

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
            send_telegram_msg(chat_id, f"✔ Xabar qabul qilindi: {text}")
            return JsonResponse({"ok": True})
        except Exception as e:
            return JsonResponse({"ok": False, "error": str(e)})
    return JsonResponse({"ok": False})

def send_telegram_msg(chat_id, text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": chat_id, "text": text})
    except:
        pass

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_available=True)
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)
        category = self.request.query_params.get('category')
        search = self.request.query_params.get('search')
        if category:
            queryset = queryset.filter(category_id=category)
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(description__icontains=search))
        return queryset

class MasterViewSet(viewsets.ModelViewSet):
    queryset = Master.objects.all()
    serializer_class = MasterSerializer

    @action(detail=False, methods=['get'])
    def my_orders(self, request):
        if not hasattr(request.user, 'master_profile'):
            return Response({"error": "Usta profili topilmadi"}, status=status.HTTP_403_FORBIDDEN)
        orders = Order.objects.filter(master=request.user.master_profile)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.all()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            msg = f"🔔 Buyurtma #{order.id} holati o'zgardi: {order.get_status_display()}"
            send_telegram_msg(settings.TELEGRAM_ADMIN_ID, msg)
            return Response({'status': 'updated'})
        return Response({'error': 'Noto‘g‘ri status'}, status=status.HTTP_400_BAD_REQUEST)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

class CreateOrderView(APIView):
    def post(self, request):
        data = request.data
        product_ids = data.get('product_ids', [])
        order = Order.objects.create(
            user=request.user.profile if request.user.is_authenticated else None,
            full_name=data.get('full_name'),
            phone_number=data.get('phone_number'),
            address=data.get('address', ''),
            total_price=0
        )
        total = 0
        for pid in product_ids:
            try:
                product = Product.objects.get(id=pid)
                OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)
                total += product.price
            except Product.DoesNotExist:
                continue
        order.total_price = total
        order.save()
        return Response({"order_id": order.id, "total": total}, status=status.HTTP_201_CREATED)

class CartViewSet(viewsets.ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user__user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet):
    queryset = CartItem.objects.all()
    serializer_class = CartItemSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class FeedbackViewSet(viewsets.ModelViewSet):
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

class WishlistViewSet(viewsets.ModelViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer

class LastSoldViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    def get_queryset(self):
        return Product.objects.filter(orderitem__isnull=False).distinct().order_by("-id")[:7]

class TopProductsViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    def get_queryset(self):
        return Product.objects.all().order_by("-id")[:10]

class RegisterView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if User.objects.filter(username=username).exists():
            return Response({"error": "User mavjud"}, status=status.HTTP_400_BAD_REQUEST)
        User.objects.create_user(username=username, password=password)
        return Response({"message": "OK"}, status=status.HTTP_201_CREATED)

class LoginView(APIView):
    def post(self, request):
        user = authenticate(username=request.data.get('username'), password=request.data.get('password'))
        if user:
            return Response({"message": "Success"})
        return Response({"error": "Xato"}, status=status.HTTP_401_UNAUTHORIZED)