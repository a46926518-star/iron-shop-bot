from django.contrib import admin

# Register your models here.
from .models import Category, Product, Order, OrderItem, Profile, Feedback, CartItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    ordering = ('-created_at',)
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'user',
        'full_name',
        'phone_number',
        'status',
        'total_amount',
        'created_at'
    )

    list_filter = ('status', 'created_at')
    search_fields = ('full_name', 'phone_number')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
admin.site.register(Profile)
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'created_at')
    search_fields = ('subject', 'message')
    ordering = ('-created_at',)
admin.site.register(CartItem)