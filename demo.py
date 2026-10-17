"""Demo offline — jalankan tanpa token Telegram asli, tanpa network.

Rekam layar terminal saat menjalankan script ini untuk video portofolio:

    python demo.py

Semua "notifikasi Telegram" dicetak ke layar sebagai simulasi.
"""
from __future__ import annotations

import time

from bot.broadcast import parse_chat_ids
from bot.config import BotConfig, load_config
from bot.faq import match_faq
from bot.main import _parse_remind

# Konfigurasi demo — token dummy, fitur aktif, tanpa .env
DEMO_CONFIG = BotConfig(
    token="DEMO:dummy-token-tidak-dipakai",
    auto_reply_enabled=True,
    broadcast_enabled=True,
    reminder_enabled=True,
    sheets_enabled=False,
    faq_rules=tuple(),  # diisi di bawah
    broadcast_delay_seconds=0.1,
    reminder_max_hours=168,
    log_file="logs/demo.log",
    log_level="INFO",
)

DEMO_FAQ = {
    "harga": "Harga mulai Rp350.000. Chat admin untuk konsultasi gratis ya!",
    "jam": "Kami online setiap hari 09.00-21.00 WIB.",
    "halo": "Halo! Ada yang bisa dibantu?",
}
DEMO_CONFIG = BotConfig(
    token=DEMO_CONFIG.token,
    auto_reply_enabled=True,
    broadcast_enabled=True,
    reminder_enabled=True,
    sheets_enabled=False,
    faq_rules=(),
    broadcast_delay_seconds=0.1,
    reminder_max_hours=168,
    log_file=DEMO_CONFIG.log_file,
    log_level=DEMO_CONFIG.log_level,
)

# frozen dataclass — rebuild dengan FAQ rules
from dataclasses import replace
from bot.config import FaqRule

DEMO_CONFIG = replace(
    DEMO_CONFIG,
    faq_rules=(
        FaqRule(keywords=("harga", "price"), reply=DEMO_FAQ["harga"]),
        FaqRule(keywords=("jam",), reply=DEMO_FAQ["jam"]),
        FaqRule(keywords=("halo", "hai", "hi"), reply=DEMO_FAQ["halo"]),
    ),
)


def _banner(text: str) -> None:
    print("\n" + "=" * 56)
    print(f"  {text}")
    print("=" * 56)


def demo_faq() -> None:
    _banner("DEMO 1 — Auto-reply FAQ")
    rules = DEMO_CONFIG.faq_rules_by_keyword
    samples = [
        "Halo bot, saya mau tanya",
        "Berapa harga jasa pembuatan bot?",
        "Jam berapa admin online?",
        "Ini pesan biasa tanpa kata kunci",
    ]
    for msg in samples:
        print(f"\n[User] {msg}")
        time.sleep(0.5)
        reply = match_faq(msg, rules)
        print(f"[Bot ] {reply or '(tidak ada match — diam)'}")
        time.sleep(0.5)


def demo_reminder() -> None:
    _banner("DEMO 2 — Reminder Terjadwal")
    for spec in ["10m cek laporan penjualan", "2h rapat tim marketing", "30s minum air"]:
        parsed = _parse_remind(spec)
        if parsed:
            seconds, message = parsed
            print(f"\n[/remind {spec}]")
            print(f"  -> Dijadwalkan: '{message}' dalam {seconds} detik")
            time.sleep(0.5)


def demo_broadcast() -> None:
    _banner("DEMO 3 — Broadcast Rate-Limited")
    raw = "10001, 10002, 10003, 10004, 10005"
    ids = parse_chat_ids(raw)
    print(f"\nTarget: {raw}")
    print(f"Chat id ter-parse: {ids}")
    print(f"Jeda antar pesan: {DEMO_CONFIG.broadcast_delay_seconds}s (aman dari flood limit)")
    for cid in ids:
        print(f"  [kirim] chat_id={cid} -> 'Promo bulan ini: diskon 20% semua layanan bot!'")
        time.sleep(0.3)
    print("\n  Ringkasan: terkirim=5, blocked=0, gagal=0")


def main() -> None:
    print("TELEGRAM BOT KIT — Demo Mode")
    print("Simulasi penuh tanpa koneksi Telegram.")
    demo_faq()
    demo_reminder()
    demo_broadcast()
    _banner("SELESAI")
    print("Untuk bot live: isi BOT_TOKEN di .env lalu jalankan python -m bot\n")


if __name__ == "__main__":
    main()
