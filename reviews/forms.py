from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["rating", "comment_text"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{'★' * i}{'☆' * (5 - i)}（{i}）") for i in range(5, 0, -1)]
            ),
            "comment_text": forms.Textarea(
                attrs={"rows": 3, "placeholder": "使ってみた感想を書く（任意）"}
            ),
        }
