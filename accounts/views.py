from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import BusinessVerificationForm, SignupForm
from .models import BusinessVerification, User


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("spots:map")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        if self.object.role == User.Role.BUSINESS:
            return reverse_lazy("accounts:business_verification")
        return reverse_lazy("spots:map")

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        if self.object.role == User.Role.BUSINESS:
            messages.info(
                self.request,
                "経営者アカウントはスポット登録の前に本人確認情報の提出が必要です。",
            )
        return response


@login_required
def business_verification_view(request):
    user = request.user
    if user.role != User.Role.BUSINESS:
        messages.error(request, "経営者アカウントのみ利用できます。")
        return redirect("spots:map")

    verification = getattr(user, "business_verification", None)

    if verification and verification.status != BusinessVerification.Status.REJECTED:
        # 審査中・認証済みの場合はフォームを出さずステータスのみ表示
        return render(
            request, "accounts/business_verification_status.html", {"verification": verification}
        )

    if request.method == "POST":
        form = BusinessVerificationForm(
            request.POST, request.FILES, instance=verification
        )
        if form.is_valid():
            new_verification = form.save(commit=False)
            new_verification.user = user
            new_verification.status = BusinessVerification.Status.PENDING
            new_verification.reject_reason = ""
            new_verification.save()
            messages.success(request, "承認申請を受け付けました。管理者の審査をお待ちください。")
            return redirect("accounts:business_verification")
    else:
        form = BusinessVerificationForm(instance=verification)

    return render(
        request,
        "accounts/business_verification_form.html",
        {"form": form, "verification": verification},
    )
