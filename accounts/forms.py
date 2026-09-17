from django.contrib.auth.forms import UserCreationForm

from .models import User


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True
        self.fields["role"].choices = [
            (User.Role.STUDENT, User.Role.STUDENT.label),
            (User.Role.BUSINESS, User.Role.BUSINESS.label),
        ]
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")
