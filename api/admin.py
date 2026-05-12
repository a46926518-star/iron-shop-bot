from django.contrib import admin
from .models import (
    Category, Product, Master, Profile,
    Lead, Cart, CartItem, Order,
    OrderItem, Feedback, Wishlist, Payment
)

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'status', 'total_price', 'master', 'created_at']
    list_filter = ['status', 'created_at', 'master']
    search_fields = ['full_name', 'phone_number', 'id']
    list_editable = ['status', 'master']
    inlines = [OrderItemInline]

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_available', 'created_at']
    list_filter = ['category', 'is_available']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'specialty', 'experience', 'is_active']
    list_filter = ['specialty', 'is_active']
    search_fields = ['full_name', 'phone_number']

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone_number', 'is_contacted', 'created_at']
    list_filter = ['is_contacted', 'created_at']
    search_fields = ['full_name', 'phone_number']

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'telegram_id', 'phone']
    search_fields = ['user__username', 'phone', 'telegram_id']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']

admin.site.register(Category)
admin.site.register(Feedback)
admin.site.register(Wishlist)
admin.site.register(Cart)
admin.site.register(CartItem)