"""Utilitas FAQ auto-reply: cocokkan pesan masuk terhadap rules config."""
from __future__ import annotations


def match_faq(text: str, rules_by_keyword: dict[str, str]) -> str | None:
    """Return jawaban pertama yang keyword-nya ditemukan di pesan, atau None.

    Pencocokan case-insensitive sederhana. Urutan rule di config menentukan prioritas.
    """
    lowered = text.lower()
    for keyword, reply in rules_by_keyword.items():
        if keyword in lowered:
            return reply
    return None
