from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Pasien, RekamMedis, Obat, ICD10
from .serializers import PasienSerializer, RekamMedisSerializer, ObatSerializer, ICD10Serializer

# ========== PASIEN API ==========
@api_view(['GET'])
def api_pasien_list(request):
    pasien = Pasien.objects.all().order_by('-id')
    serializer = PasienSerializer(pasien, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_pasien_detail(request, pk):
    try:
        pasien = Pasien.objects.get(pk=pk)
    except Pasien.DoesNotExist:
        return Response({'error': 'Pasien tidak ditemukan'}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = PasienSerializer(pasien)
    return Response(serializer.data)

@api_view(['POST'])
def api_pasien_create(request):
    serializer = PasienSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========== REKAM MEDIS API ==========
@api_view(['GET'])
def api_rekam_list(request):
    rekam = RekamMedis.objects.all().order_by('-tanggal')
    serializer = RekamMedisSerializer(rekam, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_rekam_pasien(request, pasien_id):
    rekam = RekamMedis.objects.filter(pasien_id=pasien_id).order_by('-tanggal')
    serializer = RekamMedisSerializer(rekam, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def api_rekam_create(request):
    serializer = RekamMedisSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ========== OBAT API ==========
@api_view(['GET'])
def api_obat_list(request):
    obat = Obat.objects.all().order_by('nama')
    serializer = ObatSerializer(obat, many=True)
    return Response(serializer.data)

# ========== ICD10 API ==========
@api_view(['GET'])
def api_icd10_list(request):
    icd = ICD10.objects.all().order_by('kode')
    serializer = ICD10Serializer(icd, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def api_icd10_search(request, keyword):
    icd = ICD10.objects.filter(nama_penyakit__icontains=keyword) | ICD10.objects.filter(kode__icontains=keyword)
    serializer = ICD10Serializer(icd, many=True)
    return Response(serializer.data)
