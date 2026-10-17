"""Test logika FAQ (tanpa network)."""
from bot.faq import match_faq

RULES = {
    "harga": "Harga mulai Rp350.000.",
    "halo": "Halo! Ada yang bisa dibantu?",
    "jam kerja": "Kami online 09.00-21.00 WIB.",
}


def test_match_case_insensitive():
    assert match_faq("Mohon info HARGA dong", RULES) == "Harga mulai Rp350.000."


def test_match_substring():
    assert match_faq("halo kak, mau tanya", RULES) == "Halo! Ada yang bisa dibantu?"


def test_no_match_returns_none():
    assert match_faq("apalah ini pesan acak", RULES) is None


def test_empty_text():
    assert match_faq("", RULES) is None
