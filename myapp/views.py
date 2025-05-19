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
from .forms import CommentForm
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect


# Create your views here.
def home(request):
    return render(request, "home.html")


from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Task
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
import json

@login_required
@require_POST
@csrf_exempt
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

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def reorder_tasks(request):
    try:
        data = json.loads(request.body)
        ordered_task_ids = data.get('ordered_task_ids', [])
        # Update the order field of tasks based on the new order
        for order, task_id in enumerate(ordered_task_ids):
            task = Task.objects.filter(id=task_id, user=request.user).first()
            if task:
                task.order = order
                task.save()
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('task_detail', task_id=task_id)
    else:
        form = CommentForm()

    return render(request, "task_detail.html", {"task": task, "comments": comments, "form": form})


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


from django.db import models

def task_list(request):
    if not request.user.is_authenticated:
        return redirect("login")

    category_id = request.GET.get("category")
    sort_by = request.GET.get("sort_by")

    # Filter tasks based on the logged-in user, shared tasks, and selected category
    if category_id:
        tasks = Task.objects.filter(
            (models.Q(user=request.user) | models.Q(shared_users=request.user)),
            category_id=category_id
        ).distinct()
    else:
        tasks = Task.objects.filter(
            models.Q(user=request.user) | models.Q(shared_users=request.user)
        ).distinct()

    # Apply sorting
    if sort_by == "priority":
        tasks = tasks.order_by('priority')
    elif sort_by == "due_date":
        tasks = tasks.order_by('due_date')
    else:
        tasks = tasks.order_by('created_at')

    categories = Category.objects.filter(user=request.user)

    # Optionally, you can add a message if there are no tasks
    if not tasks.exists():
        messages.info(request, "You have no tasks available. Please create a task.")

    return render(request, 'task_list.html', {
        'tasks': tasks,
        'categories': categories,
        'sort_by': sort_by,
    })


from .forms import TaskForm

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
        due_date = request.POST.get("due_date")
        priority = request.POST.get("priority")
        category_id = request.POST.get("category")
        reminder_str = request.POST.get("reminder")
        reminder = None
        if reminder_str:
            from django.utils.dateparse import parse_datetime
            reminder = parse_datetime(reminder_str)
        recurrence = request.POST.get("recurrence")

        category = Category.objects.filter(id=category_id, user=request.user).first()

        task = Task.objects.create(
            user=request.user,
            title=title,
            description=description,
            due_date=due_date if due_date else None,
            priority=priority,
            category=category,
            reminder=reminder,
            recurrence=recurrence,
        )

        # Send reminder email immediately if reminder is set
        if task.reminder:
            send_task_reminder_email(task)

        # Handle recurring tasks creation
        if task.recurrence != 'none':
            from datetime import timedelta
            from django.utils import timezone

            def create_recurring_tasks(task):
                next_due_date = task.due_date
                if isinstance(next_due_date, str):
                    from django.utils.dateparse import parse_datetime
                    next_due_date = parse_datetime(next_due_date)
                for _ in range(5):  # Create next 5 occurrences
                    if task.recurrence == 'daily':
                        next_due_date += timedelta(days=1)
                    elif task.recurrence == 'weekly':
                        next_due_date += timedelta(weeks=1)
                    elif task.recurrence == 'monthly':
                        # Approximate monthly by adding 30 days
                        next_due_date += timedelta(days=30)
                    new_task = Task.objects.create(
                        user=task.user,
                        title=task.title,
                        description=task.description,
                        due_date=next_due_date,
                        category=task.category,
                        priority=task.priority,
                        reminder=task.reminder,
                        recurrence='none',
                        parent_task=task,
                    )
                    new_task.save()

            create_recurring_tasks(task)

        messages.success(request, "Task created successfully")
        return redirect("task_list")

    return render(request, "task_create.html", {"categories": categories})


@login_required(login_url="login")
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        task.delete()
        messages.success(request, "Task delete successfully")
        return redirect("task_list")

    return render(request, "delete_task.html", {"task": task})


from .forms import TaskForm

@login_required(login_url="login")
def task_update(request, task_id):
    task = get_object_or_404(Task, id=task_id)

    if request.method == "POST":
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            form.save_m2m()  # Save many-to-many data for shared_users

            # Handle recurring tasks update if needed (optional: you can implement logic here)

            messages.success(request, "Task updated successfully")
            return redirect("task_list")
    else:
        form = TaskForm(instance=task)

    return render(request, "task_create.html", {"form": form, "task": task})


@login_required(login_url="login")
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    comments = task.comments.all().order_by('-created_at')

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.task = task
            comment.user = request.user
            comment.save()
            return redirect('task_detail', task_id=task_id)
    else:
        form = CommentForm()

    return render(request, "task_detail.html", {"task": task, "comments": comments, "form": form})


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

from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET

@login_required
@require_GET
def check_new_notifications(request):
    # For demonstration, return static notifications
    notifications = [
        {"message": "You have a task due soon!"},
    ]
    return JsonResponse({"new_notifications": notifications})
