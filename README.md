# Telegram Bot Kit

Template bot Telegram production-ready untuk order freelance: customer service auto-reply, reminder terjadidwal, broadcast rate-limited, dan integrasi Google Sheets opsional.

## Fitur

| Fitur | Perintah | Aktif via |
|---|---|---|
| Sapaan dasar | `/start`, `/help` | selalu |
| Reminder | `/remind 10m cek laporan` | `features.reminder` |
| Broadcast | `/broadcast 123,456 halo semua` | `features.broadcast` |
| Auto-reply FAQ | keyword dari `config.yaml` | `features.auto_reply` |
| Google Sheets | append row (opsional) | `features.sheets` + env |

## Setup

```powershell
# 1. Buat virtualenv & install
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# 2. Konfigurasi
Copy-Item .env.example .env
# Buka .env, isi BOT_TOKEN (dari @BotFather)

# 3. Jalankan
python -m bot
```

## Dapatkan token

1. Buka Telegram, chat [@BotFather](https://t.me/BotFather)
2. `/newbot` → ikuti instruksi → salin token ke `.env`

## Konfigurasi per order klien

Semua perilaku diatur di `config.yaml`:

- **FAQ**: tambah rule `keyword` + `reply` di bagian `auto_reply.rules`
- **Fitur**: matikan yang tidak dipakai di bagian `features`
- **Kecepatan broadcast**: `broadcast.delay_seconds` (detik jeda antar pesan)

## Deploy ke VPS (systemd)

Buat `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
WorkingDirectory=/opt/telegram-bot
ExecStart=/opt/telegram-bot/.venv/bin/python -m bot
Restart=always
EnvironmentFile=/opt/telegram-bot/.env

[Install]
WantedBy=multi-user.target
```

```powershell
sudo systemctl daemon-reload
sudo systemctl enable --now telegram-bot
sudo journalctl -u telegram-bot -f   # lihat log
```

Alternatif tanpa VPS: deploy ke Railway / Render (build command: `pip install -r requirements.txt`, start: `python -m bot`).

## Test

```powershell
pytest
```

## Keamanan

- **Jangan pernah commit `.env`** — token bot = akses penuh ke bot Anda
- `.gitignore` sudah mencakup `.env`, `logs/`, dan credential Google
- File service account Google Sheets juga rahasia; taruh di luar repo atau tambahkan ke `.gitignore`

## Lisensi

MIT — bebas dipakai untuk order klien.
