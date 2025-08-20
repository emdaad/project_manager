import random
from django.core.mail import send_mail
from django.utils.timezone import now
from datetime import timedelta
from .models import OTP

def generate_otp(user):
    code = str(random.randint(100000, 999999))
    otp = OTP.objects.create(
        user=user,
        code=code,
        expires_at=now() + timedelta(minutes=5)
    )

    send_mail(
        "Your Login OTP",
        f"Your OTP is {code}. It expires in 5 minutes.",
        "noreply@example.com",
        [user.email],
        fail_silently=False,
    )
    return otp