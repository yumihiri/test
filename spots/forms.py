from django import forms

from .models import Category, Spot


class SpotForm(forms.ModelForm):
    latitude = forms.DecimalField(widget=forms.HiddenInput())
    longitude = forms.DecimalField(widget=forms.HiddenInput())

    class Meta:
        model = Spot
        fields = [
            "name",
            "address",
            "category",
            "description",
            "image",
            "latitude",
            "longitude",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None and user.role == "student":
            self.fields["category"].queryset = Category.objects.filter(
                student_registrable=True
            )
        for name in ("name", "address", "category", "description"):
            self.fields[name].widget.attrs.setdefault("class", "form-control")
