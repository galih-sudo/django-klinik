from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Pasien, Obat, Kunjungan, RekamMedis, ICD10
from .forms import PasienForm, RekamMedisForm

@login_required
def dashboard(request):
    today = timezone.now().date()
    total_pasien = Pasien.objects.filter(aktif=True).count()
    total_obat = Obat.objects.count()
    total_kunjungan = Kunjungan.objects.filter(tanggal=today).count()
    pasien_terbaru = Pasien.objects.filter(aktif=True).order_by('-id')[:10]

    context = {
        'today': today.strftime('%Y-%m-%d'),
        'total_pasien': total_pasien,
        'total_obat': total_obat,
        'total_kunjungan': total_kunjungan,
        'pasien_terbaru': pasien_terbaru,
    }
    return render(request, 'rekam_medis/dashboard.html', context)

@login_required
def tambah_pasien(request):
    if request.method == 'POST':
        form = PasienForm(request.POST)
        if form.is_valid():
            pasien = form.save(commit=False)
            tahun = timezone.now().strftime('%y')
            count = Pasien.objects.count() + 1
            pasien.no_rm = f"{tahun}-{count:04d}"
            pasien.save()
            return redirect('dashboard')
    else:
        form = PasienForm()
    return render(request, 'rekam_medis/tambah_pasien.html', {'form': form})

@login_required
def daftar_pasien(request):
    pasien_list = Pasien.objects.filter(aktif=True).order_by('-id')
    context = {'pasien_list': pasien_list}
    return render(request, 'rekam_medis/daftar_pasien.html', context)

@login_required
def edit_pasien(request, pasien_id):
    pasien = get_object_or_404(Pasien, id=pasien_id)

    if request.method == 'POST':
        form = PasienForm(request.POST, instance=pasien)
        if form.is_valid():
            form.save()
            return redirect('daftar_pasien')
    else:
        form = PasienForm(instance=pasien)

    return render(request, 'rekam_medis/edit_pasien.html', {'form': form, 'pasien': pasien})

# ========== REKAM MEDIS SOAP ==========
@login_required
def rekam_medis(request, pasien_id):
    pasien = get_object_or_404(Pasien, id=pasien_id)
    icd_list = ICD10.objects.all().order_by('kode')

    if request.method == 'POST':
        form = RekamMedisForm(request.POST)
        if form.is_valid():
            rekam = form.save(commit=False)
            rekam.pasien = pasien
            rekam.save()

            # Catat kunjungan
            Kunjungan.objects.create(
                rekam_medis=rekam,
                tanggal=timezone.now().date()
            )
            return redirect('daftar_pasien')
    else:
        form = RekamMedisForm()

    context = {
        'form': form,
        'pasien': pasien,
        'icd_list': icd_list,
    }
    return render(request, 'rekam_medis/rekam_medis.html', context)

@login_required
def cari_pasien(request):
    keyword = request.GET.get('q', '')
    pasien_list = []
    if keyword:
        pasien_list = Pasien.objects.filter(nama__icontains=keyword)[:20]
    return render(request, 'rekam_medis/cari_pasien.html', {'pasien_list': pasien_list, 'keyword': keyword})

@login_required
def buat_resep(request, rekam_medis_id):
    rekam = get_object_or_404(RekamMedis, id=rekam_medis_id)
    obat_list = Obat.objects.all().order_by('nama')

    if request.method == 'POST':
        obat_id = request.POST.get('obat_id')
        jumlah = int(request.POST.get('jumlah', 0))
        aturan = request.POST.get('aturan', '')

        obat = get_object_or_404(Obat, id=obat_id)

        # Cek stok
        if obat.stok >= jumlah:
            # Kurangi stok
            obat.stok -= jumlah
            obat.save()

            # Buat resep
            Resep.objects.create(
                rekam_medis=rekam,
                obat=obat,
                jumlah=jumlah,
                aturan=aturan
            )
            return redirect('daftar_pasien')
        else:
            return render(request, 'rekam_medis/error_stok.html', {'obat': obat})

    context = {
        'rekam': rekam,
        'obat_list': obat_list,
    }
    return render(request, 'rekam_medis/buat_resep.html', context)

# ========== STOK OBAT ==========
@login_required
def kelola_obat(request):
    obat_list = Obat.objects.all().order_by('nama')
    return render(request, 'rekam_medis/kelola_obat.html', {'obat_list': obat_list})

@login_required
def tambah_obat(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        stok = int(request.POST.get('stok', 0))
        satuan = request.POST.get('satuan', 'tablet')

        Obat.objects.create(nama=nama, stok=stok, satuan=satuan)
        return redirect('kelola_obat')

    return render(request, 'rekam_medis/tambah_obat.html')

@login_required
def edit_obat(request, obat_id):
    obat = get_object_or_404(Obat, id=obat_id)

    if request.method == 'POST':
        obat.nama = request.POST.get('nama', obat.nama)
        obat.stok = int(request.POST.get('stok', obat.stok))
        obat.satuan = request.POST.get('satuan', obat.satuan)
        obat.save()
        return redirect('kelola_obat')

    return render(request, 'rekam_medis/edit_obat.html', {'obat': obat})

@login_required
def hapus_obat(request, obat_id):
    obat = get_object_or_404(Obat, id=obat_id)
    obat.delete()
    return redirect('kelola_obat')

@login_required
def kelola_icd10(request):
    icd_list = ICD10.objects.all().order_by('kode')

    if request.method == 'POST':
        # Tambah ICD10 baru
        kode = request.POST.get('kode')
        nama = request.POST.get('nama_penyakit')
        kategori = request.POST.get('kategori', '')

        if kode and nama:
            ICD10.objects.create(
                kode=kode,
                nama_penyakit=nama,
                kategori=kategori
            )
            return redirect('kelola_icd10')

        # Hapus ICD10
        hapus_id = request.POST.get('hapus_id')
        if hapus_id:
            icd = get_object_or_404(ICD10, kode=hapus_id)
            icd.delete()
            return redirect('kelola_icd10')

    context = {
        'icd_list': icd_list,
    }
    return render(request, 'rekam_medis/kelola_icd10.html', context)

@login_required
def tambah_icd10(request):
    if request.method == 'POST':
        kode = request.POST.get('kode')
        nama_penyakit = request.POST.get('nama_penyakit')
        kategori = request.POST.get('kategori', '')

        if kode and nama_penyakit:
            # Cek apakah kode sudah ada
            if ICD10.objects.filter(kode=kode).exists():
                # Kalo udah ada, kasih pesan error (opsional)
                pass
            else:
                ICD10.objects.create(
                    kode=kode,
                    nama_penyakit=nama_penyakit,
                    kategori=kategori
                )
            return redirect('kelola_icd10')

    return render(request, 'rekam_medis/tambah_icd10.html')

@login_required
def edit_icd10(request, kode):
    icd = get_object_or_404(ICD10, kode=kode)

    if request.method == 'POST':
        icd.nama_penyakit = request.POST.get('nama_penyakit', icd.nama_penyakit)
        icd.kategori = request.POST.get('kategori', icd.kategori)
        icd.save()
        return redirect('kelola_icd10')

    context = {
        'icd': icd,
    }
    return render(request, 'rekam_medis/edit_icd10.html', context)

@login_required
def hapus_icd10(request, kode):
    icd = get_object_or_404(ICD10, kode=kode)
    icd.delete()
    return redirect('kelola_icd10')