"""
Model data Web Report Sales Srikaton.
Mengikuti PRD section 5 (role) & section 6 (model data 2 lapis).
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# ---------------------------------------------------------------------------
# USER — 4 role (PRD section 5)
# ---------------------------------------------------------------------------
class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERUSER = "SUPERUSER", "Superuser"
        ADMIN = "ADMIN", "Admin/SPV"
        SALES = "SALES", "Sales"
        TEKNISI = "TEKNISI", "Teknisi"  # disiapkan untuk Phase 2

    role = models.CharField(
        max_length=15, choices=Role.choices, default=Role.SALES
    )
    no_hp = models.CharField(
        max_length=20, blank=True,
        help_text="Nomor HP sales (untuk tanda tangan pesan WA)"
    )

    @property
    def is_admin_spv(self):
        return self.role == self.Role.ADMIN

    @property
    def is_sales(self):
        return self.role == self.Role.SALES


# ---------------------------------------------------------------------------
# LAYER 1 — ADDRESS BOOK (SHARED) — PRD section 6
# ---------------------------------------------------------------------------
class Instansi(models.Model):
    """Buku alamat instansi, dipakai bersama semua sales."""
    nama = models.CharField(max_length=200, unique=True, db_index=True,
                            verbose_name="Nama Instansi")
    alamat = models.TextField(blank=True)
    pic = models.CharField(max_length=120, blank=True, verbose_name="PIC")
    no_wa = models.CharField(max_length=20, blank=True,
                             verbose_name="No. WA/Telp")
    dibuat_oleh = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="instansi_dibuat"
    )
    dibuat_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Instansi"
        ordering = ["nama"]

    def __str__(self):
        return self.nama

    @property
    def sudah_dikunjungi_oleh(self):
        """Daftar ringkas (sales, tanggal) kunjungan terakhir per sales."""
        hasil = []
        seen = set()
        for k in self.kunjungan_set.select_related("sales").order_by("-tanggal"):
            if k.sales_id in seen:
                continue
            seen.add(k.sales_id)
            hasil.append({
                "sales": k.sales.get_full_name() or k.sales.username,
                "tanggal": k.tanggal,
            })
        return hasil


# ---------------------------------------------------------------------------
# LAYER 2 — VISIT REPORT (PRIVATE) — PRD section 6 & 7.1
# ---------------------------------------------------------------------------
class Kunjungan(models.Model):
    """1 kunjungan = 1 record. Privat: hanya sales pembuat & SPV."""
    class Status(models.TextChoices):
        BARU = "BARU", "Baru"
        PEMBICARAAN = "PEMBICARAAN", "Pembicaraan"
        PENAWARAN = "PENAWARAN", "Penawaran"
        CLOSING = "CLOSING", "Closing"
        TIDAK_RESPON = "TIDAK_RESPON", "Tidak Respon"
        BATAL = "BATAL", "Batal"

    sales = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name="kunjungan_set")
    instansi = models.ForeignKey(Instansi, on_delete=models.CASCADE,
                                 related_name="kunjungan_set")
    tanggal = models.DateField(default=timezone.now, db_index=True)

    pic = models.CharField(max_length=120, blank=True, verbose_name="PIC")
    no_wa = models.CharField(max_length=20, blank=True,
                             verbose_name="No. WA/Telp")
    alamat = models.TextField(blank=True)
    catatan = models.TextField(blank=True)

    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.BARU,
        db_index=True
    )

    dibuat_pada = models.DateTimeField(auto_now_add=True)
    diubah_pada = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Kunjungan"
        ordering = ["-tanggal", "-dibuat_pada"]
        indexes = [
            models.Index(fields=["status", "-tanggal"]),
        ]

    def __str__(self):
        return f"{self.instansi.nama} - {self.tanggal} ({self.sales.username})"


# ---------------------------------------------------------------------------
# FOLLOW-UP WA — PRD section 7.2 & 7.3
# ---------------------------------------------------------------------------
class FollowUpWA(models.Model):
    """Status otomatis (New/Follow Up/Progress) dari klik link WA."""
    class Tahap(models.TextChoices):
        NEW = "NEW", "New"
        FOLLOW_UP = "FOLLOW_UP", "Follow Up"
        PROGRESS = "PROGRESS", "Progress"

    kunjungan = models.OneToOneField(
        Kunjungan, on_delete=models.CASCADE, related_name="followup"
    )
    tahap = models.CharField(
        max_length=15, choices=Tahap.choices, default=Tahap.NEW
    )
    h0_diklik = models.DateTimeField(null=True, blank=True)
    h2_diklik = models.DateTimeField(null=True, blank=True)
    h5_diklik = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Follow-Up WA"

    def __str__(self):
        return f"Follow-up: {self.kunjungan} [{self.get_tahap_display()}]"

    def catat_klik(self, tahap_wa):
        now = timezone.now()
        if tahap_wa == "H0":
            self.h0_diklik = now
            self.tahap = self.Tahap.NEW
        elif tahap_wa == "H2":
            self.h2_diklik = now
            self.tahap = self.Tahap.FOLLOW_UP
        elif tahap_wa == "H5":
            self.h5_diklik = now
            self.tahap = self.Tahap.PROGRESS
        self.save()
