from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from .models import Pasien, Obat, Kunjungan, RekamMedis, ICD10, Profile
from .forms import PasienForm, RekamMedisForm
from .decorators import dokter_required, staf_required
from django.db import models

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

# ========== PASIEN (Staf & Dokter bisa) ==========
@login_required
@staf_required
def daftar_pasien(request):
    pasien_list = Pasien.objects.filter(aktif=True).order_by('-id')
    context = {'pasien_list': pasien_list}
    return render(request, 'rekam_medis/daftar_pasien.html', context)

@login_required
@staf_required
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
@staf_required
def cari_pasien(request):
    keyword = request.GET.get('q', '').strip()
    jenis_kelamin = request.GET.get('jenis_kelamin', '')
    tgl_awal = request.GET.get('tgl_awal', '')
    tgl_akhir = request.GET.get('tgl_akhir', '')
    status_aktif = request.GET.get('status_aktif', '')

    pasien_list = Pasien.objects.all()

    # Filter berdasarkan keyword
    if keyword:
        pasien_list = pasien_list.filter(
            models.Q(nama__icontains=keyword) |
            models.Q(no_rm__icontains=keyword) |
            models.Q(alamat__icontains=keyword)
        )

    # Filter jenis kelamin
    if jenis_kelamin:
        pasien_list = pasien_list.filter(jenis_kelamin=jenis_kelamin)

    # Filter tanggal lahir
    if tgl_awal:
        pasien_list = pasien_list.filter(tgl_lahir__gte=tgl_awal)
    if tgl_akhir:
        pasien_list = pasien_list.filter(tgl_lahir__lte=tgl_akhir)

    # Filter status aktif
    if status_aktif == 'aktif':
        pasien_list = pasien_list.filter(aktif=True)
    elif status_aktif == 'tidak_aktif':
        pasien_list = pasien_list.filter(aktif=False)

    context = {
        'pasien_list': pasien_list,
        'keyword': keyword,
        'jenis_kelamin': jenis_kelamin,
        'tgl_awal': tgl_awal,
        'tgl_akhir': tgl_akhir,
        'status_aktif': status_aktif,
        'total': pasien_list.count(),
    }
    return render(request, 'rekam_medis/cari_pasien.html', context)

# ========== DOKTER ONLY ==========
@login_required
@dokter_required
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

@login_required
@dokter_required
def rekam_medis(request, pasien_id):
    pasien = get_object_or_404(Pasien, id=pasien_id)
    icd_list = ICD10.objects.all().order_by('kode')

    if request.method == 'POST':
        form = RekamMedisForm(request.POST)
        if form.is_valid():
            rekam = form.save(commit=False)
            rekam.pasien = pasien
            rekam.save()

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
@dokter_required
def buat_resep(request, rekam_medis_id):
    rekam = get_object_or_404(RekamMedis, id=rekam_medis_id)
    obat_list = Obat.objects.all().order_by('nama')

    if request.method == 'POST':
        obat_id = request.POST.get('obat_id')
        jumlah = int(request.POST.get('jumlah', 0))
        aturan = request.POST.get('aturan', '')

        obat = get_object_or_404(Obat, id=obat_id)

        if obat.stok >= jumlah:
            obat.stok -= jumlah
            obat.save()

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

# ========== OBAT ==========
@login_required
@dokter_required
def kelola_obat(request):
    obat_list = Obat.objects.all().order_by('nama')
    return render(request, 'rekam_medis/kelola_obat.html', {'obat_list': obat_list})

@login_required
@dokter_required
def tambah_obat(request):
    if request.method == 'POST':
        nama = request.POST.get('nama')
        stok = int(request.POST.get('stok', 0))
        satuan = request.POST.get('satuan', 'tablet')

        Obat.objects.create(nama=nama, stok=stok, satuan=satuan)
        return redirect('kelola_obat')

    return render(request, 'rekam_medis/tambah_obat.html')

@login_required
@dokter_required
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
@dokter_required
def hapus_obat(request, obat_id):
    obat = get_object_or_404(Obat, id=obat_id)
    obat.delete()
    return redirect('kelola_obat')

# ========== ICD-10 ==========
@login_required
@dokter_required
def kelola_icd10(request):
    icd_list = ICD10.objects.all().order_by('kode')

    if request.method == 'POST':
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
@dokter_required
def tambah_icd10(request):
    if request.method == 'POST':
        kode = request.POST.get('kode')
        nama_penyakit = request.POST.get('nama_penyakit')
        kategori = request.POST.get('kategori', '')

        if kode and nama_penyakit:
            if ICD10.objects.filter(kode=kode).exists():
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
@dokter_required
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
@dokter_required
def hapus_icd10(request, kode):
    icd = get_object_or_404(ICD10, kode=kode)
    icd.delete()
    return redirect('kelola_icd10')

# ========== MANAJEMEN USER ==========
@login_required
@dokter_required
def kelola_user(request):
    users = User.objects.all().select_related('profile')
    return render(request, 'rekam_medis/kelola_user.html', {'users': users})

@login_required
@dokter_required
def tambah_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '')
        role = request.POST.get('role')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah ada!')
            return redirect('tambah_user')

        user = User.objects.create_user(username=username, password=password, email=email)
        Profile.objects.create(user=user, role=role)

        messages.success(request, f'User {username} berhasil dibuat!')
        return redirect('kelola_user')

    return render(request, 'rekam_medis/tambah_user.html')

@login_required
@dokter_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    profile = user.profile

    if request.method == 'POST':
        user.email = request.POST.get('email', user.email)
        profile.role = request.POST.get('role', profile.role)
        profile.no_izin = request.POST.get('no_izin', profile.no_izin)
        profile.telepon = request.POST.get('telepon', profile.telepon)
        profile.alamat = request.POST.get('alamat', profile.alamat)

        user.save()
        profile.save()

        messages.success(request, f'User {user.username} berhasil diupdate!')
        return redirect('kelola_user')

    return render(request, 'rekam_medis/edit_user.html', {'user': user, 'profile': profile})

@login_required
@dokter_required
def hapus_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'Tidak bisa menghapus akun sendiri!')
        return redirect('kelola_user')

    user.delete()
    messages.success(request, 'User berhasil dihapus!')
    return redirect('kelola_user')