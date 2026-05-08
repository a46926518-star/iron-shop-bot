from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from api.views import telegram_webhook
from django.http import JsonResponse

def home(request):
    return JsonResponse({"status": "ok"})

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'products', views.ProductViewSet, basename='product')

router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet, basename='cart-item')

router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'order-items', views.OrderItemViewSet, basename='order-item')

router.register(r'wishlist', views.WishlistViewSet, basename='wishlist')
router.register(r'payments', views.PaymentViewSet, basename='payment')

router.register(r'last-sold', views.LastSoldViewSet, basename='last-sold')
router.register(r'top-products', views.TopProductsViewSet, basename='top-products')

urlpatterns = [
    path('', include(router.urls)),
    path("webhook/", telegram_webhook),
    path('profile/', views.ProfileView.as_view()),
    path("", home),
    path('feedback/', views.FeedbackCreateView.as_view()),
    path('auth/register/', views.RegisterView.as_view()),
    path('auth/login/', views.LoginView.as_view()),
]