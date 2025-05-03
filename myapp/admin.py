from django.contrib import admin
from myapp.models import Task, Profile, Category

# Register your models here.
admin.site.register(Task)
admin.site.register(Profile)
admin.site.register(Category)
