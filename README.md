# 🖨️ Telegram Printer Bot

> **100% vibecoded.** Not a single line of this project was written by a human. The entire codebase — bot, translations, docs, even this README — was generated from scratch by AI ([Perplexity Computer](https://www.perplexity.ai/)). No human fingers touched any code, CSS, or config. Pure vibes, zero keystrokes.

Full-featured Telegram bot for Klipper/Moonraker 3D printers — inline buttons everywhere, multi-language, auto-refresh, multi-printer support, offline detection.

## Project Structure

```
telegram-printer-bot/
├── bot.py              # Entry point — registers handlers, starts polling
├── config.py           # Config loader/saver (single & multi-printer)
├── config.yaml         # Your configuration (edit this!)
├── api.py              # Moonraker API client (per-user printer routing)
├── lang.py             # Translations (EN / DE / RU / PL)
├── helpers.py          # Auth decorators, formatting, button builders
├── monitor.py          # Background monitor (notifications, filament, offline detection)
├── handlers/
│   ├── menu.py         # Main menu + router
│   ├── status.py       # Status dashboard + auto-refresh
│   ├── temps.py        # Temperature control + presets
│   ├── files.py        # Paginated file browser
│   ├── control.py      # Print control (pause/resume/cancel)
│   ├── gcode.py        # GCode console
│   ├── macros.py       # Klipper macro runner
│   ├── camera.py       # Camera snapshots
│   ├── system.py       # System info + restart
│   ├── estop.py        # Emergency stop
│   ├── settings.py     # Live settings menu
│   └── printers.py     # Multi-printer selector
└── requirements.txt
```

## Features

### 🌐 Multi-Language
Switch between English, Deutsch, Русский, and Polski right from the settings menu. Every button, message, and notification is translated.

### 🖨️ Multi-Printer Support
Control multiple printers from a single bot. Each user can switch between printers independently — the active printer is tracked per-user.

**To enable multi-printer**, change `config.yaml` from the single printer format to:

```yaml
printers:
  - name: "Neptune"
    moonraker:
      url: "http://192.168.1.100:7125"
      api_key: ""
    camera:
      snapshot_url: ""
      stream_url: ""
  - name: "Ender 3"
    moonraker:
      url: "http://192.168.1.101:7125"
      api_key: ""
    camera:
      snapshot_url: "http://192.168.1.101/webcam/?action=snapshot"
      stream_url: ""
```

With one printer configured, the bot works exactly like before — no switch button, no printer badges. Add a second printer and the multi-printer UI appears automatically.

### 📊 Status Dashboard (Auto-Refresh)
- Progress bar, ETA, duration, filament used, temperatures
- **Auto-refresh**: tap the button and the status updates itself every 5 seconds — no need to keep pressing refresh

### 🌡️ Temperature Control
- Material presets (PLA, PETG, ABS, TPU, Nylon)
- Custom temperature input
- Cool-all button
- Heater power display

### 📂 Paginated File Browser
- Navigate with prev/next buttons
- Sort by date or name
- File info (slicer, layers, estimated time, filament usage)
- Print or delete with confirmation

### 🖨️ Print Control
- Context-aware buttons (pause when printing, resume when paused)
- Home axes, motors off
- Cancel with confirmation

### ⚡ Macros
- Auto-discovers Klipper macros
- Run with confirmation

### 💻 GCode Console
- Quick buttons (G28, G90, G91, M84, fan)
- Type any GCode command

### 📷 Camera
- Snapshot on demand
- Live stream link

### 🔧 System
- Moonraker/Klipper versions, CPU, RAM, uptime
- Firmware restart / host reboot

### 🚨 Emergency Stop
- Configurable confirmation
- Can be hidden from menu

### 🔔 Notifications
- Print complete / error / started / cancelled
- **Filament runout detection** (works with Klipper filament sensors)
- **Printer offline/online detection** — notifies you when a printer goes unreachable (after 3 consecutive failed polls) and when it comes back
- Temperature alerts

### ⚙️ Live Settings
- Toggle every notification type (including offline detection)
- Change language, poll interval, files per page
- E-Stop visibility and confirmation
- All saved to config.yaml instantly

## Setup

### 1. Create your Telegram Bot
Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy token.

### 2. Get your User ID
Message [@userinfobot](https://t.me/userinfobot) → copy your numeric ID.

### 3. Configure
Edit `config.yaml` with your token, user ID, and printer IP.

### 4. Install & Run

**Requires Python 3.11–3.13.** Python 3.14 doesn't have pre-built aiohttp wheels yet — it will fail on Windows without Microsoft C++ Build Tools.

```bash
pip install -r requirements.txt
python bot.py
```

## Proxmox / LXC

```bash
apt update && apt install -y python3 python3-pip python3-venv
python3 -m venv /opt/printer-bot/venv
source /opt/printer-bot/venv/bin/activate
pip install -r requirements.txt
```

### Systemd service

`/etc/systemd/system/printer-bot.service`:
```ini
[Unit]
Description=Telegram Printer Bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/printer-bot
ExecStart=/opt/printer-bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable --now printer-bot
```

## Filament Runout

The bot auto-detects Klipper filament sensors (`filament_switch_sensor` and `filament_motion_sensor`). If the sensor reports filament gone while printing, you get an immediate notification. Make sure your sensor is configured in your Klipper `printer.cfg`.

## Printer Offline Detection

The monitor tracks connectivity to each printer. If a printer fails to respond for 3 consecutive poll cycles, it's marked offline and you get a notification. When it comes back, you get another notification. Toggle this in settings with the "Printer Offline" toggle.

## Security

- Only `allowed_user_ids` can interact
- All destructive actions require confirmation
- No exposed ports — outbound connections only

## AI Agent Skill

Includes a companion `printer-control` skill ([SKILL.md](printer-control/SKILL.md)) that lets AI agents (OpenClaw, Perplexity, etc.) control the printer through Moonraker. Full API reference, safety rules, and workflow examples.

## License

MIT — do whatever you want with it.

---

*Supervibecoded with ❤️ by AI. Humans only provided vibes.*
