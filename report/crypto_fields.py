"""
Field terenkripsi (Fernet/AES). Kunci dari env DJANGO_FIELD_ENCRYPTION_KEY.
Data tersimpan terenkripsi di DB, otomatis didekripsi saat dibaca.
"""
import os
from cryptography.fernet import Fernet, InvalidToken
from django.db import models


def _get_fernet():
    key = os.environ.get("DJANGO_FIELD_ENCRYPTION_KEY", "")
    if not key:
        # Dev fallback: kunci tetap (JANGAN dipakai di produksi).
        key = "ZmDfcTF7_60GrrY167zsiPd67pEvs0aGOv2oasOM1Pg="
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
