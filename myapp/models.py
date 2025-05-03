from django.db import models
from django.contrib.auth.models import User

<<<<<<< HEAD
class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'name')

    def __str__(self):
        return self.name

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('High', 'High'),
        ('Medium', 'Medium'),
        ('Low', 'Low'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Medium')
    reminder = models.DateTimeField(null=True, blank=True)
=======

# Create your models here.
class Task(models.Model):
    title = models.CharField((""), max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE , null=True)  # Link task to user

>>>>>>> 2e5f3ce78f39aed0b4848893b4ae6d9b0a25f350

    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
<<<<<<< HEAD
    profile_pic = models.ImageField(
        upload_to='profile_picture/',
        default='images/default-profile.jpg'
    )
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"
=======
    profile_pic = models.ImageField(upload_to='profile_picture/', default='images/default-profile.jpg')
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"
>>>>>>> 2e5f3ce78f39aed0b4848893b4ae6d9b0a25f350
