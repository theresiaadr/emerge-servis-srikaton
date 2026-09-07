"""Test regresi dasar — pola: 1 fitur = 1 test."""
from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Instansi, Kunjungan, FollowUpWA

# django-simple-captcha membaca CAPTCHA_TEST_MODE sekali saat modulnya
# di-import (captcha/conf/settings.py), BUKAN lewat django.conf.settings
# secara dinamis — jadi @override_settings tidak berpengaruh di sini.
# Harus di-patch langsung ke atribut modulnya.
from captcha.conf import settings as captcha_settings
captcha_settings.CAPTCHA_TEST_MODE = True


class ReportTest(TestCase):
    def setUp(self):
        self.sales = User.objects.create_user(
            username="sales1", password="pass12345", role=User.Role.SALES,
            first_name="Sales Satu", no_hp="628111")
        self.sales2 = User.objects.create_user(
            username="sales2", password="pass12345", role=User.Role.SALES)
        self.spv = User.objects.create_user(
            username="spv1", password="pass12345", role=User.Role.ADMIN)

    def _login(self, c, u):
        # CAPTCHA_TEST_MODE=True: captcha_1="PASSED" selalu valid, apapun captcha_0.
        c.post("/", {
            "username": u, "password": "pass12345",
            "captcha_0": "dummy", "captcha_1": "PASSED",
        })

    def test_input_kunjungan_bikin_instansi(self):
        c = Client(); self._login(c, "sales1")
        c.post("/kunjungan/baru/", {
            "nama_instansi": "PT Test", "tanggal": "2026-09-07",
            "pic": "A", "no_wa": "08123456789", "status": "BARU"})
        self.assertEqual(Instansi.objects.count(), 1)
        self.assertEqual(Kunjungan.objects.count(), 1)
        self.assertEqual(FollowUpWA.objects.count(), 1)

    def test_enkripsi_field(self):
        from django.db import connection
        c = Client(); self._login(c, "sales1")
        c.post("/kunjungan/baru/", {
            "nama_instansi": "PT Enkrip", "tanggal": "2026-09-07",
            "no_wa": "08123456789", "status": "BARU", "catatan": "rahasia"})
        k = Kunjungan.objects.first()
        with connection.cursor() as cur:
            cur.execute("SELECT catatan FROM report_kunjungan WHERE id=%s", [k.pk])
            raw = cur.fetchone()[0]
        self.assertNotIn("rahasia", raw)
        self.assertEqual(k.catatan, "rahasia")

    def test_klik_wa_harus_post(self):
        c = Client(); self._login(c, "sales1")
        c.post("/kunjungan/baru/", {
            "nama_instansi": "PT WA", "tanggal": "2026-09-07",
            "no_wa": "08123456789", "status": "BARU"})
        k = Kunjungan.objects.first()
        c.post(f"/blast-wa/{k.pk}/H2/")
        self.assertEqual(FollowUpWA.objects.get(kunjungan=k).tahap, "FOLLOW_UP")

    def test_sales_lain_tidak_bisa_lihat(self):
        c = Client(); self._login(c, "sales1")
        c.post("/kunjungan/baru/", {
            "nama_instansi": "PT Privat", "tanggal": "2026-09-07",
            "no_wa": "08123456789", "status": "BARU"})
        k = Kunjungan.objects.first()
        c2 = Client(); self._login(c2, "sales2")
        self.assertEqual(c2.get(f"/kunjungan/{k.pk}/").status_code, 403)

    def test_spv_export_excel(self):
        c = Client(); self._login(c, "spv1")
        self.assertEqual(c.get("/export/excel/").status_code, 200)

    def test_sales_tidak_bisa_export(self):
        c = Client(); self._login(c, "sales1")
        self.assertEqual(c.get("/export/excel/").status_code, 403)

    def test_instansi_unik_case_insensitive(self):
        c = Client(); self._login(c, "sales1")
        c.post("/kunjungan/baru/", {
            "nama_instansi": "SMKN 1", "tanggal": "2026-09-01",
            "no_wa": "08123456789", "status": "BARU"})
        c.post("/kunjungan/baru/", {
            "nama_instansi": "smkn 1", "tanggal": "2026-09-02",
            "no_wa": "08123456788", "status": "BARU"})
        # Dua nama beda kapital -> tetap 1 instansi (bukan duplikat), 2 kunjungan.
        self.assertEqual(Instansi.objects.count(), 1)
        self.assertEqual(Kunjungan.objects.count(), 2)

    def test_cek_instansi_notifikasi_sudah_dikunjungi(self):
        c = Client(); self._login(c, "sales1")
        c.post("/kunjungan/baru/", {
            "nama_instansi": "PT Notif", "tanggal": "2026-09-01",
            "pic": "Budi", "no_wa": "08123456789", "status": "BARU"})
        c2 = Client(); self._login(c2, "sales2")
        resp = c2.get("/api/cek-instansi/", {"nama": "pt notif"})
        data = resp.json()
        self.assertTrue(data["ada"])
        self.assertEqual(len(data["dikunjungi"]), 1)
        self.assertEqual(data["dikunjungi"][0]["sales"], "Sales Satu")

    def test_klik_wa_h5_jadi_progress(self):
        c = Client(); self._login(c, "sales1")
        c.post("/kunjungan/baru/", {
            "nama_instansi": "PT H5", "tanggal": "2026-09-01",
            "no_wa": "08123456789", "status": "BARU"})
        k = Kunjungan.objects.first()
        c.post(f"/blast-wa/{k.pk}/H5/")
        self.assertEqual(FollowUpWA.objects.get(kunjungan=k).tahap, "PROGRESS")

    def test_klik_wa_get_ditolak(self):
        c = Client(); self._login(c, "sales1")
        c.post("/kunjungan/baru/", {
            "nama_instansi": "PT GetWA", "tanggal": "2026-09-01",
            "no_wa": "08123456789", "status": "BARU"})
        k = Kunjungan.objects.first()
        c.get(f"/blast-wa/{k.pk}/H2/")
        # GET tidak boleh mengubah tahap, harus tetap NEW.
        self.assertEqual(FollowUpWA.objects.get(kunjungan=k).tahap, "NEW")

    def test_dashboard_spv_filter(self):
        c = Client(); self._login(c, "sales1")
        c.post("/kunjungan/baru/", {
            "nama_instansi": "PT Filter A", "tanggal": "2026-09-01",
            "no_wa": "08123456789", "status": "CLOSING"})
        c.post("/kunjungan/baru/", {
            "nama_instansi": "PT Filter B", "tanggal": "2026-08-01",
            "no_wa": "08123456788", "status": "BATAL"})
        c2 = Client(); self._login(c2, "spv1")
        resp = c2.get("/dashboard/", {"bulan": "2026-09", "status": "CLOSING"})
        self.assertEqual(resp.context["total"], 1)
