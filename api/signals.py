import requests
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Order, Lead

def send_telegram_notification(text):
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_ADMIN_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram yuborishda xato: {e}")

@receiver(post_save, sender=Order)
def order_status_notify(sender, instance, created, **kwargs):
    if created:
        text = (
            f"🛒 <b>Yangi buyurtma!</b>\n\n"
            f"<b>ID:</b> #{instance.id}\n"
            f"<b>Mijoz:</b> {instance.full_name}\n"
            f"<b>Tel:</b> {instance.phone_number}\n"
            f"<b>Summa:</b> {instance.total_price} so'm"
        )
        send_telegram_notification(text)
    else:
        text = (
            f"🔔 <b>Buyurtma holati o'zgardi!</b>\n\n"
            f"<b>ID:</b> #{instance.id}\n"
            f"<b>Mijoz:</b> {instance.full_name}\n"
            f"<b>Yangi holat:</b> {instance.get_status_display()}"
        )
        send_telegram_notification(text)

@receiver(post_save, sender=Lead)
def lead_notify(sender, instance, created, **kwargs):
    if created:
        text = (
            f"🚀 <b>Yangi Lead (Landing page)!</b>\n\n"
            f"<b>Ism:</b> {instance.full_name}\n"
            f"<b>Tel:</b> {instance.phone_number}\n"
            f"<b>Xabar:</b> {instance.message if instance.message else 'Xabar yo\'q'}"
        )
        send_telegram_notification(text)