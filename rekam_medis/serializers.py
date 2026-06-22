from rest_framework import serializers
from .models import Pasien, RekamMedis, Obat, ICD10

class PasienSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pasien
        fields = ['id', 'no_rm', 'nama', 'jenis_kelamin', 'tgl_lahir', 'alamat', 'no_telp', 'aktif']

class RekamMedisSerializer(serializers.ModelSerializer):
    pasien_nama = serializers.CharField(source='pasien.nama', read_only=True)
    pasien_no_rm = serializers.CharField(source='pasien.no_rm', read_only=True)
    
    class Meta:
        model = RekamMedis
        fields = ['id', 'pasien', 'pasien_nama', 'pasien_no_rm', 'tanggal', 'subjective', 'objective', 'assessment', 'planning']

class ObatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Obat
        fields = ['id', 'nama', 'stok', 'satuan']

class ICD10Serializer(serializers.ModelSerializer):
    class Meta:
        model = ICD10
        fields = ['kode', 'nama_penyakit', 'kategori']
