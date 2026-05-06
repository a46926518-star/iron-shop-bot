from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'products', views.ProductViewSet, basename='product')

urlpatterns = [
    path('', include(router.urls)), # /api/products/ avtomatik hosil bo'ladi
    path('kategoriyalar/', views.CategoryListView.as_view(), name='category-list'),
    path('register/', views.RegisterView.as_view(), name='auth_register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('cart/', views.CartListView.as_view(), name='cart-list'),
    path('orders/', views.OrderListView.as_view(), name='order-list'),
]