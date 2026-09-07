from django.contrib import admin
from django.urls import path
from report import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
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
