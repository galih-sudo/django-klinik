from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('dokter', 'Dokter'),
        ('staf', 'Staf'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staf')
    no_izin = models.CharField(max_length=50, blank=True, null=True)
    telepon = models.CharField(max_length=20, blank=True)
    alamat = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

    def is_dokter(self):
        return self.role == 'dokter'

    def is_staf(self):
        return self.role == 'staf'

class Pasien(models.Model):
    JENIS_KELAMIN = [
        ('L', 'Laki-laki'),
        ('P', 'Perempuan'),
    ]

    no_rm = models.CharField(max_length=20, unique=True, blank=True)
    nama = models.CharField(max_length=200)
    tgl_lahir = models.DateField(null=True, blank=True)
    alamat = models.TextField(blank=True)
    no_telp = models.CharField(max_length=20, blank=True)
    jenis_kelamin = models.CharField(max_length=1, choices=JENIS_KELAMIN, blank=True)
    pekerjaan = models.CharField(max_length=100, blank=True)
    alergi = models.TextField(blank=True)
    riwayat_penyakit = models.TextField(blank=True)
    aktif = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.no_rm} - {self.nama}"

    def umur(self):
        if self.tgl_lahir:
            today = timezone.now().date()
            return today.year - self.tgl_lahir.year - ((today.month, today.day) < (self.tgl_lahir.month, self.tgl_lahir.day))
        return None

class ICD10(models.Model):
    kode = models.CharField(max_length=10, primary_key=True)
    nama_penyakit = models.CharField(max_length=255)
    kategori = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.kode} - {self.nama_penyakit}"

class RekamMedis(models.Model):
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE, related_name='rekam_medis')
    tanggal = models.DateTimeField(auto_now_add=True)
    subjective = models.TextField()
    objective = models.TextField(blank=True)
    assessment = models.CharField(max_length=255, blank=True)
    planning = models.TextField(blank=True)
    icd10 = models.ForeignKey(ICD10, on_delete=models.SET_NULL, null=True, blank=True)
    lampiran_mega = models.URLField(blank=True)
    file_lampiran = models.FileField(upload_to='lampiran/', blank=True, null=True)

    def __str__(self):
        return f"RM {self.pasien.no_rm} - {self.tanggal.strftime('%d-%m-%Y %H:%M')}"

class Obat(models.Model):
    nama = models.CharField(max_length=200, unique=True)
    stok = models.IntegerField(default=0)
    satuan = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.nama} ({self.stok} {self.satuan})"

class Resep(models.Model):
    rekam_medis = models.ForeignKey(RekamMedis, on_delete=models.CASCADE, related_name='resep')
    obat = models.ForeignKey(Obat, on_delete=models.CASCADE)
    jumlah = models.IntegerField()
    aturan = models.TextField()

    def __str__(self):
        return f"Resep {self.rekam_medis.id} - {self.obat.nama}"

class Kunjungan(models.Model):
    rekam_medis = models.ForeignKey(RekamMedis, on_delete=models.CASCADE)
    tanggal = models.DateField(auto_now_add=True)

class LogCetakSurat(models.Model):
    pasien = models.ForeignKey(Pasien, on_delete=models.CASCADE)
    jenis_surat = models.CharField(max_length=50)
    tanggal_cetak = models.DateTimeField(auto_now_add=True)
    dicetak_oleh = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.jenis_surat} - {self.pasien.nama} ({self.tanggal_cetak.strftime('%d-%m-%Y %H:%M')})"
