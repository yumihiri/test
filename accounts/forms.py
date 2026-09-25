from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import BusinessVerification, User


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


class BusinessVerificationForm(forms.ModelForm):
    class Meta:
        model = BusinessVerification
        fields = [
            "business_name",
            "representative_name",
            "corporate_number",
            "contact_email",
            "id_document",
        ]
        widgets = {
            "corporate_number": forms.TextInput(attrs={"placeholder": "1234567890123（13桁）"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name != "id_document":
                field.widget.attrs.setdefault("class", "form-control")
