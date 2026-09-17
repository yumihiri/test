from django.urls import path

from . import views

app_name = "reviews"

urlpatterns = [
    path("spots/<int:spot_id>/review/", views.submit_review, name="submit"),
]
