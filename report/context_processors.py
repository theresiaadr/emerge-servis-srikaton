"""Context processor: badge notifikasi reminder global (AI-7)."""
from .views import hitung_reminder


def reminder_badge(request):
    return {"reminder_count": hitung_reminder(request.user)}
