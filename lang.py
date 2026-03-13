"""
Multi-language support — English, German, Russian.
All UI strings live here. Access via t("key", lang).
"""

STRINGS = {
    # ── Main Menu ────────────────────────────────────────────────────────
    "menu.title": {
        "en": "🖨️ *Printer Control*\n\nChoose an option:",
        "de": "🖨️ *Druckersteuerung*\n\nWähle eine Option:",
        "ru": "🖨️ *Управление принтером*\n\nВыберите действие:",
    },
    "menu.status": {
        "en": "📊 Status",
        "de": "📊 Status",
        "ru": "📊 Статус",
    },
    "menu.temps": {
        "en": "🌡️ Temperatures",
        "de": "🌡️ Temperaturen",
        "ru": "🌡️ Температуры",
    },
    "menu.files": {
        "en": "📂 Files",
        "de": "📂 Dateien",
        "ru": "📂 Файлы",
    },
    "menu.print_ctrl": {
        "en": "🖨️ Print Control",
        "de": "🖨️ Drucksteuerung",
        "ru": "🖨️ Управление печатью",
    },
    "menu.macros": {
        "en": "⚡ Macros",
        "de": "⚡ Makros",
        "ru": "⚡ Макросы",
    },
    "menu.gcode": {
        "en": "💻 GCode Console",
        "de": "💻 GCode-Konsole",
        "ru": "💻 Консоль GCode",
    },
    "menu.camera": {
        "en": "📷 Camera",
        "de": "📷 Kamera",
        "ru": "📷 Камера",
    },
    "menu.system": {
        "en": "🔧 System",
        "de": "🔧 System",
        "ru": "🔧 Система",
    },
    "menu.settings": {
        "en": "⚙️ Settings",
        "de": "⚙️ Einstellungen",
        "ru": "⚙️ Настройки",
    },
    "menu.estop": {
        "en": "🚨 EMERGENCY STOP",
        "de": "🚨 NOT-HALT",
        "ru": "🚨 АВАРИЙНАЯ ОСТАНОВКА",
    },

    # ── Common ───────────────────────────────────────────────────────────
    "btn.back_menu": {
        "en": "🔙 Menu",
        "de": "🔙 Menü",
        "ru": "🔙 Меню",
    },
    "btn.refresh": {
        "en": "🔄 Refresh",
        "de": "🔄 Aktualisieren",
        "ru": "🔄 Обновить",
    },
    "btn.cancel": {
        "en": "❌ Cancel",
        "de": "❌ Abbrechen",
        "ru": "❌ Отмена",
    },
    "btn.snapshot": {
        "en": "📷 Snapshot",
        "de": "📷 Foto",
        "ru": "📷 Снимок",
    },
    "err.no_connect": {
        "en": "❌ Cannot connect to printer.",
        "de": "❌ Keine Verbindung zum Drucker.",
        "ru": "❌ Нет связи с принтером.",
    },

    # ── Status ───────────────────────────────────────────────────────────
    "status.title": {
        "en": "📊 *Status Dashboard*",
        "de": "📊 *Statusübersicht*",
        "ru": "📊 *Панель статуса*",
    },
    "status.state": {
        "en": "State",
        "de": "Zustand",
        "ru": "Состояние",
    },
    "status.file": {
        "en": "File",
        "de": "Datei",
        "ru": "Файл",
    },
    "status.progress": {
        "en": "Progress",
        "de": "Fortschritt",
        "ru": "Прогресс",
    },
    "status.duration": {
        "en": "Duration",
        "de": "Dauer",
        "ru": "Длительность",
    },
    "status.eta": {
        "en": "ETA",
        "de": "Restzeit",
        "ru": "Осталось",
    },
    "status.filament": {
        "en": "Filament",
        "de": "Filament",
        "ru": "Филамент",
    },
    "status.hotend": {
        "en": "Hotend",
        "de": "Hotend",
        "ru": "Хотэнд",
    },
    "status.bed": {
        "en": "Bed",
        "de": "Bett",
        "ru": "Стол",
    },
    "status.auto_on": {
        "en": "⏸️ Stop Auto-Refresh",
        "de": "⏸️ Auto-Refresh stoppen",
        "ru": "⏸️ Остановить обновление",
    },
    "status.auto_off": {
        "en": "▶️ Auto-Refresh (5s)",
        "de": "▶️ Auto-Refresh (5s)",
        "ru": "▶️ Авто-обновление (5с)",
    },

    # ── Printer States ───────────────────────────────────────────────────
    "state.ready": {
        "en": "🟢 Ready",
        "de": "🟢 Bereit",
        "ru": "🟢 Готов",
    },
    "state.standby": {
        "en": "🟢 Standby",
        "de": "🟢 Standby",
        "ru": "🟢 Ожидание",
    },
    "state.printing": {
        "en": "🖨️ Printing",
        "de": "🖨️ Druckt",
        "ru": "🖨️ Печатает",
    },
    "state.paused": {
        "en": "⏸️ Paused",
        "de": "⏸️ Pausiert",
        "ru": "⏸️ Пауза",
    },
    "state.error": {
        "en": "🔴 Error",
        "de": "🔴 Fehler",
        "ru": "🔴 Ошибка",
    },
    "state.shutdown": {
        "en": "⚫ Shutdown",
        "de": "⚫ Heruntergefahren",
        "ru": "⚫ Выключен",
    },
    "state.startup": {
        "en": "🟡 Starting",
        "de": "🟡 Startet",
        "ru": "🟡 Запуск",
    },
    "state.cancelled": {
        "en": "🟠 Cancelled",
        "de": "🟠 Abgebrochen",
        "ru": "🟠 Отменено",
    },
    "state.complete": {
        "en": "✅ Complete",
        "de": "✅ Fertig",
        "ru": "✅ Завершено",
    },

    # ── Temperatures ─────────────────────────────────────────────────────
    "temps.title": {
        "en": "🌡️ *Temperatures*",
        "de": "🌡️ *Temperaturen*",
        "ru": "🌡️ *Температуры*",
    },
    "temps.power": {
        "en": "Power",
        "de": "Leistung",
        "ru": "Мощность",
    },
    "temps.set_hotend": {
        "en": "🔥 Set Hotend",
        "de": "🔥 Hotend einstellen",
        "ru": "🔥 Установить хотэнд",
    },
    "temps.set_bed": {
        "en": "🛏️ Set Bed",
        "de": "🛏️ Bett einstellen",
        "ru": "🛏️ Установить стол",
    },
    "temps.cool_all": {
        "en": "❄️ Cool All",
        "de": "❄️ Alles kühlen",
        "ru": "❄️ Охладить всё",
    },
    "temps.cooled": {
        "en": "❄️ Cooling all heaters",
        "de": "❄️ Alle Heizer kühlen",
        "ru": "❄️ Охлаждение всех нагревателей",
    },
    "temps.hotend_title": {
        "en": "🔥 *Set Hotend Temperature*\n\nChoose a preset or enter custom:",
        "de": "🔥 *Hotend-Temperatur einstellen*\n\nWähle eine Vorlage oder gib einen Wert ein:",
        "ru": "🔥 *Температура хотэнда*\n\nВыберите пресет или введите вручную:",
    },
    "temps.bed_title": {
        "en": "🛏️ *Set Bed Temperature*\n\nChoose a preset or enter custom:",
        "de": "🛏️ *Bett-Temperatur einstellen*\n\nWähle eine Vorlage oder gib einen Wert ein:",
        "ru": "🛏️ *Температура стола*\n\nВыберите пресет или введите вручную:",
    },
    "temps.custom": {
        "en": "✏️ Custom",
        "de": "✏️ Manuell",
        "ru": "✏️ Вручную",
    },
    "temps.custom_hotend_prompt": {
        "en": "✏️ *Custom Hotend Temperature*\n\nType the temperature in °C (0-300):",
        "de": "✏️ *Hotend-Temperatur manuell*\n\nGib die Temperatur in °C ein (0-300):",
        "ru": "✏️ *Температура хотэнда вручную*\n\nВведите температуру в °C (0-300):",
    },
    "temps.custom_bed_prompt": {
        "en": "✏️ *Custom Bed Temperature*\n\nType the temperature in °C (0-120):",
        "de": "✏️ *Bett-Temperatur manuell*\n\nGib die Temperatur in °C ein (0-120):",
        "ru": "✏️ *Температура стола вручную*\n\nВведите температуру в °C (0-120):",
    },
    "temps.invalid_hotend": {
        "en": "❌ Enter a number between 0 and 300.",
        "de": "❌ Gib eine Zahl zwischen 0 und 300 ein.",
        "ru": "❌ Введите число от 0 до 300.",
    },
    "temps.invalid_bed": {
        "en": "❌ Enter a number between 0 and 120.",
        "de": "❌ Gib eine Zahl zwischen 0 und 120 ein.",
        "ru": "❌ Введите число от 0 до 120.",
    },
    "temps.back": {
        "en": "🔙 Temperatures",
        "de": "🔙 Temperaturen",
        "ru": "🔙 Температуры",
    },

    # ── Print Control ────────────────────────────────────────────────────
    "ctrl.title": {
        "en": "🖨️ *Print Control*",
        "de": "🖨️ *Drucksteuerung*",
        "ru": "🖨️ *Управление печатью*",
    },
    "ctrl.pause": {
        "en": "⏸️ Pause",
        "de": "⏸️ Pause",
        "ru": "⏸️ Пауза",
    },
    "ctrl.resume": {
        "en": "▶️ Resume",
        "de": "▶️ Fortsetzen",
        "ru": "▶️ Продолжить",
    },
    "ctrl.cancel": {
        "en": "🛑 Cancel",
        "de": "🛑 Abbrechen",
        "ru": "🛑 Отменить",
    },
    "ctrl.browse": {
        "en": "📂 Browse Files to Print",
        "de": "📂 Dateien zum Drucken",
        "ru": "📂 Выбрать файл для печати",
    },
    "ctrl.home": {
        "en": "🏠 Home All",
        "de": "🏠 Alle homen",
        "ru": "🏠 Домой",
    },
    "ctrl.motors_off": {
        "en": "🔓 Motors Off",
        "de": "🔓 Motoren aus",
        "ru": "🔓 Моторы выкл.",
    },
    "ctrl.cancel_confirm": {
        "en": "⚠️ *Cancel Print?*\n\nAre you sure you want to cancel the current print?",
        "de": "⚠️ *Druck abbrechen?*\n\nBist du sicher, dass du den aktuellen Druck abbrechen möchtest?",
        "ru": "⚠️ *Отменить печать?*\n\nВы уверены, что хотите отменить текущую печать?",
    },
    "ctrl.yes_cancel": {
        "en": "✅ Yes, cancel",
        "de": "✅ Ja, abbrechen",
        "ru": "✅ Да, отменить",
    },
    "ctrl.no_keep": {
        "en": "❌ No, keep printing",
        "de": "❌ Nein, weiterdrucken",
        "ru": "❌ Нет, продолжить",
    },
    "ctrl.paused": {
        "en": "⏸️ Paused",
        "de": "⏸️ Pausiert",
        "ru": "⏸️ Пауза",
    },
    "ctrl.resumed": {
        "en": "▶️ Resumed",
        "de": "▶️ Fortgesetzt",
        "ru": "▶️ Продолжено",
    },
    "ctrl.cancelled": {
        "en": "🛑 Cancelled",
        "de": "🛑 Abgebrochen",
        "ru": "🛑 Отменено",
    },
    "ctrl.homing": {
        "en": "🏠 Homing...",
        "de": "🏠 Home-Fahrt...",
        "ru": "🏠 Парковка...",
    },
    "ctrl.motors_disabled": {
        "en": "🔓 Motors off",
        "de": "🔓 Motoren aus",
        "ru": "🔓 Моторы выкл.",
    },

    # ── Files ────────────────────────────────────────────────────────────
    "files.title": {
        "en": "📂 *Files* — Page {page}/{total}",
        "de": "📂 *Dateien* — Seite {page}/{total}",
        "ru": "📂 *Файлы* — Стр. {page}/{total}",
    },
    "files.empty": {
        "en": "📂 No gcode files found.",
        "de": "📂 Keine GCode-Dateien gefunden.",
        "ru": "📂 Файлы GCode не найдены.",
    },
    "files.prev": {
        "en": "⬅️ Prev",
        "de": "⬅️ Zurück",
        "ru": "⬅️ Назад",
    },
    "files.next": {
        "en": "Next ➡️",
        "de": "Weiter ➡️",
        "ru": "Далее ➡️",
    },
    "files.by_date": {
        "en": "📅 By Date",
        "de": "📅 Nach Datum",
        "ru": "📅 По дате",
    },
    "files.by_name": {
        "en": "🔤 By Name",
        "de": "🔤 Nach Name",
        "ru": "🔤 По имени",
    },
    "files.info_title": {
        "en": "ℹ️ *File Info*",
        "de": "ℹ️ *Datei-Info*",
        "ru": "ℹ️ *Информация о файле*",
    },
    "files.name": {
        "en": "Name",
        "de": "Name",
        "ru": "Имя",
    },
    "files.size": {
        "en": "Size",
        "de": "Größe",
        "ru": "Размер",
    },
    "files.est_time": {
        "en": "Est. Time",
        "de": "Gesch. Zeit",
        "ru": "Расч. время",
    },
    "files.slicer": {
        "en": "Slicer",
        "de": "Slicer",
        "ru": "Слайсер",
    },
    "files.layer_height": {
        "en": "Layer Height",
        "de": "Schichthöhe",
        "ru": "Высота слоя",
    },
    "files.first_layer": {
        "en": "First Layer",
        "de": "Erste Schicht",
        "ru": "Первый слой",
    },
    "files.obj_height": {
        "en": "Object Height",
        "de": "Objekthöhe",
        "ru": "Высота объекта",
    },
    "files.filament_usage": {
        "en": "Filament",
        "de": "Filament",
        "ru": "Филамент",
    },
    "files.print_this": {
        "en": "🖨️ Print This",
        "de": "🖨️ Drucken",
        "ru": "🖨️ Печатать",
    },
    "files.delete": {
        "en": "🗑️ Delete",
        "de": "🗑️ Löschen",
        "ru": "🗑️ Удалить",
    },
    "files.back": {
        "en": "🔙 Files",
        "de": "🔙 Dateien",
        "ru": "🔙 Файлы",
    },
    "files.start_confirm": {
        "en": "🖨️ *Start Print?*\n\nFile: `{filename}`",
        "de": "🖨️ *Druck starten?*\n\nDatei: `{filename}`",
        "ru": "🖨️ *Начать печать?*\n\nФайл: `{filename}`",
    },
    "files.start_btn": {
        "en": "✅ Start",
        "de": "✅ Starten",
        "ru": "✅ Начать",
    },
    "files.started": {
        "en": "🖨️ Print started!",
        "de": "🖨️ Druck gestartet!",
        "ru": "🖨️ Печать начата!",
    },
    "files.delete_confirm": {
        "en": "🗑️ *Delete file?*\n\n`{filename}`\n\nThis cannot be undone.",
        "de": "🗑️ *Datei löschen?*\n\n`{filename}`\n\nDas kann nicht rückgängig gemacht werden.",
        "ru": "🗑️ *Удалить файл?*\n\n`{filename}`\n\nЭто действие нельзя отменить.",
    },
    "files.delete_btn": {
        "en": "✅ Delete",
        "de": "✅ Löschen",
        "ru": "✅ Удалить",
    },
    "files.keep_btn": {
        "en": "❌ Keep",
        "de": "❌ Behalten",
        "ru": "❌ Оставить",
    },
    "files.deleted": {
        "en": "🗑️ Deleted",
        "de": "🗑️ Gelöscht",
        "ru": "🗑️ Удалено",
    },

    # ── Camera ───────────────────────────────────────────────────────────
    "camera.title": {
        "en": "📷 *Camera*",
        "de": "📷 *Kamera*",
        "ru": "📷 *Камера*",
    },
    "camera.no_config": {
        "en": "📷 *Camera*\n\nNo camera configured.\n\nSet `snapshot_url` in config.yaml.",
        "de": "📷 *Kamera*\n\nKeine Kamera konfiguriert.\n\n`snapshot_url` in config.yaml setzen.",
        "ru": "📷 *Камера*\n\nКамера не настроена.\n\nУстановите `snapshot_url` в config.yaml.",
    },
    "camera.snapshot": {
        "en": "📷 Camera Snapshot",
        "de": "📷 Kamera-Foto",
        "ru": "📷 Снимок камеры",
    },
    "camera.new_snapshot": {
        "en": "🔄 New Snapshot",
        "de": "🔄 Neues Foto",
        "ru": "🔄 Новый снимок",
    },
    "camera.stream": {
        "en": "📹 Live Stream",
        "de": "📹 Livestream",
        "ru": "📹 Трансляция",
    },
    "camera.failed": {
        "en": "❌ Failed to get snapshot.",
        "de": "❌ Foto fehlgeschlagen.",
        "ru": "❌ Не удалось получить снимок.",
    },
    "camera.retry": {
        "en": "🔄 Retry",
        "de": "🔄 Nochmal",
        "ru": "🔄 Повторить",
    },
    "camera.capturing": {
        "en": "📷 Capturing...",
        "de": "📷 Aufnehmen...",
        "ru": "📷 Съёмка...",
    },

    # ── GCode Console ────────────────────────────────────────────────────
    "gcode.title": {
        "en": "💻 *GCode Console*\n\nQuick commands below, or type any GCode command:",
        "de": "💻 *GCode-Konsole*\n\nSchnellbefehle unten, oder tippe einen GCode-Befehl:",
        "ru": "💻 *Консоль GCode*\n\nБыстрые команды ниже, или введите любую команду GCode:",
    },
    "gcode.ok": {
        "en": "✅ `{cmd}` — OK",
        "de": "✅ `{cmd}` — OK",
        "ru": "✅ `{cmd}` — OK",
    },
    "gcode.fail": {
        "en": "❌ `{cmd}` — Failed",
        "de": "❌ `{cmd}` — Fehlgeschlagen",
        "ru": "❌ `{cmd}` — Ошибка",
    },
    "gcode.another": {
        "en": "Send another command or press Menu:",
        "de": "Sende einen weiteren Befehl oder drücke Menü:",
        "ru": "Отправьте ещё команду или нажмите Меню:",
    },

    # ── Macros ───────────────────────────────────────────────────────────
    "macros.title": {
        "en": "⚡ *Macros* ({count} found)\n\nTap to run:",
        "de": "⚡ *Makros* ({count} gefunden)\n\nTippe zum Ausführen:",
        "ru": "⚡ *Макросы* ({count} найдено)\n\nНажмите для запуска:",
    },
    "macros.empty": {
        "en": "⚡ *Macros*\n\nNo macros found.",
        "de": "⚡ *Makros*\n\nKeine Makros gefunden.",
        "ru": "⚡ *Макросы*\n\nМакросы не найдены.",
    },
    "macros.run_confirm": {
        "en": "⚡ Run macro *{name}*?",
        "de": "⚡ Makro *{name}* ausführen?",
        "ru": "⚡ Запустить макрос *{name}*?",
    },
    "macros.run_btn": {
        "en": "✅ Run",
        "de": "✅ Ausführen",
        "ru": "✅ Запустить",
    },

    # ── System ───────────────────────────────────────────────────────────
    "system.title": {
        "en": "🔧 *System Info*",
        "de": "🔧 *Systeminfo*",
        "ru": "🔧 *Информация о системе*",
    },
    "system.fw_restart": {
        "en": "🔁 Restart Firmware",
        "de": "🔁 Firmware neustarten",
        "ru": "🔁 Перезагрузить прошивку",
    },
    "system.host_restart": {
        "en": "🔁 Restart Host",
        "de": "🔁 Host neustarten",
        "ru": "🔁 Перезагрузить хост",
    },
    "system.fw_confirm": {
        "en": "🔁 *Firmware Restart?*\n\nThis will restart the printer firmware.",
        "de": "🔁 *Firmware neustarten?*\n\nDie Drucker-Firmware wird neu gestartet.",
        "ru": "🔁 *Перезагрузить прошивку?*\n\nПрошивка принтера будет перезагружена.",
    },
    "system.host_confirm": {
        "en": "🔁 *Host Reboot?*\n\nThis will reboot the printer host system.",
        "de": "🔁 *Host neustarten?*\n\nDas Host-System wird neu gestartet.",
        "ru": "🔁 *Перезагрузить хост?*\n\nХост-система принтера будет перезагружена.",
    },

    # ── Emergency Stop ───────────────────────────────────────────────────
    "estop.confirm": {
        "en": "🚨 *EMERGENCY STOP*\n\nThis will IMMEDIATELY halt the printer.\nYou will need to restart firmware after.\n\nAre you sure?",
        "de": "🚨 *NOT-HALT*\n\nDer Drucker wird SOFORT gestoppt.\nDanach muss die Firmware neu gestartet werden.\n\nBist du sicher?",
        "ru": "🚨 *АВАРИЙНАЯ ОСТАНОВКА*\n\nПринтер будет НЕМЕДЛЕННО остановлен.\nПосле этого потребуется перезагрузка прошивки.\n\nВы уверены?",
    },
    "estop.yes": {
        "en": "🚨 YES, STOP NOW",
        "de": "🚨 JA, SOFORT STOPPEN",
        "ru": "🚨 ДА, ОСТАНОВИТЬ",
    },
    "estop.done": {
        "en": "🚨 *EMERGENCY STOP EXECUTED*\n\nRestart firmware to continue.",
        "de": "🚨 *NOT-HALT AUSGEFÜHRT*\n\nFirmware neustarten um fortzufahren.",
        "ru": "🚨 *АВАРИЙНАЯ ОСТАНОВКА ВЫПОЛНЕНА*\n\nПерезагрузите прошивку для продолжения.",
    },
    "estop.failed": {
        "en": "❌ E-Stop failed! Check connection.",
        "de": "❌ Not-Halt fehlgeschlagen! Verbindung prüfen.",
        "ru": "❌ Аварийная остановка не удалась! Проверьте соединение.",
    },

    # ── Settings ─────────────────────────────────────────────────────────
    "settings.title": {
        "en": "⚙️ *Settings*\n\nTap to toggle or cycle values:",
        "de": "⚙️ *Einstellungen*\n\nTippe zum Umschalten:",
        "ru": "⚙️ *Настройки*\n\nНажмите для переключения:",
    },
    "settings.print_complete": {
        "en": "Print Complete",
        "de": "Druck fertig",
        "ru": "Печать завершена",
    },
    "settings.print_error": {
        "en": "Print Error",
        "de": "Druckfehler",
        "ru": "Ошибка печати",
    },
    "settings.print_start": {
        "en": "Print Start",
        "de": "Druck gestartet",
        "ru": "Начало печати",
    },
    "settings.print_cancelled": {
        "en": "Print Cancelled",
        "de": "Druck abgebrochen",
        "ru": "Печать отменена",
    },
    "settings.filament_runout": {
        "en": "Filament Runout",
        "de": "Filament leer",
        "ru": "Конец филамента",
    },
    "settings.temp_alert": {
        "en": "Temp Alert",
        "de": "Temp-Alarm",
        "ru": "Тревога темп.",
    },
    "settings.estop_menu": {
        "en": "E-Stop in Menu",
        "de": "Not-Halt im Menü",
        "ru": "Авар. стоп в меню",
    },
    "settings.estop_confirm": {
        "en": "E-Stop Confirmation",
        "de": "Not-Halt Bestätigung",
        "ru": "Подтв. авар. стопа",
    },
    "settings.poll": {
        "en": "Poll",
        "de": "Abfrage",
        "ru": "Опрос",
    },
    "settings.files_per_page": {
        "en": "Files/page",
        "de": "Dateien/Seite",
        "ru": "Файлов/стр.",
    },
    "settings.language": {
        "en": "🌐 Language: English",
        "de": "🌐 Sprache: Deutsch",
        "ru": "🌐 Язык: Русский",
    },

    # ── Notifications ────────────────────────────────────────────────────
    "notif.complete": {
        "en": "✅ *Print Complete!*\n\nFile: `{filename}`\nDuration: {duration}\nFilament: {filament} m",
        "de": "✅ *Druck fertig!*\n\nDatei: `{filename}`\nDauer: {duration}\nFilament: {filament} m",
        "ru": "✅ *Печать завершена!*\n\nФайл: `{filename}`\nДлительность: {duration}\nФиламент: {filament} м",
    },
    "notif.error": {
        "en": "🔴 *Print Error!*\n\nFile: `{filename}`\nError: {error}",
        "de": "🔴 *Druckfehler!*\n\nDatei: `{filename}`\nFehler: {error}",
        "ru": "🔴 *Ошибка печати!*\n\nФайл: `{filename}`\nОшибка: {error}",
    },
    "notif.started": {
        "en": "🖨️ *Print Started*\n\nFile: `{filename}`",
        "de": "🖨️ *Druck gestartet*\n\nDatei: `{filename}`",
        "ru": "🖨️ *Печать начата*\n\nФайл: `{filename}`",
    },
    "notif.cancelled": {
        "en": "🟠 *Print Cancelled*\n\nFile: `{filename}`",
        "de": "🟠 *Druck abgebrochen*\n\nDatei: `{filename}`",
        "ru": "🟠 *Печать отменена*\n\nФайл: `{filename}`",
    },
    "notif.temp_alert": {
        "en": "🌡️ *Temp Alert!*\n\nHotend: {temp}°C (threshold: {threshold}°C)",
        "de": "🌡️ *Temperatur-Alarm!*\n\nHotend: {temp}°C (Schwelle: {threshold}°C)",
        "ru": "🌡️ *Тревога температуры!*\n\nХотэнд: {temp}°C (порог: {threshold}°C)",
    },
    "notif.filament_runout": {
        "en": "🔴 *Filament Runout Detected!*\n\nThe filament sensor triggered — printer should be paused.\nCheck the printer immediately!",
        "de": "🔴 *Filament leer!*\n\nDer Filament-Sensor hat ausgelöst — Drucker sollte pausiert sein.\nPrüfe den Drucker sofort!",
        "ru": "🔴 *Обнаружен конец филамента!*\n\nСработал датчик филамента — принтер должен быть на паузе.\nПроверьте принтер немедленно!",
    },

    # ── Generic ──────────────────────────────────────────────────────────
    "generic.failed": {
        "en": "❌ Failed",
        "de": "❌ Fehlgeschlagen",
        "ru": "❌ Ошибка",
    },
    "generic.done": {
        "en": "✅ Done",
        "de": "✅ Fertig",
        "ru": "✅ Готово",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Get a translated string. Falls back to English."""
    entry = STRINGS.get(key)
    if not entry:
        return f"[{key}]"
    return entry.get(lang, entry.get("en", f"[{key}]"))
