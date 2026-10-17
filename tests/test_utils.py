"""Test parser reminder & chat id broadcast (tanpa network)."""
from bot.broadcast import parse_chat_ids
from bot.main import _parse_remind


def test_parse_remind_minutes():
    assert _parse_remind("10m cek laporan") == (600, "cek laporan")


def test_parse_remind_hours():
    assert _parse_remind("2h rapat") == (7200, "rapat")


def test_parse_remind_seconds():
    assert _parse_remind("45s cek") == (45, "cek")


def test_parse_remind_invalid():
    assert _parse_remind("besok ingatkan saya") is None
    assert _parse_remind("") is None


def test_parse_chat_ids_comma():
    assert parse_chat_ids("123, 456,789") == [123, 456, 789]


def test_parse_chat_ids_fallback():
    assert parse_chat_ids("", "111 222") == [111, 222]


def test_parse_chat_ids_garbage_filtered():
    assert parse_chat_ids("123,abc,456") == [123, 456]


def test_parse_chat_ids_empty():
    assert parse_chat_ids(None, None) == []
