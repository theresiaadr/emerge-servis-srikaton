"""Buat akun bawaan: python manage.py buat_akun

Password default tiap akun bisa dioverride lewat env var
BUAT_AKUN_PASSWORD_<USERNAME_UPPER> (mis. BUAT_AKUN_PASSWORD_CLYDE),
atau fallback global lewat --password (semua akun pakai 1 password
yang sama, hanya untuk seed pertama di lokal/staging).
"""
import os
from django.core.management.base import BaseCommand
from report.models import User

AKUN = [
    dict(username="Clyde", password="GANTI_clyde_2026", role=User.Role.SUPERUSER,
         first_name="Clyde", is_superuser=True, is_staff=True),
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
    help = "Membuat akun bawaan (1 superuser + 2 admin + 2 sales) jika belum ada"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password", default=None,
            help="Override password untuk SEMUA akun yang baru dibuat "
                 "(kalau tidak diisi, pakai env BUAT_AKUN_PASSWORD_<USERNAME> "
                 "lalu fallback ke placeholder GANTI_*).",
        )

    def handle(self, *args, **opts):
        password_override = opts.get("password")
        for a in AKUN:
            a = dict(a)
            username = a["username"]
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"- {username}: sudah ada, dilewati")
                continue
            env_key = f"BUAT_AKUN_PASSWORD_{username.upper()}"
            a["password"] = (
                password_override or os.environ.get(env_key) or a["password"]
            )
            User.objects.create_user(**a)
            self.stdout.write(self.style.SUCCESS(
                f"+ {username} ({a['role']})"))
        self.stdout.write(
            "Selesai. WAJIB ganti password tiap akun (nilai GANTI_* di atas "
            "cuma placeholder) — pakai --password, env BUAT_AKUN_PASSWORD_<USER>, "
            "atau ganti manual via /admin/.")
