from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from report import views
from report.forms import LoginForm

urlpatterns = [
    path("admin/", admin.site.urls),
    path("captcha/", include("captcha.urls")),
    path("", auth_views.LoginView.as_view(
        template_name="report/login.html",
        authentication_form=LoginForm,
        redirect_authenticated_user=True), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="login"), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    # Sales
    path("kunjungan/", views.kunjungan_list, name="kunjungan_list"),
    path("kunjungan/baru/", views.kunjungan_baru, name="kunjungan_baru"),
    path("kunjungan/<int:pk>/edit/", views.kunjungan_edit, name="kunjungan_edit"),
    path("kunjungan/<int:pk>/", views.kunjungan_detail, name="kunjungan_detail"),
    path("api/cek-instansi/", views.cek_instansi, name="cek_instansi"),
    # Blast WA
    path("blast-wa/", views.blast_wa, name="blast_wa"),
    path("blast-wa/<int:pk>/<str:tahap>/", views.klik_wa, name="klik_wa"),
    # Export
    path("export/excel/", views.export_excel, name="export_excel"),
]
