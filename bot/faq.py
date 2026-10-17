"""Logika FAQ auto-reply: cocokkan pesan masuk terhadap rules config.

match_best: skoring per-rule — rule dengan jumlah keyword terbanyak yang cocok
menang. Pencocokan pakai word-boundary supaya "halo" tidak ikut match di
"halogen".
"""
from __future__ import annotations

import re

from bot.config import FaqRule


def _hit(text_lower: str, keyword: str) -> bool:
    return re.search(rf"\b{re.escape(keyword)}\b", text_lower) is not None


def match_best(text: str, rules: tuple[FaqRule, ...]) -> str | None:
    """Balasan dari rule dengan skor (jumlah keyword cocok) tertinggi, atau None."""
    lowered = (text or "").strip().lower()
    if not lowered:
        return None

    best_reply: str | None = None
    best_score = 0
    for rule in rules:
        score = sum(1 for kw in rule.keywords if _hit(lowered, kw))
        if score > best_score:
            best_reply, best_score = rule.reply, score
    return best_reply


def match_faq(text: str, rules_by_keyword: dict[str, str]) -> str | None:
    """Compat lama (dict pipih): balasan pertama yang keyword-nya ditemukan."""
    lowered = (text or "").lower()
    for keyword, reply in rules_by_keyword.items():
        if keyword in lowered:
            return reply
    return None
