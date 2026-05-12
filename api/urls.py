from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'masters', views.MasterViewSet)
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'cart-items', views.CartItemViewSet)
router.register(r'orders', views.OrderViewSet)
router.register(r'order-items', views.OrderItemViewSet)
router.register(r'leads', views.LeadViewSet)
router.register(r'wishlist', views.WishlistViewSet)
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'last-sold', views.LastSoldViewSet, basename='last-sold')
router.register(r'top-products', views.TopProductsViewSet, basename='top-products')
router.register(r'feedback', views.FeedbackViewSet)
router.register(r'profiles', views.ProfileViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('create-order/', views.CreateOrderView.as_view(), name='create-order'),
    path('webhook/telegram/', views.telegram_webhook, name='telegram-webhook'),
]