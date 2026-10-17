"""Integrasi Google Sheets via service account (opsional, feature-flagged).

Credential TIDAK boleh di-commit. Isi path file service account lewat env var.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class SheetsStorage:
    """Append baris sederhana ke Google Spreadsheet."""

    def __init__(self, service_account_json: str, spreadsheet_id: str, cell_range: str):
        self._path = service_account_json
        self._id = spreadsheet_id
        self._range = cell_range
        self._client = None

    def _ensure_client(self):
        if self._client is not None:
            return self._client
        if not self._path or not Path(self._path).exists():
            raise FileNotFoundError(
                "File service account tidak ditemukan. Set GOOGLE_SERVICE_ACCOUNT_JSON di .env."
            )
        if not self._id:
            raise ValueError("GOOGLE_SHEET_ID belum diisi di .env.")

        import gspread

        self._client = gspread.service_account(filename=self._path)
        return self._client

    def append_row(self, values: list) -> None:
        """Tambah satu baris. Gagal logged, tidak crash bot."""
        try:
            client = self._ensure_client()
            sheet = client.open_by_key(self._id)
            worksheet = sheet.worksheet(self._range.split("!")[0]) if "!" in self._range else sheet.sheet1
            worksheet.append_row(values)
        except Exception:
            logger.exception("Gagal append ke Google Sheets")


def is_configured(service_account_json: str, spreadsheet_id: str) -> bool:
    return bool(service_account_json) and bool(spreadsheet_id)
