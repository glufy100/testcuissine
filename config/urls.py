from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth
from blog.access import admin_required, AdminLoginForm
from django.urls import path
from django.urls import reverse_lazy
from blog import views
urlpatterns = [
    path('', views.home, name='home'),
    path('article/<slug:slug>/', views.detail, name='detail'),
    path('connexion/', auth.LoginView.as_view(template_name='registration/login.html', authentication_form=AdminLoginForm), name='login'),
    path('deconnexion/', auth.LogoutView.as_view(), name='logout'),
    path('admin/', views.dashboard, name='dashboard'),
    path('admin/mot-de-passe/', admin_required(auth.PasswordChangeView.as_view(template_name='registration/password_change.html', success_url=reverse_lazy('password_changed'))), name='password_change'),
    path('admin/mot-de-passe/modifie/', admin_required(auth.PasswordChangeDoneView.as_view(template_name='registration/password_changed.html')), name='password_changed'),
    path('admin/nouveau/', views.edit, name='create'),
    path('admin/article/<int:pk>/', views.edit, name='edit'),
    path('admin/article/<int:pk>/supprimer/', views.delete, name='delete'),
    path('gestion-django/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
