from django.urls import path
from .views import UserAPI, AddressAPI

urlpatterns = [
    path("user/", UserAPI.as_view()),
    path("address/<str:id>/", AddressAPI.as_view(), name="address_id"),
    path("address/", AddressAPI.as_view(), name="address"),
]
