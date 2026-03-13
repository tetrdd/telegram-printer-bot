---
name: printer-control
description: >-
  Control a 3D printer running Klipper firmware via the Moonraker HTTP API.
  Use when the user asks to check printer status, set temperatures, start or stop
  a print, send GCode, manage files, run macros, take camera snapshots, handle
  emergency stops, or perform any other printer-related operation.
  Keywords: 3D printer, Klipper, Moonraker, Elegoo Neptune, print, filament,
  extruder, bed, temperature, GCode, homing, leveling, firmware.
license: MIT
metadata:
  author: eddisch
  version: '1.0'
  printer: Elegoo Neptune (stock Klipper)
---

# Printer Control via Moonraker API

Control a Klipper-based 3D printer through its Moonraker HTTP API. This skill
covers every common operation: status monitoring, temperature control, print
management, file handling, GCode execution, macros, camera, and system
administration.

## When to Use This Skill

Use this skill when the user asks you to:

- Check printer status, temperatures, or print progress
- Start, pause, resume, or cancel a print
- Set or adjust extruder / bed temperatures
- Home axes, run bed leveling, or move the toolhead
- Send raw GCode commands
- List, inspect, or delete print files
- Run Klipper macros
- Take a camera snapshot
- Emergency-stop the printer
- Reboot / restart the printer firmware or host
- Diagnose printer issues (connectivity, errors, warnings)

## Connection Setup

The Moonraker API runs on the printer's host machine (Raspberry Pi, SBC, or
Proxmox LXC). You need:

| Setting | Example |
|---|---|
| Base URL | `http://192.168.1.100:7125` |
| API Key (optional) | Set in Moonraker config if authentication is enabled |

All endpoints below are relative to the base URL. If an API key is configured,
include the header `X-Api-Key: <key>` on every request.

**Timeout**: Use a 10-second timeout for normal requests, 15 seconds for camera
snapshots.

---

## Safety Rules (CRITICAL)

1. **NEVER send `EMERGENCY_STOP`, temperature changes, or movement commands
   without explicit user confirmation.** Always describe what you are about to
   do and wait for approval.
2. **NEVER set temperatures above safe limits.** Extruder max: 260 °C (check
   printer config). Bed max: 110 °C. If the user requests higher, warn them
   and refuse unless they explicitly override.
3. **NEVER start a print without confirming the filename with the user.**
   Printing the wrong file wastes filament and time.
4. **NEVER cancel a running print without confirmation.** A cancelled print
   cannot be resumed.
5. **Check printer state before destructive actions.** Don't try to pause when
   not printing. Don't home axes while a print is running.
6. **Emergency stop is irreversible.** It kills the MCU immediately. The user
   must run `FIRMWARE_RESTART` to recover. Only use in genuine emergencies.
7. **Filament awareness**: Before starting a print, remind the user to verify
   filament is loaded if you cannot confirm it programmatically.

---

## API Reference

### 1. Printer Status

**Get full status snapshot** (temperatures, print stats, progress):

```
GET /printer/objects/query?print_stats&display_status&virtual_sdcard&extruder&heater_bed
```

Response path: `result.status`

Key fields in `result.status`:

| Object | Field | Description |
|---|---|---|
| `print_stats` | `state` | `standby`, `printing`, `paused`, `complete`, `error` |
| `print_stats` | `filename` | Currently loaded file |
| `print_stats` | `total_duration` | Total print time (seconds) |
| `print_stats` | `print_duration` | Actual printing time (seconds) |
| `display_status` | `progress` | 0.0 – 1.0 (multiply by 100 for %) |
| `display_status` | `message` | Display message (if any) |
| `virtual_sdcard` | `file_position` | Current byte position in file |
| `virtual_sdcard` | `progress` | 0.0 – 1.0 |
| `extruder` | `temperature` | Current extruder temp (°C) |
| `extruder` | `target` | Target extruder temp (°C) |
| `heater_bed` | `temperature` | Current bed temp (°C) |
| `heater_bed` | `target` | Target bed temp (°C) |

**List all printer objects** (discover available sensors, fans, etc.):

```
GET /printer/objects/list
```

Response path: `result.objects` → list of strings like `extruder`, `heater_bed`,
`gcode_move`, `fan`, `filament_switch_sensor runout_sensor`, etc.

**Query specific objects** (you can query any object from the list above):

```
GET /printer/objects/query?gcode_move&fan&filament_switch_sensor%20runout_sensor
```

Useful objects:
- `gcode_move` → `position` (X, Y, Z, E), `speed`, `speed_factor`
- `fan` → `speed` (0.0–1.0)
- `toolhead` → `position`, `homed_axes`, `max_velocity`
- `filament_switch_sensor runout_sensor` → `filament_detected` (bool), `enabled`

---

### 2. Temperature Control

Set temperatures via GCode (see Section 5 for how to send):

| Command | Description |
|---|---|
| `M104 S210` | Set extruder to 210 °C (no wait) |
| `M109 S210` | Set extruder to 210 °C and wait until reached |
| `M140 S60` | Set bed to 60 °C (no wait) |
| `M190 S60` | Set bed to 60 °C and wait |
| `M104 S0` | Turn off extruder |
| `M140 S0` | Turn off bed |

Common presets:
- **PLA**: Extruder 200–210 °C, Bed 60 °C
- **PETG**: Extruder 230–240 °C, Bed 80 °C
- **ABS**: Extruder 240–250 °C, Bed 100–110 °C
- **TPU**: Extruder 220–230 °C, Bed 50 °C

---

### 3. Print Management

**Start a print** (file must exist in `gcodes/`):

```
POST /printer/print/start?filename=<url-encoded-filename>
```

**Pause print**:

```
POST /printer/print/pause
```

**Resume print**:

```
POST /printer/print/resume
```

**Cancel print** ⚠️ Irreversible:

```
POST /printer/print/cancel
```

---

### 4. File Management

**List all gcode files**:

```
GET /server/files/list?root=gcodes
```

Response: `result` → array of objects with `path`, `modified`, `size`,
`print_start_time`, `job_id`, etc.

**Get file metadata** (estimated time, layer height, filament used):

```
GET /server/files/metadata?filename=<url-encoded-filename>
```

Response fields: `estimated_time`, `layer_height`, `first_layer_height`,
`object_height`, `filament_total`, `slicer`, `slicer_version`, etc.

**Delete a file** ⚠️:

```
DELETE /server/files/gcodes/<url-encoded-filename>
```

**Upload a file** (multipart form data):

```
POST /server/files/upload
Content-Type: multipart/form-data
Body: file=<file>, root=gcodes
```

---

### 5. GCode Execution

Send any GCode command:

```
POST /printer/gcode/script?script=<url-encoded-gcode>
```

You can chain multiple commands with `%0A` (newline):

```
POST /printer/gcode/script?script=G28%0AG1%20X100%20Y100%20F3000
```

Common GCode commands:

| Command | Description |
|---|---|
| `G28` | Home all axes |
| `G28 X Y` | Home X and Y only |
| `G28 Z` | Home Z only |
| `BED_MESH_CALIBRATE` | Run automatic bed leveling (Klipper macro) |
| `G1 X100 Y100 F3000` | Move toolhead to X=100 Y=100 at 3000mm/min |
| `G1 Z50 F600` | Move Z to 50mm |
| `G1 E10 F300` | Extrude 10mm of filament |
| `G1 E-10 F300` | Retract 10mm of filament |
| `M84` | Disable stepper motors |
| `M106 S255` | Fan on full (0–255) |
| `M107` | Fan off |
| `M400` | Wait for all moves to finish |
| `SAVE_CONFIG` | Save Klipper config changes (triggers restart) |
| `FIRMWARE_RESTART` | Restart Klipper firmware (required after E-stop) |

---

### 6. Klipper Macros

Macros are defined in the printer's `printer.cfg`. Discover available macros by
listing printer objects and filtering for `gcode_macro` prefixes:

```
GET /printer/objects/list
```

Look for entries like `gcode_macro START_PRINT`, `gcode_macro END_PRINT`, etc.

Run a macro by sending it as GCode:

```
POST /printer/gcode/script?script=START_PRINT
```

Macros may accept parameters:

```
POST /printer/gcode/script?script=START_PRINT%20EXTRUDER=210%20BED=60
```

---

### 7. Camera

If a webcam is configured (e.g., crowsnest, ustreamer), the snapshot URL is
typically:

```
http://<printer-ip>/webcam/?action=snapshot
```

This returns a JPEG image. The exact URL depends on the user's camera setup.

---

### 8. Emergency Stop ⚠️

```
POST /printer/emergency_stop
```

Immediately kills the MCU. **All heaters off, motors off, print lost.**

To recover after an emergency stop:

```
POST /printer/firmware_restart
```

---

### 9. System Administration

**Server info** (Moonraker version, Klipper state, plugins):

```
GET /server/info
```

Response: `result` with `klippy_state` (`ready`, `error`, `shutdown`, `startup`),
`moonraker_version`, `components`, `failed_components`, etc.

**System info** (host hardware, OS, CPU, memory):

```
GET /machine/system_info
```

**Process stats** (CPU %, memory, uptime):

```
GET /machine/proc_stats
```

**Reboot the host** ⚠️:

```
POST /machine/reboot
```

**Shutdown the host** ⚠️:

```
POST /machine/shutdown
```

**Restart Moonraker service**:

```
POST /server/restart
```

**Firmware restart** (Klipper only, not the host):

```
POST /printer/firmware_restart
```

---

## Common Workflows

### Check if printer is ready

1. `GET /server/info` → check `klippy_state == "ready"`
2. If not ready, report the state and suggest firmware restart

### Monitor a running print

1. `GET /printer/objects/query?print_stats&display_status&virtual_sdcard&extruder&heater_bed`
2. Extract: `print_stats.state`, `display_status.progress`, temperatures
3. Format: "Printing `filename` — 42% complete, extruder 210°C, bed 60°C, ETA ~25 min"
4. ETA calculation: `estimated_time × (1 - progress) / progress` (from file metadata)

### Start a print from scratch

1. Confirm printer is ready (Klippy state)
2. `GET /server/files/list?root=gcodes` → show files to user
3. User selects file → confirm choice
4. `GET /server/files/metadata?filename=...` → show estimated time, filament needed
5. Remind user to check filament
6. `POST /printer/print/start?filename=...`
7. Poll status periodically to report progress

### Preheat for a material

1. Ask user which material (PLA/PETG/ABS/TPU)
2. Send temperature GCodes (no wait variants for faster response):
   - `M104 S210` and `M140 S60` for PLA
3. Poll temperatures to report progress

### Handle an error state

1. `GET /server/info` → check `klippy_state`
2. If `error` or `shutdown`:
   - Report the error
   - Suggest: `POST /printer/firmware_restart`
3. After restart, check state again

### Filament runout detected

1. Query `filament_switch_sensor runout_sensor` → `filament_detected: false`
2. Alert user immediately
3. Suggest pausing print if printing
4. Guide user through filament change:
   - Heat extruder to printing temp
   - `G1 E-50 F300` (retract old filament)
   - User loads new filament manually
   - `G1 E50 F300` (prime new filament)
   - Resume print

---

## Error Handling

- **Connection refused**: Moonraker is not running or wrong IP/port. Check the
  base URL.
- **HTTP 401/403**: API key is required. Set `X-Api-Key` header.
- **Klippy state `error`/`shutdown`**: Firmware needs restart. Use
  `/printer/firmware_restart`.
- **Klippy state `startup`**: Klipper is still initializing. Wait 10–30 seconds
  and retry.
- **Command rejected during print**: Some commands (like `G28`) are blocked while
  printing. Check `print_stats.state` first.

---

## Examples

### Example 1: User asks "What's my printer doing?"

```
GET http://192.168.1.100:7125/printer/objects/query?print_stats&display_status&virtual_sdcard&extruder&heater_bed
```

Parse response and reply:
> Your printer is printing `benchy.gcode` — 67% done. Extruder: 210°C (target 210°C), Bed: 60°C (target 60°C). Estimated ~18 minutes remaining.

### Example 2: User asks "Preheat for PETG"

After confirmation, send:

```
POST http://192.168.1.100:7125/printer/gcode/script?script=M104%20S235%0AM140%20S80
```

Reply:
> Preheating — extruder target set to 235°C, bed to 80°C. I'll let you know when temps are reached.

### Example 3: User asks "Cancel the print"

1. Confirm: "Are you sure you want to cancel? This cannot be undone."
2. After user confirms:

```
POST http://192.168.1.100:7125/printer/print/cancel
```

3. Optionally turn off heaters:

```
POST http://192.168.1.100:7125/printer/gcode/script?script=M104%20S0%0AM140%20S0
```

### Example 4: User asks "Emergency stop!"

This is urgent — still confirm quickly but act fast:

```
POST http://192.168.1.100:7125/printer/emergency_stop
```

Reply:
> Emergency stop executed. All heaters and motors are off. When safe, I can run a firmware restart to bring the printer back online.
