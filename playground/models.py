from django.db import models
from django.conf import settings

# Create your models here.
class Task(models.Model):

    task_choices = [
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
        ("Unassigned", "Unassigned"),
    ]

    task_name = models.CharField(max_length=64)
    assigned_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, related_name='tasks_assgined',null=True, blank=True,)
    task_status = models.CharField(max_length=32, choices=task_choices, default="Unassigned",)
    due_date = models.DateField(null=True, blank=True)
    # description = models.TextField(blank=True)
    # notes = models.TextField(blank=True)



    # This is a string rep of tasks
    def __str__(self):
        user = self.assigned_user.username if self.assigned_user else "Unassigned"
        due  = self.due_date.strftime("%Y-%m-%d") if self.due_date else "No due date"
        return f"{self.task_name} — {self.task_status} (Assigned to {user}, Due {due})"
