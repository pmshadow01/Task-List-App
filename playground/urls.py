from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path("", views.login_view, name='login'),
    path('home/', views.home_view, name='home'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('task_list/', views.task_list_view, name='task_list'),
    path('task_list/task_form/', views.create_task_view, name='task_form'),
    path("tasks/<int:pk>/delete/", views.task_delete_view, name="task_delete"),
    path("tasks/bulk-delete/", views.tasks_bulk_delete_view, name="tasks_bulk_delete"),
    path("tasks/<int:pk>/update/", views.task_update_view, name="task_update"),
]