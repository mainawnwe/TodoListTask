from django.shortcuts import render, redirect, get_object_or_404
from .models import Task, Category
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm, ProfileForm, RegistrationForm
from .models import Profile
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from myapp.utils import send_task_reminder_email
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required


# Create your views here.
def home(request):
    return render(request, "home.html")


@login_required
@require_POST
def toggle_task_completion(request):
    task_id = request.POST.get('task_id')
    is_completed = request.POST.get('is_completed') == 'true'

    try:
        task = Task.objects.get(id=task_id, user=request.user)
        task.is_completed = is_completed
        task.save()
        return JsonResponse({'success': True, 'is_completed': task.is_completed})
    except Task.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Task not found or unauthorized'}, status=404)


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
    if not request.user.is_authenticated:
        return redirect("login")

    category_id = request.GET.get("category")

    # Filter tasks based on the logged-in user and selected category
    if category_id:
        tasks = Task.objects.filter(user=request.user, category_id=category_id)
    else:
        tasks = Task.objects.filter(user=request.user)

    categories = Category.objects.filter(user=request.user)

    # Optionally, you can add a message if there are no tasks
    if not tasks.exists():
        messages.info(request, "You have no tasks available. Please create a task.")

    return render(request, 'task_list.html', {
        'tasks': tasks,
        'categories': categories,
    })


@login_required(login_url="login")
def task_create(request):
    # Default categories to add if user has none
    default_category_names = [
        "Work", "Personal", "Shopping", "Health", "Finance",
        "Education", "Home", "Travel", "Fitness", "Others"
    ]

    # Check if user has any categories, if not create default ones
    user_categories = Category.objects.filter(user=request.user)
    if not user_categories.exists():
        for name in default_category_names:
            Category.objects.get_or_create(name=name, user=request.user)

    categories = Category.objects.filter(user=request.user)

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        created_at = request.POST.get("created_at")
        due_date = request.POST.get("due_date")
        is_completed = request.POST.get("is_completed") == "on"
        category_id = request.POST.get("category")
        new_category_name = request.POST.get("new_category").strip()
        priority = request.POST.get("priority")
        reminder = request.POST.get("reminder")

        if new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name, user=request.user)
        else:
            category = Category.objects.filter(user=request.user).get(id=category_id) if category_id else None

        task = Task(
            title=title,
            description=description,
            created_at=created_at,
            due_date=due_date,
            is_completed=is_completed,
            category=category,
            user=request.user,
            priority=priority,
            reminder=reminder if reminder else None,
        )
        task.save()
        # Send reminder email immediately if reminder is set
        if task.reminder:
            send_task_reminder_email(task)
        messages.success(request, "Task created successfully")
        if category:
            return redirect(f"{request.path}?category={category.id}")
        else:
            return redirect("task_list")

    return render(request, "task_form.html", {"categories": categories, "task": None})


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
        task.priority = request.POST.get("priority")
        reminder = request.POST.get("reminder")
        task.reminder = reminder if reminder else None

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
