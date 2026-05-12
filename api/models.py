from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE, verbose_name="Kategoriya")
    name = models.CharField(max_length=255, verbose_name="Mahsulot nomi")
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)  # Shuni qo'shing
    description = models.TextField(verbose_name="Tavsif")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Narxi")
    image = models.ImageField(upload_to='products/', verbose_name="Rasm")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

class Master(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='master_profile')
    full_name = models.CharField(max_length=255, verbose_name="Usta ismi")
    specialty = models.CharField(max_length=255, verbose_name="Ixtisosligi")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqami")
    experience = models.PositiveIntegerField(verbose_name="Tajribasi (yil)")
    photo = models.ImageField(upload_to='masters/', verbose_name="Rasmi", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Hozir ishlaydimi?")

    def __str__(self):
        return f"{self.full_name} - {self.specialty}"

    class Meta:
        verbose_name = "Usta"
        verbose_name_plural = "Ustalar"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username


# 5. Lead (Landing page - lead form uchun)
class Lead(models.Model):
    full_name = models.CharField(max_length=255, verbose_name="Ism sharfi")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqami")
    message = models.TextField(blank=True, null=True, verbose_name="Xabar")
    is_contacted = models.BooleanField(default=False, verbose_name="Bog'lanildimi?")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Lead (Landing page arizasi)"
        verbose_name_plural = "Leadlar"


class Cart(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Yangi'),
        ('process', 'Jarayonda'),
        ('finished', 'Bitgan'),
        ('canceled', 'Bekor qilingan'),
    ]
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    master = models.ForeignKey(Master, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders')
    full_name = models.CharField(max_length=255, verbose_name="Mijoz ismi")
    phone_number = models.CharField(max_length=20, verbose_name="Telefon raqami")
    address = models.TextField(verbose_name="Manzil")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Holati")
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Umumiy summa")

    # Kanban doskasida elementlar tartibini saqlash uchun
    kanban_order = models.PositiveIntegerField(default=0, verbose_name="Kanban tartibi")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id} - {self.full_name}"

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['kanban_order', '-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sotilgan narxi")


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=255, verbose_name="Ismi")
    subject = models.CharField(max_length=255, verbose_name="Mavzu")
    message = models.TextField(verbose_name="Xabar")
    created_at = models.DateTimeField(auto_now_add=True)


class Wishlist(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)


class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Kutilmoqda'),
        ('completed', 'Toʻlangan'),
        ('failed', 'Xato'),
    ]
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    transaction_id = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)