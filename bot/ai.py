"""Jawaban AI opsional untuk pertanyaan yang tidak kena FAQ.

Aktif hanya jika features.ai=true di config.yaml DAN GEMINI_API_KEY ada di .env.
Pakai httpx (sudah jadi dependensi python-telegram-bot) — tanpa dependensi baru.

Fallback selalu aman: kalau key kosong / call gagal, return None dan pemanggil
memakai teks fallback biasa.
"""
from __future__ import annotations

import logging
import os

import httpx

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Kamu customer service Alexsander LL Bot, jasa pembuatan bot Telegram custom, "
    "monitor stok/harga real-time, dan web scraper data (Python). "
    "Harga mulai: bot Rp350rb, monitor Rp500rb, scraper Rp400rb. "
    "Pengerjaan 2-7 hari, sistem DP 50%, include deploy + dokumentasi, "
    "jam layanan 09.00-21.00 WIB. "
    "Jawab dalam bahasa Indonesia, singkat (1-3 kalimat), sopan, tanpa mengarang "
    "layanan/bio yang tidak disebutkan. Kalau ditanya harga detail, arahkan ke perintah /price. "
    "Kalau di luar topok jasa ini, jawab singkat lalu arahkan ke /price."
)


def ai_answer(text: str, model: str = "gemini-2.0-flash") -> str | None:
    """Kirim pertanyaan ke Gemini. Return None jika tidak tersedia/gagal."""
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    payload = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": text}]}],
        "generationConfig": {"maxOutputTokens": 300, "temperature": 0.4},
    }
    try:
        with httpx.Client(timeout=8.0) as client:
            resp = client.post(url, params={"key": key}, json=payload)
            resp.raise_for_status()
            candidates = resp.json().get("candidates") or []
            if not candidates:
                return None
            parts = candidates[0].get("content", {}).get("parts") or []
            answer = "".join(p.get("text", "") for p in parts).strip()
            return answer or None
    except Exception:
        logger.exception("AI answer gagal, pakai fallback biasa")
        return None
