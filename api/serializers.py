from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Category, Product, Order, OrderItem, Profile, Feedback, CartItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", "name", "image"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "image",
            "category",
            "category_name"
        ]

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "price"


        ]

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "full_name",
            "phone_number",
            "status",
            "total_amount",
            "created_at",
            "items"
        ]
        read_only_fields = ["status", "created_at"]

        def get_total_amount(self, obj):
            return sum(
                item.price * item.quantity
                for item in obj.items.all()
            )

class TelegramOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "full_name",
            "phone_number"
        ]

    def create(self, validated_data):
        # default status
        validated_data["status"] = "pending"

        order = Order.objects.create(**validated_data)
        return order



class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_name",
            "quantity",
            "user"
        ]
        read_only_fields = ["user"]

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Profile
        fields = [
            "id",
            "user",
            "username",
            "phone",
            "telegram_id"
        ]

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["username", "password", "email"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            password=validated_data["password"]
        )
        return user

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "user", "message", "created_at"]


from .models import Order, OrderItem, Product
from rest_framework import serializers


class OrderCreateSerializer(serializers.Serializer):
    product_ids = serializers.ListField(
        child=serializers.IntegerField()
    )
    full_name = serializers.CharField()
    phone_number = serializers.CharField()
