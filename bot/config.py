"""Konfigurasi bot: muat config.yaml + environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class FaqRule:
    keywords: tuple[str, ...]
    reply: str


@dataclass(frozen=True)
class BotConfig:
    token: str
    auto_reply_enabled: bool
    broadcast_enabled: bool
    reminder_enabled: bool
    sheets_enabled: bool
    faq_rules: tuple[FaqRule, ...]
    broadcast_delay_seconds: float
    reminder_max_hours: int
    log_file: str
    log_level: str
    sheets_service_account_json: str = ""
    sheets_id: str = ""
    sheets_range: str = "Sheet1!A:B"
    default_broadcast_chat_id: str = ""

    @property
    def faq_rules_by_keyword(self) -> dict[str, str]:
        """Peta keyword lowercase -> jawaban, untuk pencocokan cepat."""
        mapping: dict[str, str] = {}
        for rule in self.faq_rules:
            for kw in rule.keywords:
                mapping[kw.lower()] = rule.reply
        return mapping


def _parse_faq_rules(raw_rules: list[dict[str, Any]]) -> tuple[FaqRule, ...]:
    rules: list[FaqRule] = []
    for item in raw_rules:
        keywords = item.get("keyword") or item.get("keywords") or []
        reply = item.get("reply", "")
        if not keywords or not reply:
            continue
        if isinstance(keywords, str):
            keywords = [keywords]
        rules.append(FaqRule(keywords=tuple(str(k).lower() for k in keywords), reply=str(reply)))
    return tuple(rules)


def load_config(config_path: str | Path = "config.yaml") -> BotConfig:
    """Muat konfigurasi dari YAML dan .env. Token wajib ada di BOT_TOKEN."""
    load_dotenv()

    path = Path(config_path)
    data: dict[str, Any] = {}
    if path.exists():
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    features = data.get("features", {}) or {}
    auto_reply_cfg = data.get("auto_reply", {}) or {}
    broadcast_cfg = data.get("broadcast", {}) or {}
    reminder_cfg = data.get("reminder", {}) or {}
    logging_cfg = data.get("logging", {}) or {}

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise ValueError(
            "BOT_TOKEN belum diisi. Salin .env.example menjadi .env lalu isi token dari @BotFather."
        )

    return BotConfig(
        token=token,
        auto_reply_enabled=bool(features.get("auto_reply", False)),
        broadcast_enabled=bool(features.get("broadcast", False)),
        reminder_enabled=bool(features.get("reminder", False)),
        sheets_enabled=bool(features.get("sheets", False)),
        faq_rules=_parse_faq_rules(auto_reply_cfg.get("rules", []) or []),
        broadcast_delay_seconds=float(broadcast_cfg.get("delay_seconds", 1.0)),
        reminder_max_hours=int(reminder_cfg.get("max_hours_ahead", 168)),
        log_file=str(logging_cfg.get("file", "logs/bot.log")),
        log_level=str(logging_cfg.get("level", "INFO")),
        sheets_service_account_json=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", ""),
        sheets_id=os.getenv("GOOGLE_SHEET_ID", ""),
        sheets_range=os.getenv("GOOGLE_SHEET_RANGE", "Sheet1!A:B"),
        default_broadcast_chat_id=os.getenv("DEFAULT_BROADCAST_CHAT_ID", ""),
    )
