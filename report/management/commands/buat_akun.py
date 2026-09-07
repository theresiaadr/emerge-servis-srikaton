"""Buat akun bawaan: python manage.py buat_akun"""
from django.core.management.base import BaseCommand
from report.models import User

AKUN = [
    dict(username="Devy", password="GANTI_devy_2026", role=User.Role.ADMIN,
         first_name="Devy"),
    dict(username="Mia", password="GANTI_mia_2026", role=User.Role.ADMIN,
         first_name="Mia"),
    dict(username="Utoro", password="GANTI_utoro_2026", role=User.Role.SALES,
         first_name="Utoro RW Adjie", no_hp="628xxxxxxxxxx"),
    dict(username="Maryadi", password="GANTI_maryadi_2026", role=User.Role.SALES,
         first_name="Maryadi", no_hp="628xxxxxxxxxx"),
]


class Command(BaseCommand):
    help = "Membuat akun bawaan (2 admin + 2 sales) jika belum ada"

    def handle(self, *args, **opts):
        for a in AKUN:
            if User.objects.filter(username=a["username"]).exists():
                self.stdout.write(f"- {a['username']}: sudah ada, dilewati")
                continue
            User.objects.create_user(**a)
            self.stdout.write(self.style.SUCCESS(
                f"+ {a['username']} ({a['role']})"))
        self.stdout.write(
            "Selesai. WAJIB ganti password tiap akun (nilai GANTI_* di atas "
            "cuma placeholder) — edit file ini atau ganti via /admin/.")
