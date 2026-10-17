"""Format pesan statis command: /price, /order, /portofolio, /kontak.

Teks default dipakai kalau config.yaml tidak menyediakan blok `pricing`/`texts`.
Semua bisa dioverride per order klien lewat config.yaml.
"""
from __future__ import annotations

from bot.config import BotConfig

DEFAULT_PRICING: tuple[tuple[str, str, str], ...] = (
    ("Bot Telegram Custom", "Mulai Rp350.000", "Basic Rp350rb / Standard Rp750rb / Premium Rp1,5jt"),
    ("Monitor Stok & Harga", "Mulai Rp500.000", "Basic Rp500rb / Standard Rp1,2jt / Premium Rp2,5jt"),
    ("Web Scraper Data", "Mulai Rp400.000", "Basic Rp400rb / Standard Rp1jt / Premium Rp2jt"),
)

DEFAULT_ORDER = (
    "Cara order:\n"
    "1. Ceritakan kebutuhan Anda (bisa langsung chat di sini)\n"
    "2. Saya balas estimasi harga + waktu pengerjaan — GRATIS\n"
    "3. Deal → DP 50% → pengerjaan → pelunasan → serah terima source code\n"
    "\nRevisi sesuai paket. Include deploy + dokumentasi."
)

DEFAULT_PORTFOLIO = (
    "Portofolio kode (open-source, ada unit test):\n"
    "• Bot Telegram kit: https://github.com/Knowll322/telegram-bot-kit\n"
    "• Stock monitor kit: https://github.com/Knowll322/stock-monitor-kit\n"
    "• Landing page: https://knowll322.github.io\n"
    "\nMau demo langsung? Ketik /price dulu, lalu ceritakan kebutuhan Anda."
)

DEFAULT_CONTACT = (
    "Alexsander LL Bot — layanan bot & automation\n"
    "Jam layanan: setiap hari 09.00–21.00 WIB (chat kapan saja, dibalas di jam layanan)\n"
    "Balas chat ini saja untuk konsultasi — gratis, tanpa komitmen."
)

DEFAULT_FALLBACK = (
    "Maaf, saya belum mengerti pertanyaannya. Coba:\n"
    "/price — daftar harga\n"
    "/order — cara pesan\n"
    "/portofolio — contoh kode kerja\n"
    "/kontak — info layanan\n"
    "\nAtau tulis pertanyaan langsung, mis. \"berapa harga bot absensi?\""
)


def format_price(cfg: BotConfig) -> str:
    rows = cfg.pricing or DEFAULT_PRICING
    lines = ["DAFTAR HARGA — Alexsander LL Bot", ""]
    for i, (name, price, detail) in enumerate(rows, 1):
        lines.append(f"{i}. {name} — {price}")
        lines.append(f"   {detail}")
    lines.append("")
    lines.append("Harga final mengikuti scope. Semua include deploy + dokumentasi.")
    lines.append("Cara order: /order — konsultasi gratis: balas chat ini aja.")
    return "\n".join(lines)


def resolve(cfg: BotConfig, key: str, default: str) -> str:
    """Ambil teks override dari config (blok texts), fallback ke default."""
    return (cfg.texts.get(key) or "").strip() or default
