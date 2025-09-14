"""
Disclaimer:
    This app does not support password reset functionality as it is for demo purposes only.
    Users register and sign in with a username instead of an email.
    Thank you for your understanding.
"""
from django import forms
from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError
from .models import Task

User = get_user_model()

class CreateTaskForm(forms.ModelForm):
    # Model-backed form for creating/editing tasks.
    class Meta:
        model = Task
        fields = ["task_name", "assigned_user", "task_status", "due_date",]
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date"}),   # native date picker
            "description": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "task_name": "Task name",
            "assigned_user": "Assignee: ",
            "task_status": "Status",
            "due_date": "Due date",
        }


class RegisterForm(forms.ModelForm):
    # Form-only fields
    username = forms.CharField(max_length=150, help_text="Keep it simple!")
    password = forms.CharField(widget=forms.PasswordInput, help_text="Password must be 8 characters long.")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password", help_text="Enter the same password again for verification.")

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm']

    def clean(self):
        # Run default cleaning, then enforce matching passwords and validators.
        cleaned = super().clean()
        pw  = cleaned.get("password")
        pw2 = cleaned.get("password_confirm")
        if pw and pw2 and pw != pw2:
            raise forms.ValidationError("Passwords do not match")
        # Apply Django’s password validators
        if pw:
            try:
                password_validation.validate_password(pw, user=User(username=cleaned.get("username")))
            except ValidationError as e:
                self.add_error("password", e)
        return cleaned

    def save(self, commit=True):
        # IMPORTANT: hash the password before saving
        user = super().save(commit=False)  # instance currently has raw password set by ModelForm
        user.set_password(self.cleaned_data["password"])  # hashes and overwrites
        if commit:
            user.save()
        return user