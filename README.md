# 🖨️ Telegram Printer Bot

> **100% supervibecoded.** Not a single line of this project was written by a human. Not even one human touched this. The entire codebase — bot, translations, docs, even this README — was generated from scratch by AI ([Perplexity Computer](https://www.perplexity.ai/)). Pure vibes, zero keystrokes.

Full-featured Telegram bot for Klipper/Moonraker 3D printers — inline buttons everywhere, multi-language, auto-refresh, multi-printer support, offline-aware UI, live adjustments, bed mesh visualization, print history.

## Project Structure

```
telegram-printer-bot/
├── bot.py              # Entry point — registers handlers, starts polling
├── config.py           # Config loader/saver (single & multi-printer)
├── config.yaml         # Your configuration (edit this!)
├── api.py              # Moonraker API client (per-user printer routing)
├── lang.py             # Translations (EN / DE / RU / PL)
├── helpers.py          # Auth decorators, formatting, button builders
├── monitor.py          # Background monitor (notifications, milestones, offline tracking)
├── handlers/
│   ├── menu.py         # Main menu + router (offline-aware)
│   ├── status.py       # Status dashboard + auto-refresh + overrides
│   ├── temps.py        # Temperature control + presets
│   ├── files.py        # Paginated file browser
│   ├── control.py      # Print control (pause/resume/cancel)
│   ├── gcode.py        # GCode console
│   ├── macros.py       # Klipper macros (aliases + pagination)
│   ├── camera.py       # Camera snapshots
│   ├── system.py       # System info + restart
│   ├── estop.py        # Emergency stop
│   ├── settings.py     # Live settings menu
│   ├── printers.py     # Multi-printer selector
│   ├── adjust.py       # Speed / flow / fan / Z-offset adjustments
│   ├── bed_mesh.py     # Bed mesh visualization
│   └── history.py      # Print history browser
├── printer-control/
│   └── SKILL.md        # AI agent skill for printer control
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
- **Clock ETA** — shows estimated finish as wall-clock time (e.g. "Finish at: ~15:30")
- **Layer count** — current/total layers when available
- **Speed / Flow / Fan / Z-offset overrides** — shown when they differ from defaults
- **Auto-refresh**: tap the button and the status updates itself every 5 seconds
- Quick access to **Adjust**, **Print History**, and **Bed Mesh** right from the status page

### ⚫ Offline-Aware UI
When a printer is unreachable, the bot doesn't spam you with notifications. Instead:
- The **main menu** shows a stripped-down version with only Status, Settings, E-Stop, and printer switch
- The **status page** displays cached data with a "last seen X ago" timestamp
- All control handlers are **blocked** with a friendly offline message
- E-Stop always remains available regardless of online status

### 🔧 Live Adjustments
Adjust print parameters on the fly from the status page:
- **Speed override**: 50% / 75% / 100% / 125% / 150%
- **Flow override**: 75% / 100% / 110% / 120%
- **Fan speed**: 0% / 25% / 50% / 75% / 100%
- **Z-offset**: ±0.01mm / ±0.05mm / reset

### 📐 Bed Mesh Visualization
View your bed mesh probe data as a text grid right in Telegram:
- Profile name, grid dimensions
- Min/max range across the mesh
- Full probed matrix rendered as numbers

### 📜 Print History
Browse your last 50 completed prints (accessed from the status page):
- Status icons (✅ completed, ❌ error, 🟠 cancelled)
- Duration and date for each job
- Paginated with 10 entries per page

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
- Auto-discovers Klipper macros (hides internal `_` prefixed ones)
- **Human-readable aliases** — map ugly macro names to friendly labels in config
- **Pagination** — handles large macro lists with prev/next pages
- Run with confirmation

```yaml
macros:
  aliases:
    LOAD_FILAMENT: "🔄 Load Filament"
    UNLOAD_FILAMENT: "🔄 Unload Filament"
    PARK: "🅿️ Park Nozzle"
  per_page: 8
```

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
- **Always available** — even when printer is marked offline

### 🔔 Notifications
- Print complete / error / started / cancelled
- **Progress milestones** — get notified at 25%, 50%, 75% with ETA
- **Filament runout detection** (works with Klipper filament sensors)
- Temperature alerts
- All toggleable in settings

### ⚙️ Live Settings
- Toggle every notification type (including progress milestones)
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

## Security

- Only `allowed_user_ids` can interact
- All destructive actions require confirmation
- No exposed ports — outbound connections only

## AI Agent Skill

Includes a companion `printer-control` skill ([SKILL.md](printer-control/SKILL.md)) that lets AI agents (OpenClaw, Perplexity, etc.) control the printer through Moonraker. Full API reference, safety rules, and workflow examples.

## License

MIT — do whatever you want with it.

---

*Supervibecoded with ❤️ by AI. Not even one human touched this.*
