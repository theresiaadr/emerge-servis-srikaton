# Web Report Sales Srikaton (Phase 1)

Sistem laporan kunjungan sales — Django 6. Dibangun sesuai PRD final v4
+ hasil review (AI-1 s/d AI-7).

## Fitur (sudah jadi & teruji)
- Login username, 4 role (Superuser/Admin-SPV/Sales/Teknisi-Phase2)
- Address book instansi (shared) + notif "sudah dikunjungi sales lain"
- Laporan kunjungan (1 record = 1 kunjungan), privat per sales
- Blast WA: 3 link (H0/H2/H5), template otomatis, klik=auto-update status (via POST)
- Notifikasi lonceng global (badge di topbar) untuk reminder H+2/H+5
- Dashboard SPV: rekap + filter + drill-down detail + export Excel
- Detail kunjungan dengan timeline follow-up WA

## Keamanan (PRD section 12 + review)
- DEBUG=0 default, HTTPS-ready, security headers, HSTS
- Cookie Secure + HttpOnly, session idle 2 jam
- **django-axes** (anti brute-force, limit 5x)
- **Field terenkripsi** (Fernet): `catatan` & `no_wa` di Kunjungan, `no_wa` di Instansi
- Anti-dobel instansi (unique case-insensitive di DB)
- Sentry-ready
- Validasi format nomor WA

## CATATAN: captcha login
django-axes sudah menutup proteksi brute-force. Kalau ingin tambah CAPTCHA
(seperti servis-srikaton), install `django-simple-captcha` + `Pillow` saat
deploy, lalu tambahkan field captcha di form login. Belum dipasang di scaffold
ini karena butuh dependency gambar tambahan.

## Setup Lokal (dev)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env    # set DJANGO_DEBUG=1 untuk dev
# WAJIB generate encryption key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# masukkan hasilnya ke DJANGO_FIELD_ENCRYPTION_KEY di .env
python manage.py migrate
python manage.py buat_akun
python manage.py createsuperuser
python manage.py runserver
```

## WAJIB sebelum produksi
1. Ganti password placeholder `GANTI_*` di `buat_akun.py` + isi `no_hp` sales asli
2. Generate `DJANGO_SECRET_KEY` DAN `DJANGO_FIELD_ENCRYPTION_KEY` baru
   (encryption key WAJIB — kalau hilang, data terenkripsi tidak bisa dibaca!)
3. `DJANGO_DEBUG=0`, pakai PostgreSQL

## Akun bawaan
| Username | Role |
|---|---|
| Devy, Mia | Admin/SPV (lihat + export) |
| Utoro, Maryadi | Sales (input & edit sendiri) |

Teknisi (Agie) = Phase 2.

## Deploy ke VPS
Pola sama servis-srikaton (Nginx + Gunicorn), subdomain report.srikaton.id.
Panduan lengkap saat tahap deploy.
