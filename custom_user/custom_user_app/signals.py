from django.db.models.signals import post_save
from .models import CustomUser, Profile
from django.dispatch import receiver


@receiver(post_save, sender=CustomUser)
def hello_profile(sender, instance, created, *args, **kwargs):
    if created:
        instance.address = 'address'
        instance.phone_number = '12321123'
        instance.country = 'India'
        Profile.objects.create(user=instance, address=instance.address, phone_number=instance.phone_number, country=instance.country)
