from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Pasien, Obat, Kunjungan
from .forms import PasienForm
from django.utils import timezone

def dashboard(request):
    total_pasien = Pasien.objects.filter(aktif=True).count()
    total_obat = Obat.objects.count()
    today = timezone.now().date()
    total_kunjungan = Kunjungan.objects.filter(tanggal=today).count()

    context = {
        'total_pasien': total_pasien,
        'total_kunjungan': total_kunjungan,
        'total_obat': total_obat,
    }
    return render(request, 'rekam_medis/dashboard.html', context)

@login_required
def tambah_pasien(request):
    if request.method == 'POST':
        form = PasienForm(request.POST)
        if form.is_valid():
            pasien = form.save(commit=False)
            # Generate No RM otomatis
            tahun = timezone.now().strftime('%y')
            count = Pasien.objects.count() + 1
            pasien.no_rm = f"{tahun}-{count:04d}"
            pasien.save()
            return redirect('dashboard')
    else:
        form = PasienForm()

    return render(request, 'rekam_medis/tambah_pasien.html', {'form': form})