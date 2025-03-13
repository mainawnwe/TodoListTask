from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm
from .models import Profile
from .forms import ProfileForm
from django.contrib.auth import update_session_auth_hash


# Create your views here.
def home(request):
    return render(request, "home.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Retrieve failed attempts from session
        failed_attempts = request.session.get("failed_attempts", 0)

        # Authenticate user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Reset failed attempts on successful login
            request.session["failed_attempts"] = 0
            login(request, user)
            messages.success(request, f"You are now logged in as {username}")
            return redirect("task_list")
        else:
            # Increment failed attempts if authentication fails
            failed_attempts += 1
            request.session["failed_attempts"] = failed_attempts
            messages.error(request, "Invalid username or password")

    else:
        # If GET request, just load the page
        failed_attempts = request.session.get("failed_attempts", 0)

    # Show "Forgot Password?" link if failed attempts >= 3
    show_forgot_password = failed_attempts >= 3

    return render(request, "myapp/login.html", {"show_forgot_password": show_forgot_password})


from django.contrib.auth.models import User
from .forms import RegistrationForm


from django.views.decorators.csrf import csrf_exempt

@csrf_exempt

def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            email = form.cleaned_data.get("email")

            # Prevent duplicate username and email
            if User.objects.filter(username=username).exists():
                messages.error(request, "Username already exists. Please choose a different one.")
                return redirect("register")

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already exists. Please use a different email address.")
                return redirect("register")

            # ✅ Just create the user (Profile will be created automatically via signals)
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()

            messages.success(request, "Your account has been created successfully. Please log in.")
            return redirect("login")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()

    return render(request, "myapp/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("home")


def task_list(request):
    if request.user.is_authenticated:
        tasks = Task.objects.filter(user=request.user)  # Only show tasks for the logged-in user
    else:
        tasks = None  # Set tasks to None if the user is not logged in

    return render(request, 'task_list.html', {'tasks': tasks})


@login_required(login_url="login")  # Ensure the user is logged in
def task_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        created_at = request.POST.get("created_at")
        due_date = request.POST.get("due_date")
        is_completed = request.POST.get("is_completed") == "on"

        task = Task(
            title=title,
            description=description,
            created_at=created_at,
            due_date=due_date,
            is_completed=is_completed,
            user=request.user  # Associate the task with the logged-in user
        )
        task.save()
        messages.success(request, "Task created successfully")
        return redirect("task_list")  # Redirect to task_list after creating the task
    return render(request, "task_form.html")  # Render the task form on GET request

@login_required(login_url="login")
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        task.delete()
        messages.success(request, "Task delete successfully")
        return redirect("task_list")

    return render(request, "delete_task.html", {"task": task})


@login_required(login_url="login")
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        task.title = request.POST.get("title")
        task.description = request.POST.get("description")
        task.due_date = request.POST.get("due_date")
        task.is_completed = request.POST.get("is_completed") == "on"

        task.save()
        messages.success(request, "Task updated successfully")
        return redirect("task_list")

    return render(request, "task_form.html", {"task": task})


@login_required(login_url="login")
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    return render(request, "task_detail.html", {"task": task})


@login_required
def profile(request):
    # Ensure the profile exists
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect after saving
    else:
        form = ProfileUpdateForm(instance=profile)

    return render(request, 'profile.html', {'form': form, 'profile': profile})

def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    return render(request, 'profile.html', {'profile': profile})

def update_profile(request):
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            return redirect('profile')  # Redirect after saving

    else:
        profile_form = ProfileForm(instance=request.user.profile)

    return render(request, 'profile.html', {'profile_form': profile_form})



from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse

def send_reset_email(request, token, user_email):
    # The email content
    subject = "Password Reset Request"
    message = f"""
    You're receiving this email because you requested a password reset for your user account.

    Please go to the following page and choose a new password:
    http://127.0.0.1:8000/reset/{token}/

    Your username, in case you’ve forgotten: {user_email}

    Thanks for using our site!
    """
    
    # Send the email to the user
    try:
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])
        messages.success(request, "Password reset email sent.")
        return HttpResponse("Email sent successfully!")
    except Exception as e:
        messages.error(request, f"Failed to send email: {e}")
        return HttpResponse("Failed to send email.")

import hashlib
import time
def generate_reset_token(user):
    timestamp = str(int(time.time()))
    token = hashlib.sha256((user.username + timestamp).encode()).hexdigest()
    return token    


from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator


def password_reset_view(request):
    if request.method == "POST":
        email = request.POST["email"]
        try:
            user = User.objects.get(email=email)
            
            # Generate the reset token and encode user ID
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(str(user.pk).encode())

            reset_link = request.build_absolute_uri(f'/reset/{uid}/{token}/')

            # Send the reset email to the user
            subject = "Password Reset Request"
            message = f"""
            You're receiving this email because you requested a password reset for your account.

            Please go to the following page and choose a new password:
            {reset_link}

            If you did not request this, please ignore this email.
            """
            
            # Send the email
            send_mail(subject, message, settings.EMAIL_HOST_USER, [email])
            messages.success(request, "Password reset email sent.")
            return redirect('password_reset_done')  # Redirect to a page confirming email sent

        except User.DoesNotExist:
            messages.error(request, "No user found with that email address.")
            return redirect('password_reset')  # Or show an error page

    return render(request, 'registration/password_reset.html')  # Show the password reset form

    




# reset password

def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
        
        if default_token_generator.check_token(user, token):
            if request.method == 'POST':
                new_password1 = request.POST['new_password1']
                new_password2 = request.POST['new_password2']

                if new_password1 == new_password2:
                    user.set_password(new_password1)
                    user.save()
                    messages.success(request, "Password reset successfully. You can now log in.")
                    return redirect('login')
                else:
                    messages.error(request, "Passwords do not match.")
            return render(request, 'registration/password_reset_confirm.html', {'uidb64': uidb64, 'token': token})
        else:
            messages.error(request, "The reset link is invalid or has expired.")
            return redirect('password_reset')

    except (User.DoesNotExist, ValueError, TypeError):
        messages.error(request, "Invalid reset link.")
        return redirect('password_reset')
