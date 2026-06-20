from django import forms
from .models import Pasien

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
