from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('pasien/', views.daftar_pasien, name='daftar_pasien'),
    path('pasien/tambah/', views.tambah_pasien, name='tambah_pasien'),
    path('pasien/rekam/<int:pasien_id>/', views.rekam_medis, name='rekam_medis'),
    path('pasien/edit/<int:pasien_id>/', views.edit_pasien, name='edit_pasien'),
    path('pasien/cari/', views.cari_pasien, name='cari_pasien'),
    path('resep/<int:rekam_medis_id>/', views.buat_resep, name='buat_resep'),
    path('obat/', views.kelola_obat, name='kelola_obat'),
    path('obat/tambah/', views.tambah_obat, name='tambah_obat'),
    path('obat/edit/<int:obat_id>/', views.edit_obat, name='edit_obat'),
    path('obat/hapus/<int:obat_id>/', views.hapus_obat, name='hapus_obat'),
    path('icd10/', views.kelola_icd10, name='kelola_icd10'),
    path('icd10/tambah/', views.tambah_icd10, name='tambah_icd10'),
    path('icd10/edit/<str:kode>/', views.edit_icd10, name='edit_icd10'),
    path('icd10/hapus/<str:kode>/', views.hapus_icd10, name='hapus_icd10'),
]

