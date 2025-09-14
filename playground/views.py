"""
Disclaimer:
    This app does not support password reset functionality as it is for demo purposes only.
    Users register and sign in with a username instead of an email.
    Thank you for your understanding.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.contrib import messages
from .forms import CreateTaskForm
from .forms import RegisterForm
from .models import Task
import datetime

# Create your views here.

User = get_user_model()

# Handles user registration from the RegisterForm class in forms.py. If the POST request and form is valid, a new user is created and logged in. Otherwise, the registration form is displayed.
def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})

# Logs in a user with username/password. Redirects on success, shows error on failure.
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'home'
            return redirect(next_url)
        messages.error(request, "Invalid credentials")
    return render(request, 'accounts/login.html')

# Logs out the current user and redirects them to the login page.
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("login")
    return render(request, "accounts/logout.html")

# Home page view requiring login with decorator. Nothing too fancy... yet. From this point on, all functions will have the @login_required decorator.
@login_required
def home_view(request):
    return render(request, 'playground_app/home.html')

# Task list view. You can add/remove/update tasks here with the other functions below this one. Tasks are sorted by due date by default.
@login_required
def task_list_view(request):
    tasks = Task.objects.select_related("assigned_user").order_by("due_date")
    users = User.objects.order_by("username")

    return render(request, "tasks/task_list.html", {
        "tasks": tasks,
        "users": users,                              # <-- for the Assignee dropdown
        "task_choices": Task.task_choices,           # <-- for the Status dropdown
    })

# Create tasks here using the CreateTaskForm class in forms.py. Once a task is created, there will be a return to task list button to take you back.
@login_required
def create_task_view(request):
    if request.method == "POST":
        form = CreateTaskForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Task created successfully!")
    else:
        form = CreateTaskForm()
    return render(request, "tasks/task_form.html", {"form": form})

# Task single and bulk delete views.
# get_object_or_404 is handy here since it avoids writing a full try/except block
# when fetching a single task. The @require_POST decorator ensures that these
# views can only be accessed via POST requests, which prevents accidental deletions
# from GET requests in a browser.
@login_required
@require_POST
def task_delete_view(request, pk):
    task = get_object_or_404(Task, pk=pk)
    task.delete()
    return redirect("task_list")

@login_required
@require_POST
def tasks_bulk_delete_view(request):
    ids = request.POST.getlist("ids")
    if ids:
        Task.objects.filter(id__in=ids).delete()
    return redirect("task_list")

# The task update view. Read in-line comments.
@login_required
@require_POST
def task_update_view(request, pk):
    # Only process if the row Save button was clicked
    if request.POST.get("action") != "save_row":
        return redirect("task_list")

    # Get the task or 404 if it doesn't exist.
    task = get_object_or_404(Task, pk=pk)

    # Inputs come from per-row fields.
    assignee_id = request.POST.get(f"assigned_user_{pk}")
    new_status  = request.POST.get(f"task_status_{pk}")
    due_str     = request.POST.get(f"due_date_{pk}", "").strip()

    # Validate and assign
    if new_status:
        valid = {v for v, _ in Task.task_choices}
        if new_status not in valid:
            messages.error(request, "Invalid status choice.")
            return redirect("task_list")
        task.task_status = new_status

    # If an assignee id was provided, ensure the user exists before assigning.
    # Note: leaving assignee_id blank keeps the current assignee
    if assignee_id:
        try:
            task.assigned_user = User.objects.get(pk=assignee_id)
        except User.DoesNotExist:
            messages.error(request, "Selected assignee does not exist.")
            return redirect("task_list")
        
    # Handle due date. Empty string clears it, otherwise display (YYYY-MM-DD).
    if due_str == "":
        task.due_date = None
    else:
        try:
            task.due_date = datetime.date.fromisoformat(due_str)
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect("task_list")
        
    # Persist changes and notify the user
    task.save()
    messages.success(request, "Task updated.")
    return redirect("task_list")