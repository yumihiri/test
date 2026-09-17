from django.urls import path

from . import views

app_name = "spots"

urlpatterns = [
    path("", views.MapView.as_view(), name="map"),
    path("spots/new/", views.SpotCreateView.as_view(), name="register"),
    path("spots/mine/", views.MyPageView.as_view(), name="mypage"),
    path("spots/geocode/", views.geocode_view, name="geocode"),
    path("spots/reverse-geocode/", views.reverse_geocode_view, name="reverse_geocode"),
    path("spots/<int:pk>/", views.SpotDetailView.as_view(), name="detail"),
]
