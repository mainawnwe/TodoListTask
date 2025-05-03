from django.urls import path
from . import views
from django.contrib.auth.views import PasswordResetView


urlpatterns = [
    path('', views.home, name='home'), # Root URL is now home
    path("task_list/", views.task_list, name="task_list"),  # Root URL is now task_list
    path("task_create/", views.task_create, name="task_create"),
    path("task_update/<int:task_id>/", views.task_update, name="task_update"),
    path("task_delete/<int:task_id>/", views.delete_task, name="delete_task"),
    path("task_detail/<int:task_id>/", views.task_detail, name="task_detail"),
    path('profile/', views.profile, name='profile'),
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),



]
