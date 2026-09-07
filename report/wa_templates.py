"""
Template pesan WhatsApp H0/H2/H5 + generator link wa.me.
Sesuai PRD section 9. Variabel diisi otomatis dari data kunjungan & sales.
"""
from urllib.parse import quote


def _normalisasi_no_wa(no):
    """Ubah 08xxx -> 628xxx supaya link wa.me valid (PRD: validasi format WA)."""
    no = (no or "").strip().replace(" ", "").replace("-", "").replace("+", "")
    if no.startswith("0"):
        return "62" + no[1:]
    if no.startswith("62"):
        return no
    # kalau sudah format lain, kembalikan apa adanya
    return no


def pesan_h0(nama_sales, no_hp_sales):
    return (
        "Selamat pagi Bapak/Ibu,\n"
        f"Perkenalkan saya {nama_sales} dari PT. Srikaton Inovasi Teknologi,\n"
        "Kami bergerak dalam Pengadaan IT (Komputer, Server, Command Center, "
        "CCTV dan Pembuatan Layanan/Aplikasi secara Custom untuk kebutuhan "
        "Instansi Pemerintah, TNI/Polri, Sekolah/Universitas, BUMN)\n"
        "Jika Bapak dan Ibu berkenan, kami akan berkunjung untuk "
        "mempresentasikan produk-produk kami.\n"
        "Mohon izin waktu untuk bertemu dengan Pejabat terkait...\n"
        "Terima kasih\n"
        f"{nama_sales} // {no_hp_sales}\n"
        "(PT. Srikaton Inovasi Teknologi)"
    )


def pesan_h2(nama_pic, nama_instansi):
    sapaan = f"Bapak/Ibu {nama_pic}" if nama_pic else "Bapak/Ibu"
    return (
        f"Selamat pagi {sapaan}, izin follow up terkait "
        f"penawaran untuk {nama_instansi}. Jika ada kebutuhan atau "
        "pertanyaan, kami siap membantu 🙏"
    )


def pesan_h5(nama_pic, nama_instansi):
    sapaan = f"Bapak/Ibu {nama_pic}" if nama_pic else "Bapak/Ibu"
    return (
        f"Selamat pagi {sapaan}, kami mengingatkan kembali "
        f"terkait kebutuhan {nama_instansi}. Saat ini kami siap membantu "
        "jika dibutuhkan tindak lanjut."
    )


def build_link_wa(no_wa, pesan):
    """Bangun link wa.me/<nomor>?text=<pesan terenkode>."""
    nomor = _normalisasi_no_wa(no_wa)
    if not nomor:
        return ""
    return f"https://wa.me/{nomor}?text={quote(pesan)}"


def semua_link_wa(kunjungan):
    """
    Kembalikan dict {H0, H2, H5} berisi (pesan, link) untuk 1 kunjungan.
    Dipakai di halaman Blast WA.
    """
    sales = kunjungan.sales
    nama_sales = sales.get_full_name() or sales.username
    no_hp_sales = sales.no_hp or ""
    nama_pic = kunjungan.pic or kunjungan.instansi.pic
    nama_instansi = kunjungan.instansi.nama
    no_wa = kunjungan.no_wa or kunjungan.instansi.no_wa

    p0 = pesan_h0(nama_sales, no_hp_sales)
    p2 = pesan_h2(nama_pic, nama_instansi)
    p5 = pesan_h5(nama_pic, nama_instansi)

    return {
        "H0": {"pesan": p0, "link": build_link_wa(no_wa, p0)},
        "H2": {"pesan": p2, "link": build_link_wa(no_wa, p2)},
        "H5": {"pesan": p5, "link": build_link_wa(no_wa, p5)},
    }
