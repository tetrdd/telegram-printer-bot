---
name: printer-control
description: >-
  Control a 3D printer running Klipper firmware via the Moonraker HTTP API.
  Use when the user asks to check printer status, set temperatures, start or stop
  a print, send GCode, manage files, run macros, take camera snapshots, handle
  emergency stops, adjust speed/flow/fan/z-offset, view bed mesh, check print
  history, or perform any other printer-related operation.
  Keywords: 3D printer, Klipper, Moonraker, Elegoo Neptune, print, filament,
  extruder, bed, temperature, GCode, homing, leveling, firmware, z-offset,
  bed mesh, speed, flow, fan, history.
license: MIT
metadata:
  author: eddisch
  version: '2.0'
  printer: Elegoo Neptune (stock Klipper)
---

# Printer Control via Moonraker API

Control a Klipper-based 3D printer through its Moonraker HTTP API. This skill
covers every common operation: status monitoring, temperature control, print
management, file handling, GCode execution, macros, camera, system
administration, live adjustments, bed mesh, and print history.

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
- Adjust speed, flow, fan, or Z-offset during a print
- View bed mesh probe data
- Check print history (past jobs)

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
8. **Z-offset changes are cumulative with `Z_ADJUST`.** Small steps (0.01–0.05mm)
   are safe. Large jumps can crash the nozzle into the bed.

---

## API Reference

### 1. Printer Status

**Get full status snapshot** (temperatures, print stats, progress, speed/flow, fan):

```
GET /printer/objects/query?print_stats&display_status&virtual_sdcard&extruder&heater_bed&gcode_move&fan
```

Response path: `result.status`

Key fields in `result.status`:

| Object | Field | Description |
|---|---|---|
| `print_stats` | `state` | `standby`, `printing`, `paused`, `complete`, `error` |
| `print_stats` | `filename` | Currently loaded file |
| `print_stats` | `total_duration` | Total print time (seconds) |
| `print_stats` | `print_duration` | Actual printing time (seconds) |
| `print_stats` | `info.current_layer` | Current layer number |
| `print_stats` | `info.total_layer` | Total layer count |
| `display_status` | `progress` | 0.0 – 1.0 (multiply by 100 for %) |
| `virtual_sdcard` | `progress` | 0.0 – 1.0 |
| `extruder` | `temperature` | Current extruder temp (°C) |
| `extruder` | `target` | Target extruder temp (°C) |
| `heater_bed` | `temperature` | Current bed temp (°C) |
| `heater_bed` | `target` | Target bed temp (°C) |
| `gcode_move` | `speed_factor` | Speed override (0.0–1.0, multiply by 100 for %) |
| `gcode_move` | `extrude_factor` | Flow override (0.0–1.0, multiply by 100 for %) |
| `gcode_move` | `homing_origin` | Array [X, Y, Z, E] — Z is the Z-offset |
| `gcode_move` | `position` | Current position [X, Y, Z, E] |
| `gcode_move` | `speed` | Current speed (mm/s) |
| `fan` | `speed` | Part cooling fan speed (0.0–1.0) |

**List all printer objects** (discover available sensors, fans, etc.):

```
GET /printer/objects/list
```

Response path: `result.objects` → list of strings like `extruder`, `heater_bed`,
`gcode_move`, `fan`, `filament_switch_sensor runout_sensor`, `bed_mesh`, etc.

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

**Get file metadata** (estimated time, layer height, filament used):

```
GET /server/files/metadata?filename=<url-encoded-filename>
```

**Delete a file** ⚠️:

```
DELETE /server/files/gcodes/<url-encoded-filename>
```

---

### 5. GCode Execution

Send any GCode command:

```
POST /printer/gcode/script?script=<url-encoded-gcode>
```

Chain multiple commands with `%0A` (newline):

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
| `M84` | Disable stepper motors |
| `M106 S255` | Fan on full (0–255) |
| `M107` | Fan off |
| `FIRMWARE_RESTART` | Restart Klipper firmware (required after E-stop) |

---

### 6. Live Adjustments (during print)

**Speed override** (percentage, 100 = normal):

```
POST /printer/gcode/script?script=M220%20S<percent>
```

Example: `M220 S125` → 125% speed

**Flow override** (extrusion multiplier, 100 = normal):

```
POST /printer/gcode/script?script=M221%20S<percent>
```

Example: `M221 S110` → 110% flow

**Fan speed** (0–255):

```
POST /printer/gcode/script?script=M106%20S<value>
```

Example: `M106 S128` → ~50% fan. Formula: `value = 255 × percent / 100`

**Z-offset adjustment** (incremental, MOVE=1 applies immediately):

```
POST /printer/gcode/script?script=SET_GCODE_OFFSET%20Z_ADJUST%3D<offset>%20MOVE%3D1
```

Example: `SET_GCODE_OFFSET Z_ADJUST=0.05 MOVE=1` → raise nozzle 0.05mm
Example: `SET_GCODE_OFFSET Z_ADJUST=-0.02 MOVE=1` → lower nozzle 0.02mm

**Reset Z-offset to zero**:

```
POST /printer/gcode/script?script=SET_GCODE_OFFSET%20Z%3D0%20MOVE%3D1
```

⚠️ Z-offset adjustments are cumulative. Use small increments (0.01–0.05mm).

---

### 7. Bed Mesh

**Get current bed mesh data**:

```
GET /printer/objects/query?bed_mesh
```

Response path: `result.status.bed_mesh`

Key fields:
- `profile_name` — active mesh profile name
- `mesh_matrix` — interpolated mesh (higher resolution)
- `mesh_min`, `mesh_max` — probe area bounds [X, Y]

**Run bed mesh calibration** (Klipper macro):

```
POST /printer/gcode/script?script=BED_MESH_CALIBRATE
```

**Load a mesh profile**:

```
POST /printer/gcode/script?script=BED_MESH_PROFILE%20LOAD%3D<profile-name>
```

---

### 8. Print History

**Get print history** (requires Moonraker history component):

```
GET /server/history/list?limit=50&order=desc
```

Response path: `result.jobs` → array of job objects

Key fields per job:
- `filename` — printed file name
- `status` — `completed`, `error`, `cancelled`, `in_progress`
- `total_duration` — total job time (seconds)
- `print_duration` — actual printing time (seconds)
- `start_time` — Unix timestamp when job started
- `end_time` — Unix timestamp when job ended
- `filament_used` — filament consumed (mm)

---

### 9. Klipper Macros

Macros are defined in the printer's `printer.cfg`. Discover available macros by
listing printer objects and filtering for `gcode_macro` prefixes:

```
GET /printer/objects/list
```

Look for entries like `gcode_macro START_PRINT`, `gcode_macro END_PRINT`, etc.
Macros prefixed with `_` are internal and should be hidden from users.

Run a macro by sending it as GCode:

```
POST /printer/gcode/script?script=START_PRINT
```

Macros may accept parameters:

```
POST /printer/gcode/script?script=START_PRINT%20EXTRUDER=210%20BED=60
```

---

### 10. Camera

If a webcam is configured (e.g., crowsnest, ustreamer), the snapshot URL is
typically:

```
http://<printer-ip>/webcam/?action=snapshot
```

This returns a JPEG image. The exact URL depends on the user's camera setup.

---

### 11. Emergency Stop ⚠️

```
POST /printer/emergency_stop
```

Immediately kills the MCU. **All heaters off, motors off, print lost.**

To recover after an emergency stop:

```
POST /printer/firmware_restart
```

---

### 12. System Administration

**Server info** (Moonraker version, Klipper state, plugins):

```
GET /server/info
```

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

1. `GET /printer/objects/query?print_stats&display_status&virtual_sdcard&extruder&heater_bed&gcode_move&fan`
2. Extract: state, progress, temperatures, speed/flow overrides, fan, layers
3. Format: "Printing `filename` — 42% (layer 84/200), speed 100%, ETA ~15:30"

### Adjust print on the fly

1. Check printer is in `printing` state
2. Adjust speed: `M220 S125` (125%)
3. Adjust flow: `M221 S110` (110%)
4. Adjust fan: `M106 S128` (50%)
5. Fine-tune Z: `SET_GCODE_OFFSET Z_ADJUST=-0.02 MOVE=1`

### Start a print from scratch

1. Confirm printer is ready (Klippy state)
2. `GET /server/files/list?root=gcodes` → show files to user
3. User selects file → confirm choice
4. `GET /server/files/metadata?filename=...` → show estimated time, filament needed
5. Remind user to check filament
6. `POST /printer/print/start?filename=...`
7. Poll status periodically to report progress

### Handle an error state

1. `GET /server/info` → check `klippy_state`
2. If `error` or `shutdown`:
   - Report the error
   - Suggest: `POST /printer/firmware_restart`
3. After restart, check state again

### Check bed mesh quality

1. `GET /printer/objects/query?bed_mesh`
2. Extract `probed_matrix`, calculate min/max
3. If range > 0.5mm, suggest re-leveling the bed manually
4. Run `BED_MESH_CALIBRATE` to generate a new mesh

---

## Error Handling

- **Connection refused**: Moonraker is not running or wrong IP/port
- **HTTP 401/403**: API key is required. Set `X-Api-Key` header
- **Klippy state `error`/`shutdown`**: Firmware needs restart
- **Klippy state `startup`**: Klipper is still initializing, wait 10–30 seconds
- **Command rejected during print**: Some commands (like `G28`) are blocked while printing
