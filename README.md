# 🖨️ Telegram Printer Bot

> **100% vibecoded.** Not a single line of this project was written by a human. The entire codebase — bot, Mini App, translations, docs, even this README — was generated from scratch by AI ([Perplexity Computer](https://www.perplexity.ai/)). No human fingers touched any code, CSS, or config. Pure vibes, zero keystrokes.

Full-featured Telegram bot for Klipper/Moonraker 3D printers — inline buttons everywhere, multi-language, auto-refresh.

## Project Structure

```
telegram-printer-bot/
├── bot.py              # Entry point — registers handlers, starts polling
├── config.py           # Config loader/saver
├── config.yaml         # Your configuration (edit this!)
├── api.py              # Moonraker API client
├── lang.py             # Translations (EN / DE / RU)
├── helpers.py          # Auth decorators, formatting, button builders
├── monitor.py          # Background monitor (notifications, filament runout)
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
│   └── settings.py     # Live settings menu
└── requirements.txt
```

## Features

### 🌐 Multi-Language
Switch between English, Deutsch, and Русский right from the settings menu. Every button, message, and notification is translated.

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
- Temperature alerts

### ⚙️ Live Settings
- Toggle every notification type
- Change language, poll interval, files per page
- E-Stop visibility and confirmation
- All saved to config.yaml instantly

## Telegram Mini App (Dashboard)

The `webapp/` folder contains a full web dashboard that runs as a Telegram Mini App — right inside Telegram, no browser needed.

### How it works

The Mini App connects directly to your Moonraker API and gives you:
- Live status dashboard (auto-refreshes every 3s)
- Temperature gauges with heater power bars
- Print progress with ETA
- Full control (pause/resume/cancel, home, motors off)
- Temperature presets (PLA, PETG, ABS, TPU)
- GCode console with history
- File browser with tap-to-print
- Camera snapshots
- Emergency stop
- Matches Telegram's dark theme automatically

### Setting it up

1. **Host `webapp/` on HTTPS** — Telegram requires HTTPS. Options:
   - **GitHub Pages** (free): push the `webapp/` folder to a repo, enable Pages
   - **Cloudflare Pages** (free): connect your repo or drag-drop the folder
   - **Your own server**: serve via nginx/caddy with Let's Encrypt

2. **Edit `webapp/app.js`** — Change `DEFAULT_MOONRAKER` to your printer's IP:
   ```js
   const DEFAULT_MOONRAKER = 'http://192.168.1.100:7125';
   ```
   Or pass it via URL hash: `https://your-site.com/printer-app/#moonraker=http://192.168.1.100:7125`

3. **Configure in BotFather** — message [@BotFather](https://t.me/BotFather):

   **Option A: Menu button** (appears in bottom-left of the chat)
   ```
   /setmenubutton → select your bot → enter your HTTPS URL → set title "Dashboard"
   ```

   **Option B: Main Mini App** (adds a "Launch app" button on the bot's profile)
   ```
   /mybots → select your bot → Bot Settings → Configure Mini App → Enable Mini App → enter URL
   ```

   **Option C: Direct link app**
   ```
   /newapp → select your bot → enter URL → choose a short name
   ```
   This creates a `t.me/yourbot/appname` link you can share anywhere.

4. **CORS**: Make sure Moonraker allows requests from your webapp domain. In `moonraker.conf`:
   ```
   [authorization]
   cors_domains:
       https://your-site.com
   ```

## Setup (Bot)

### Overview

### 1. Create your Telegram Bot
Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy token.

### 2. Get your User ID
Message [@userinfobot](https://t.me/userinfobot) → copy your numeric ID.

### 3. Configure
Edit `config.yaml` with your token, user ID, and printer IP.

### 4. Run
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

*Supervibecoded with ❤️ by AI. Humans only provided vibes.*
