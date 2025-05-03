from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

# This signal is triggered when a new user is created
# The signal creates a new profile for the new user
# and saves it to the database
# The signal is connected to the User model
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # ✅ Only create a profile if it doesn't already exist
        Profile.objects.get_or_create(user=instance, defaults={"profile_pic": "profile_picture/default-profile.jpg"})

