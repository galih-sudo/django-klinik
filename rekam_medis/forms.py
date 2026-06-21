from django import forms
from .models import Pasien, RekamMedis

class PasienForm(forms.ModelForm):
    class Meta:
        model = Pasien
        fields = ['nama', 'tgl_lahir', 'alamat', 'no_telp', 'jenis_kelamin', 'pekerjaan', 'alergi', 'riwayat_penyakit']
        widgets = {
            'tgl_lahir': forms.DateInput(attrs={'type': 'date'}),
            'alamat': forms.Textarea(attrs={'rows': 3}),
            'alergi': forms.Textarea(attrs={'rows': 2}),
            'riwayat_penyakit': forms.Textarea(attrs={'rows': 2}),
        }

class RekamMedisForm(forms.ModelForm):
    class Meta:
        model = RekamMedis
        fields = ['subjective', 'objective', 'assessment', 'planning', 'icd10', 'lampiran_mega']
        widgets = {
            'subjective': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Keluhan pasien'}),
            'objective': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Hasil pemeriksaan'}),
            'planning': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tatalaksana'}),
            'lampiran_mega': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }