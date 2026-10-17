"""Entry point: rakit Application, daftarkan handler sesuai fitur aktif."""
from __future__ import annotations

import logging
import os
import re
from datetime import timedelta
from functools import partial

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from bot.broadcast import broadcast, parse_chat_ids
from bot.config import BotConfig, load_config
from bot.faq import match_best
from bot.logging_setup import setup_logging
from bot.pricing import (
    DEFAULT_CONTACT,
    DEFAULT_FALLBACK,
    DEFAULT_ORDER,
    DEFAULT_PORTFOLIO,
    format_price,
    resolve,
)

logger = logging.getLogger(__name__)

_REMIND_RE = re.compile(r"^(\d+)([smh])\s+(.+)$")


def _parse_remind(text: str) -> tuple[int, str] | None:
    """Parse '30m cek laporan' -> (detik, pesan). Return None jika format salah."""
    m = _REMIND_RE.match(text.strip())
    if not m:
        return None
    amount = int(m.group(1))
    unit = m.group(2)
    message = m.group(3).strip()
    multiplier = {"s": 1, "m": 60, "h": 3600}[unit]
    return amount * multiplier, message


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Halo! Saya Alexsander LL Bot — asisten jasa bot & automation.\n"
        "\nSilakan pilih:\n"
        "/price — daftar harga layanan\n"
        "/order — cara pesan\n"
        "/portofolio — contoh kode kerja\n"
        "/kontak — info layanan\n"
        "/remind 10m cek laporan — pengingat\n"
        "\nAtau langsung tanya apa saja, mis. \"berapa harga bot absensi?\""
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/price — daftar harga\n"
        "/order — alur pemesanan\n"
        "/portofolio — repo GitHub & landing page\n"
        "/kontak — jam layanan & cara hubungi\n"
        "/remind <waktu> <pesan> — contoh: /remind 30m cek email\n"
        "/broadcast <id,pesan> — khusus admin\n"
        "\nTulis pertanyaan bebas juga bisa — saya usahakan jawab."
    )


async def cmd_price(update: Update, context: ContextTypes.DEFAULT_TYPE, cfg: BotConfig) -> None:
    await update.message.reply_text(format_price(cfg))


async def cmd_order(update: Update, context: ContextTypes.DEFAULT_TYPE, cfg: BotConfig) -> None:
    await update.message.reply_text(resolve(cfg, "order", DEFAULT_ORDER))


async def cmd_portfolio(update: Update, context: ContextTypes.DEFAULT_TYPE, cfg: BotConfig) -> None:
    await update.message.reply_text(resolve(cfg, "portfolio", DEFAULT_PORTFOLIO))


async def cmd_contact(update: Update, context: ContextTypes.DEFAULT_TYPE, cfg: BotConfig) -> None:
    await update.message.reply_text(resolve(cfg, "contact", DEFAULT_CONTACT))


async def cmd_remind(update: Update, context: ContextTypes.DEFAULT_TYPE, cfg: BotConfig) -> None:
    if not cfg.reminder_enabled:
        return
    if not context.args:
        await update.message.reply_text("Format: /remind 10m cek laporan (satuan: s/m/h)")
        return

    parsed = _parse_remind(" ".join(context.args))
    if parsed is None:
        await update.message.reply_text("Format salah. Contoh: /remind 30m cek email")
        return

    seconds, message = parsed
    if seconds > cfg.reminder_max_hours * 3600:
        await update.message.reply_text(
            f"Reminder maksimal {cfg.reminder_max_hours} jam ke depan."
        )
        return

    chat_id = update.effective_chat.id
    context.application.job_queue.run_once(
        _send_reminder,
        when=timedelta(seconds=seconds),
        data={"chat_id": chat_id, "message": message},
        name=f"remind_{chat_id}_{seconds}",
    )
    await update.message.reply_text(f"Oke, saya ingatkan dalam {seconds} detik.")


async def _send_reminder(context: ContextTypes.DEFAULT_TYPE) -> None:
    data = context.job.data
    await context.bot.send_message(
        chat_id=data["chat_id"], text=f"Pengingat: {data['message']}"
    )


async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE, cfg: BotConfig) -> None:
    if not cfg.broadcast_enabled:
        return
    # Hanya admin yang boleh broadcast. Sesuaikan ADMIN_IDS di .env jika perlu.
    admin_ids = {int(x) for x in os.getenv("ADMIN_IDS", "").split() if x.strip().isdigit()}
    if admin_ids and update.effective_user.id not in admin_ids:
        await update.message.reply_text("Hanya admin yang boleh broadcast.")
        return
    if not context.args:
        await update.message.reply_text(
            "Format: /broadcast <chat_id,chat_id,...> <pesan>\n"
            "atau set DEFAULT_BROADCAST_CHAT_ID di .env lalu: /broadcast <pesan>"
        )
        return

    # Pisahkan token pertama: jika berupa daftar angka -> target, selain itu -> pesan penuh
    first, *rest = context.args
    if re.fullmatch(r"[\d,\s]+", first):
        targets = parse_chat_ids(first, cfg.default_broadcast_chat_id)
        message = " ".join(rest)
    else:
        targets = parse_chat_ids(None, cfg.default_broadcast_chat_id)
        message = " ".join(context.args)

    if not targets or not message:
        await update.message.reply_text("Target atau pesan kosong.")
        return

    await update.message.reply_text(f"Mengirim broadcast ke {len(targets)} chat...")
    summary = await broadcast(
        context.bot, targets, message, delay_seconds=cfg.broadcast_delay_seconds
    )
    await update.message.reply_text(
        f"Broadcast selesai. Terkirim: {summary['sent']}, "
        f"blocked: {summary['blocked']}, gagal: {summary['failed']}."
    )


async def on_text(update: Update, context: ContextTypes.DEFAULT_TYPE, cfg: BotConfig) -> None:
    """Jawab setiap pesan teks: FAQ skoring -> AI (opsional) -> fallback."""
    if update.message is None or not update.message.text:
        return
    text = update.message.text

    if cfg.auto_reply_enabled:
        reply = match_best(text, cfg.faq_rules)
        if reply:
            await update.message.reply_text(reply)
            return

    if cfg.ai_enabled:
        from bot.ai import ai_answer  # import lokal: butuh GEMINI_API_KEY

        reply = await context.application.run_sync(ai_answer, text)
        if reply:
            await update.message.reply_text(reply)
            return

    # Auto-reply mati? tetap diam. Tapi kalau fitur aktif tapi tak match -> fallback
    if cfg.auto_reply_enabled:
        await update.message.reply_text(resolve(cfg, "fallback", DEFAULT_FALLBACK))


def build_application(cfg: BotConfig) -> Application:
    app = Application.builder().token(cfg.token).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))

    # partial (bukan lambda) supaya PTB mengenali callback sebagai coroutine function
    app.add_handler(CommandHandler("price", partial(cmd_price, cfg=cfg)))
    app.add_handler(CommandHandler("order", partial(cmd_order, cfg=cfg)))
    app.add_handler(CommandHandler("portofolio", partial(cmd_portfolio, cfg=cfg)))
    app.add_handler(CommandHandler("kontak", partial(cmd_contact, cfg=cfg)))
    if cfg.reminder_enabled:
        app.add_handler(CommandHandler("remind", partial(cmd_remind, cfg=cfg)))
    if cfg.broadcast_enabled:
        app.add_handler(CommandHandler("broadcast", partial(cmd_broadcast, cfg=cfg)))
    if cfg.auto_reply_enabled:
        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, partial(on_text, cfg=cfg))
        )

    return app


def main() -> None:
    cfg = load_config()
    setup_logging(cfg.log_file, cfg.log_level)
    logger.info(
        "Bot mulai (fitur: auto_reply=%s broadcast=%s reminder=%s sheets=%s)",
        cfg.auto_reply_enabled,
        cfg.broadcast_enabled,
        cfg.reminder_enabled,
        cfg.sheets_enabled,
    )
    app = build_application(cfg)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
