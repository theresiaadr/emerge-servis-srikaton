from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Instansi, Kunjungan, FollowUpWA


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "first_name", "role", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("Info Srikaton", {"fields": ("role", "no_hp")}),
    )


@admin.register(Instansi)
class InstansiAdmin(admin.ModelAdmin):
    list_display = ("nama", "pic", "no_wa", "dibuat_oleh", "dibuat_pada")
    search_fields = ("nama", "pic")


@admin.register(Kunjungan)
class KunjunganAdmin(admin.ModelAdmin):
    list_display = ("tanggal", "sales", "instansi", "status")
    list_filter = ("status", "sales", "tanggal")
    search_fields = ("instansi__nama", "pic")


@admin.register(FollowUpWA)
class FollowUpWAAdmin(admin.ModelAdmin):
    list_display = ("kunjungan", "tahap", "h0_diklik", "h2_diklik", "h5_diklik")
