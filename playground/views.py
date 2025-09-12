import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateTaskForm
from .forms import RegisterForm
from .models import Task

# Create your views here.

User = get_user_model()

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


def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect("login")
    return render(request, "accounts/logout.html")
    
@login_required
def home_view(request):
    return render(request, 'playground_app/home.html')

@login_required
def task_list_view(request):
    tasks = Task.objects.select_related("assigned_user").order_by("due_date")
    users = User.objects.order_by("username")

    return render(request, "tasks/task_list.html", {
        "tasks": tasks,
        "users": users,                              # <-- for the Assignee dropdown
        "task_choices": Task.task_choices,           # <-- for the Status dropdown
        # or: "task_choices": Task._meta.get_field("task_status").choices
    })

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

User = get_user_model()

@login_required
@require_POST
def task_update_view(request, pk):
    # Only process if the row Save button was clicked
    if request.POST.get("action") != "save_row":
        return redirect("task_list")

    task = get_object_or_404(Task, pk=pk)

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

    if assignee_id:
        try:
            task.assigned_user = User.objects.get(pk=assignee_id)
        except User.DoesNotExist:
            messages.error(request, "Selected assignee does not exist.")
            return redirect("task_list")
    
    if due_str == "":
        task.due_date = None
    else:
        try:
            task.due_date = datetime.date.fromisoformat(due_str)
        except ValueError:
            messages.error(request, "Invalid date format.")
            return redirect("task_list")

    task.save()
    messages.success(request, "Task updated.")
    return redirect("task_list")

# class ProtectedView(LoginRequiredMixin, View):
#     login_url = '/login/'
#     redirect_field_name = 'redirect_to'

#     def get(self, request):
#         return render(request, 'registration/protected.html')

# def contact_view(request):
#     if request.method == "POST":
#         form = TaskForm(request.POST)
#         if form.is_valid():
#             form.send_email()
#             return redirect('contact-success')
#     else:
#         form = TaskForm()
#     context = {'form':form}
#     return render(request, 'contact.html', context)

# def contact_success_view(request):
#     return render(request, 'contact_success.html')

# def register_view(request):
#     if request.method == "POST":
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             return redirect("home")
#     else:
#         form = CustomUserCreationForm()
#     return render(request, "accounts/register.html", {"form": form})