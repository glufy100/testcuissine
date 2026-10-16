from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth
from django.urls import path
from blog import views
urlpatterns = [
    path('', views.home, name='home'),
    path('article/<slug:slug>/', views.detail, name='detail'),
    path('connexion/', auth.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('deconnexion/', auth.LogoutView.as_view(), name='logout'),
    path('admin/', views.dashboard, name='dashboard'),
    path('admin/nouveau/', views.edit, name='create'),
    path('admin/article/<int:pk>/', views.edit, name='edit'),
    path('admin/article/<int:pk>/supprimer/', views.delete, name='delete'),
    path('gestion-django/', admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
