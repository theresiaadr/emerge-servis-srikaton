"""Test regresi dasar — pola: 1 fitur = 1 test."""
from django.test import TestCase, Client
from django.urls import reverse
from .models import User, Instansi, Kunjungan, FollowUpWA


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
        c.post("/", {"username": u, "password": "pass12345"})

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
