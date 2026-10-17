"""Broadcast rate-limited ke daftar chat id.

Telegram membatasi ~30 pesan/detik per bot. Default di sini jauh di bawah
itu supaya aman untuk broadcast ribuan member sekalipun.
"""
from __future__ import annotations

import asyncio
import logging

from telegram import Bot
from telegram.error import ChatMigrated, Forbidden, TelegramError

logger = logging.getLogger(__name__)


async def broadcast(
    bot: Bot,
    chat_ids: list[int | str],
    text: str,
    *,
    delay_seconds: float = 1.0,
) -> dict[str, int]:
    """Kirim pesan ke semua chat_id dengan jeda antar pesan.

    Return ringkasan: {"sent": n, "failed": n, "blocked": n}.
    Gagal di satu chat tidak menghentikan chat lain.
    """
    summary = {"sent": 0, "failed": 0, "blocked": 0}
    seen: set[int] = set()

    for chat_id in chat_ids:
        try:
            cid = int(chat_id)
        except (TypeError, ValueError):
            logger.warning("chat_id tidak valid dilewati: %r", chat_id)
            summary["failed"] += 1
            continue

        if cid in seen:  # dedup, jangan kirim dua kali
            continue
        seen.add(cid)

        try:
            await bot.send_message(chat_id=cid, text=text)
            summary["sent"] += 1
        except Forbidden:
            # Bot di-block / user tidak pernah start bot
            summary["blocked"] += 1
        except ChatMigrated as exc:
            logger.info("Chat %s migrate ke %s, coba ulang", cid, exc.new_chat_id)
            try:
                await bot.send_message(chat_id=exc.new_chat_id, text=text)
                summary["sent"] += 1
            except TelegramError:
                summary["failed"] += 1
        except TelegramError as exc:
            logger.error("Gagal kirim ke %s: %s", cid, exc)
            summary["failed"] += 1

        await asyncio.sleep(delay_seconds)

    logger.info("Broadcast selesai: %s", summary)
    return summary


def parse_chat_ids(raw: str | None, fallback: str | None = None) -> list[int]:
    """Parse daftar chat id dari string dipisah koma/spasi; fallback dipakai jika kosong."""
    source = (raw or "").strip() or (fallback or "").strip()
    if not source:
        return []
    ids: list[int] = []
    for part in source.replace(",", " ").split():
        try:
            ids.append(int(part))
        except ValueError:
            continue
    return ids
