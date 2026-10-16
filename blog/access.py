from functools import wraps
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied, ValidationError


def is_admin(user):
    return user.is_authenticated and user.is_active and user.is_staff and user.is_superuser


def admin_required(view):
    @wraps(view)
    def protected(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url='login')
        if not is_admin(request.user):
            raise PermissionDenied('Cet espace est réservé aux administrateurs.')
        return view(request, *args, **kwargs)
    return protected


class AdminLoginForm(AuthenticationForm):
    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not is_admin(user):
            raise ValidationError('Ce compte ne possède pas les droits d’administration.', code='not_admin')
