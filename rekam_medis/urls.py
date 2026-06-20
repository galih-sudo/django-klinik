from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pasien/tambah/', views.tambah_pasien, name='tambah_pasien'),
]