"""Form input kunjungan & validasi nomor WA (PRD section 12)."""
import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from captcha.fields import CaptchaField
from .models import Kunjungan, Instansi


class LoginForm(AuthenticationForm):
    """Form login standar Django (username/password + authenticate lewat
    axes backend) + 1 field captcha tambahan (AI-1b)."""
    captcha = CaptchaField(label="Kode Keamanan")


def validasi_no_wa(value):
    if not value:
        return value
    bersih = value.strip().replace(" ", "").replace("-", "").replace("+", "")
    if not re.fullmatch(r"0\d{8,14}|62\d{8,14}", bersih):
        raise forms.ValidationError(
            "Format nomor tidak valid. Gunakan 08xxx atau 62xxx."
        )
    return value


class KunjunganForm(forms.ModelForm):
    # Field instansi ditulis bebas (dengan autocomplete di frontend),
    # nanti dicocokkan/dibuat di view.
    nama_instansi = forms.CharField(
        max_length=200, label="Nama Instansi",
        widget=forms.TextInput(attrs={
            "list": "daftar-instansi", "autocomplete": "off",
            "placeholder": "Ketik nama instansi...",
        })
    )

    class Meta:
        model = Kunjungan
        fields = ["tanggal", "pic", "no_wa", "alamat", "catatan", "status"]
        widgets = {
            "tanggal": forms.DateInput(attrs={"type": "date"}),
            "alamat": forms.Textarea(attrs={"rows": 2}),
            "catatan": forms.Textarea(attrs={"rows": 3,
                     "placeholder": "Catatan hasil kunjungan / update tambahan"}),
        }

    def clean_no_wa(self):
        return validasi_no_wa(self.cleaned_data.get("no_wa"))
