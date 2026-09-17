from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404, redirect

from spots.models import Spot

from .forms import CommentForm


@login_required
def submit_review(request, spot_id):
    spot = get_object_or_404(Spot, pk=spot_id, status=Spot.Status.APPROVED)

    if request.method != "POST":
        return redirect("spots:detail", pk=spot.id)

    if spot.comments.filter(user=request.user).exists():
        messages.error(request, "このスポットには既に評価を投稿済みです。")
        return redirect("spots:detail", pk=spot.id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.spot = spot
        try:
            with transaction.atomic():
                comment.save()
            messages.success(request, "コメントを投稿しました。")
        except IntegrityError:
            messages.error(request, "このスポットには既に評価を投稿済みです。")
    else:
        messages.error(request, "入力内容を確認してください。")

    return redirect("spots:detail", pk=spot.id)
