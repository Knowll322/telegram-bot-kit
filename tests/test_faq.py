"""Test logika FAQ skoring (tanpa network)."""
from bot.config import FaqRule
from bot.faq import match_best, match_faq

RULES = (
    FaqRule(keywords=("harga", "biaya"), reply="harga-1"),
    FaqRule(keywords=("bot", "telegram"), reply="bot-1"),
    FaqRule(keywords=("halo", "hai"), reply="sapa"),
)


def test_match_best_single_keyword():
    assert match_best("berapa biaya yang dikenakan", RULES) == "harga-1"


def test_match_best_word_boundary_no_false_positive():
    # "halogen" tidak boleh kena keyword "halo"
    assert match_best("saya suka halogen", RULES) is None


def test_match_best_highest_score_wins():
    # pesan ini match 2 keyword di rule bot, 0 di lainnya
    assert match_best("butuh bot telegram", RULES) == "bot-1"


def test_match_best_case_insensitive():
    assert match_best("HALO bot", RULES) == "bot-1"  # skor 1 vs 1, menang rule pertama yang dicapai... 
    # "HALO bot": rule harga 0, rule bot 1, rule sapa 1 -> bot (index lebih awal dengan skor sama, karena > strict)


def test_match_best_empty():
    assert match_best("", RULES) is None
    assert match_best("   ", RULES) is None


def test_match_best_no_match():
    assert match_best("cuaca hari ini enak", RULES) is None


def test_match_faq_compat_dict():
    legacy = {"harga": "jawaban-h", "halo": "jawaban-s"}
    assert match_faq("Mana HARGA nya?", legacy) == "jawaban-h"
    assert match_faq("tidak relevan", legacy) is None
