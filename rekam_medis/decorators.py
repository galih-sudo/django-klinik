from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def role_required(allowed_roles=[]):
    """
    Decorator untuk membatasi akses berdasarkan role.
    Contoh penggunaan:
    @role_required(['dokter'])
    def my_view(request):
        ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Cek apakah user sudah login
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Cek apakah user punya profile
            if hasattr(request.user, 'profile'):
                role = request.user.profile.role
                if role in allowed_roles:
                    return view_func(request, *args, **kwargs)
            
            # Kalau tidak punya akses
            messages.error(request, 'Anda tidak memiliki akses ke halaman ini!')
            return redirect('dashboard')
        return wrapper
    return decorator


def dokter_required(view_func):
    """
    Decorator khusus untuk akses dokter saja.
    """
    return role_required(['dokter'])(view_func)


def staf_required(view_func):
    """
    Decorator untuk akses staf dan dokter.
    """
    return role_required(['staf', 'dokter'])(view_func)


def admin_required(view_func):
    """
    Decorator untuk akses admin saja.
    (Bisa digunakan nanti kalau mau tambah role admin)
    """
    return role_required(['admin'])(view_func)
