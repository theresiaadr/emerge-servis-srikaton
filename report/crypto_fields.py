"""
Field terenkripsi (Fernet/AES). Kunci dari env DJANGO_FIELD_ENCRYPTION_KEY.
Data tersimpan terenkripsi di DB, otomatis didekripsi saat dibaca.
"""
import os
from cryptography.fernet import Fernet, InvalidToken
from django.core.exceptions import ImproperlyConfigured
from django.db import models

_DEV_FALLBACK_KEY = "ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg="


def _get_fernet():
    from django.conf import settings

    key = os.environ.get("DJANGO_FIELD_ENCRYPTION_KEY", "")
    if not key:
        if not settings.DEBUG:
            raise ImproperlyConfigured(
                "DJANGO_FIELD_ENCRYPTION_KEY kosong padahal DEBUG=0. "
                "Wajib diisi di produksi, tidak boleh pakai kunci dev."
            )
        # Dev fallback: kunci tetap (JANGAN dipakai di produksi).
        key = _DEV_FALLBACK_KEY
    return Fernet(key.encode() if isinstance(key, str) else key)


class EncryptedTextField(models.TextField):
    """TextField yang otomatis enkripsi saat simpan, dekripsi saat baca."""

    def get_prep_value(self, value):
        if value is None or value == "":
            return value
        f = _get_fernet()
        return f.encrypt(str(value).encode()).decode()

    def from_db_value(self, value, expression, connection):
        if value is None or value == "":
            return value
        f = _get_fernet()
        try:
            return f.decrypt(value.encode()).decode()
        except (InvalidToken, Exception):
            # Kalau data lama belum terenkripsi, kembalikan apa adanya
            return value


class EncryptedCharField(EncryptedTextField):
    """Sama seperti EncryptedTextField tapi untuk field pendek (no_wa)."""
    pass
