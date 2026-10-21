from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("shop/",views.product_list, name="product_list"),
    path("products/<slug:slug>/", views.product_detail, name="product_detail"),
    path("contact/", views.contact, name="contact"),
    path("policies/<slug:page>/", views.policy, name="policy"),
    path("our-story/", views.about, name="about"),
]