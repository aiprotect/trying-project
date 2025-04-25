from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile

@receiver(post_save, sender=User)
def user_profile_handler(sender, instance, created, **kwargs):
    """
    ایجاد خودکار پروفایل هنگام ثبت کاربر جدید
    """
    if created:
        UserProfile.objects.create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
            