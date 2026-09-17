from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, TemplateView

from .forms import SpotForm
from .geocoding import GeocodingError, geocode_address, reverse_geocode
from .models import Category, Spot


class MapView(TemplateView):
    template_name = "spots/map.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        spots = Spot.objects.select_related("category").filter(status=Spot.Status.APPROVED)
        if user.is_authenticated:
            if user.role == "admin":
                spots = Spot.objects.select_related("category").exclude(
                    status=Spot.Status.APPROVED
                ) | spots
            else:
                mine = Spot.objects.select_related("category").filter(
                    registered_by=user
                ).exclude(status=Spot.Status.APPROVED)
                spots = spots | mine

        spots = spots.distinct().annotate(avg_rating=Avg("comments__rating"))

        spot_payload = [
            {
                "id": spot.id,
                "name": spot.name,
                "categoryId": spot.category_id,
                "lat": float(spot.latitude),
                "lng": float(spot.longitude),
                "description": spot.description,
                "status": spot.status,
                "avgRating": round(spot.avg_rating, 1) if spot.avg_rating else None,
                "reviewCount": spot.comments.count(),
                "detailUrl": f"/spots/{spot.id}/",
            }
            for spot in spots
        ]

        categories = list(
            Category.objects.values("id", "name", "icon_class", "color")
        )

        context["categories"] = categories
        context["spots"] = spot_payload
        return context


class SpotDetailView(DetailView):
    model = Spot
    template_name = "spots/detail.html"
    context_object_name = "spot"

    def get_object(self, queryset=None):
        spot = get_object_or_404(Spot.objects.select_related("category"), pk=self.kwargs["pk"])
        if not spot.is_visible_to(self.request.user):
            raise Http404("スポットが見つかりません")
        return spot

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        spot = context["spot"]
        context["reviews"] = spot.comments.select_related("user").order_by("-created_at")
        context["avg_rating"] = spot.comments.aggregate(avg=Avg("rating"))["avg"]
        if self.request.user.is_authenticated:
            context["already_reviewed"] = spot.comments.filter(
                user=self.request.user
            ).exists()
        context["can_delete"] = spot.can_be_deleted_by(self.request.user)
        return context


class SpotCreateView(LoginRequiredMixin, CreateView):
    model = Spot
    form_class = SpotForm
    template_name = "spots/register.html"
    success_url = reverse_lazy("spots:mypage")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.registered_by = self.request.user
        form.instance.status = Spot.Status.PENDING
        messages.success(self.request, "スポットを登録しました。管理者の承認をお待ちください。")
        return super().form_valid(form)


class SpotDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Spot
    success_url = reverse_lazy("spots:mypage")
    http_method_names = ["post"]

    def test_func(self):
        return self.get_object().can_be_deleted_by(self.request.user)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        raise Http404("スポットが見つかりません")

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, "スポットを削除しました。")
        return response


class MyPageView(LoginRequiredMixin, ListView):
    template_name = "spots/mypage.html"
    context_object_name = "spots"

    def get_queryset(self):
        return Spot.objects.select_related("category").filter(
            registered_by=self.request.user
        )


@require_POST
def geocode_view(request):
    address = request.POST.get("address", "").strip()
    if not address:
        return JsonResponse({"error": "住所を入力してください。"}, status=400)
    try:
        lat, lng = geocode_address(address)
    except GeocodingError as exc:
        return JsonResponse({"error": str(exc)}, status=422)
    return JsonResponse({"lat": lat, "lng": lng})


@require_POST
def reverse_geocode_view(request):
    try:
        lat = float(request.POST.get("lat", ""))
        lng = float(request.POST.get("lng", ""))
    except ValueError:
        return JsonResponse({"error": "緯度・経度が不正です。"}, status=400)
    try:
        address = reverse_geocode(lat, lng)
    except GeocodingError as exc:
        return JsonResponse({"error": str(exc)}, status=422)
    return JsonResponse({"address": address})
