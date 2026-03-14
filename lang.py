"""
Multi-language support — English, German, Russian, Polish.
All UI strings live here. Access via t("key", lang).
"""
from __future__ import annotations

STRINGS = {
    # ── Main Menu ────────────────────────────────────────────────────────
    "menu.title": {
        "en": "🖨️ *Printer Control*\n\nChoose an option:",
        "de": "🖨️ *Druckersteuerung*\n\nWähle eine Option:",
        "ru": "🖨️ *Управление принтером*\n\nВыберите действие:",
        "pl": "🖨️ *Sterowanie drukarką*\n\nWybierz opcję:",
    },
    "menu.status": {
        "en": "📊 Status",
        "de": "📊 Status",
        "ru": "📊 Статус",
        "pl": "📊 Status",
    },
    "menu.temps": {
        "en": "🌡️ Temperatures",
        "de": "🌡️ Temperaturen",
        "ru": "🌡️ Температуры",
        "pl": "🌡️ Temperatury",
    },
    "menu.files": {
        "en": "📂 Files",
        "de": "📂 Dateien",
        "ru": "📂 Файлы",
        "pl": "📂 Pliki",
    },
    "menu.print_ctrl": {
        "en": "🖨️ Print Control",
        "de": "🖨️ Drucksteuerung",
        "ru": "🖨️ Управление печатью",
        "pl": "🖨️ Sterowanie drukiem",
    },
    "menu.macros": {
        "en": "⚡ Macros",
        "de": "⚡ Makros",
        "ru": "⚡ Макросы",
        "pl": "⚡ Makra",
    },
    "menu.gcode": {
        "en": "💻 GCode Console",
        "de": "💻 GCode-Konsole",
        "ru": "💻 Консоль GCode",
        "pl": "💻 Konsola GCode",
    },
    "menu.camera": {
        "en": "📷 Camera",
        "de": "📷 Kamera",
        "ru": "📷 Камера",
        "pl": "📷 Kamera",
    },
    "menu.system": {
        "en": "🔧 System",
        "de": "🔧 System",
        "ru": "🔧 Система",
        "pl": "🔧 System",
    },
    "menu.settings": {
        "en": "⚙️ Settings",
        "de": "⚙️ Einstellungen",
        "ru": "⚙️ Настройки",
        "pl": "⚙️ Ustawienia",
    },
    "menu.estop": {
        "en": "🚨 EMERGENCY STOP",
        "de": "🚨 NOT-HALT",
        "ru": "🚨 АВАРИЙНАЯ ОСТАНОВКА",
        "pl": "🚨 ZATRZYMANIE AWARYJNE",
    },
    "menu.switch_printer": {
        "en": "Switch Printer",
        "de": "Drucker wechseln",
        "ru": "Сменить принтер",
        "pl": "Zmień drukarkę",
    },
    "menu.adjust": {
        "en": "🔧 Adjust",
        "de": "🔧 Anpassen",
        "ru": "🔧 Настройка",
        "pl": "🔧 Dostosuj",
    },
    "menu.bed_mesh": {
        "en": "📐 Bed Mesh",
        "de": "📐 Bett-Mesh",
        "ru": "📐 Сетка стола",
        "pl": "📐 Siatka stołu",
    },

    # ── Common ───────────────────────────────────────────────────────────
    "btn.back_menu": {
        "en": "🔙 Menu",
        "de": "🔙 Menü",
        "ru": "🔙 Меню",
        "pl": "🔙 Menu",
    },
    "btn.refresh": {
        "en": "🔄 Refresh",
        "de": "🔄 Aktualisieren",
        "ru": "🔄 Обновить",
        "pl": "🔄 Odśwież",
    },
    "btn.cancel": {
        "en": "❌ Cancel",
        "de": "❌ Abbrechen",
        "ru": "❌ Отмена",
        "pl": "❌ Anuluj",
    },
    "btn.snapshot": {
        "en": "📷 Snapshot",
        "de": "📷 Foto",
        "ru": "📷 Снимок",
        "pl": "📷 Zdjęcie",
    },
    "err.no_connect": {
        "en": "❌ Cannot connect to printer.",
        "de": "❌ Keine Verbindung zum Drucker.",
        "ru": "❌ Нет связи с принтером.",
        "pl": "❌ Brak połączenia z drukarką.",
    },

    # ── Offline UI ───────────────────────────────────────────────────────
    "offline.blocked": {
        "en": "⛔ Printer is offline. This feature is unavailable.",
        "de": "⛔ Drucker ist offline. Diese Funktion ist nicht verfügbar.",
        "ru": "⛔ Принтер не в сети. Функция недоступна.",
        "pl": "⛔ Drukarka jest offline. Ta funkcja jest niedostępna.",
    },
    "offline.title": {
        "en": "⚫ *Printer Offline*",
        "de": "⚫ *Drucker Offline*",
        "ru": "⚫ *Принтер не в сети*",
        "pl": "⚫ *Drukarka offline*",
    },
    "offline.cached": {
        "en": "📋 Last known data (cached):",
        "de": "📋 Letzte bekannte Daten (gecacht):",
        "ru": "📋 Последние известные данные (кэш):",
        "pl": "📋 Ostatnie znane dane (cache):",
    },
    "offline.last_seen": {
        "en": "Last seen: {time}",
        "de": "Zuletzt gesehen: {time}",
        "ru": "Последний раз в сети: {time}",
        "pl": "Ostatnio widziana: {time}",
    },

    # ── Status ───────────────────────────────────────────────────────────
    "status.title": {
        "en": "📊 *Status Dashboard*",
        "de": "📊 *Statusübersicht*",
        "ru": "📊 *Панель статуса*",
        "pl": "📊 *Panel statusu*",
    },
    "status.state": {
        "en": "State",
        "de": "Zustand",
        "ru": "Состояние",
        "pl": "Stan",
    },
    "status.file": {
        "en": "File",
        "de": "Datei",
        "ru": "Файл",
        "pl": "Plik",
    },
    "status.progress": {
        "en": "Progress",
        "de": "Fortschritt",
        "ru": "Прогресс",
        "pl": "Postęp",
    },
    "status.duration": {
        "en": "Duration",
        "de": "Dauer",
        "ru": "Длительность",
        "pl": "Czas trwania",
    },
    "status.eta": {
        "en": "ETA",
        "de": "Restzeit",
        "ru": "Осталось",
        "pl": "Pozostało",
    },
    "status.filament": {
        "en": "Filament",
        "de": "Filament",
        "ru": "Филамент",
        "pl": "Filament",
    },
    "status.hotend": {
        "en": "Hotend",
        "de": "Hotend",
        "ru": "Хотэнд",
        "pl": "Hotend",
    },
    "status.bed": {
        "en": "Bed",
        "de": "Bett",
        "ru": "Стол",
        "pl": "Stół",
    },
    "status.auto_on": {
        "en": "⏸️ Stop Auto-Refresh",
        "de": "⏸️ Auto-Refresh stoppen",
        "ru": "⏸️ Остановить обновление",
        "pl": "⏸️ Zatrzymaj odświeżanie",
    },
    "status.auto_off": {
        "en": "▶️ Auto-Refresh (5s)",
        "de": "▶️ Auto-Refresh (5s)",
        "ru": "▶️ Авто-обновление (5с)",
        "pl": "▶️ Auto-odświeżanie (5s)",
    },
    "status.speed": {
        "en": "Speed",
        "de": "Geschwindigkeit",
        "ru": "Скорость",
        "pl": "Prędkość",
    },
    "status.flow": {
        "en": "Flow",
        "de": "Fluss",
        "ru": "Поток",
        "pl": "Przepływ",
    },
    "status.fan": {
        "en": "Fan",
        "de": "Lüfter",
        "ru": "Вентилятор",
        "pl": "Wentylator",
    },
    "status.clock_eta": {
        "en": "Finish at",
        "de": "Fertig um",
        "ru": "Готово к",
        "pl": "Gotowe o",
    },
    "status.layers": {
        "en": "Layers",
        "de": "Schichten",
        "ru": "Слои",
        "pl": "Warstwy",
    },

    # ── Printer States ───────────────────────────────────────────────────
    "state.ready": {
        "en": "🟢 Ready",
        "de": "🟢 Bereit",
        "ru": "🟢 Готов",
        "pl": "🟢 Gotowa",
    },
    "state.standby": {
        "en": "🟢 Standby",
        "de": "🟢 Standby",
        "ru": "🟢 Ожидание",
        "pl": "🟢 Czuwanie",
    },
    "state.printing": {
        "en": "🖨️ Printing",
        "de": "🖨️ Druckt",
        "ru": "🖨️ Печатает",
        "pl": "🖨️ Drukuje",
    },
    "state.paused": {
        "en": "⏸️ Paused",
        "de": "⏸️ Pausiert",
        "ru": "⏸️ Пауза",
        "pl": "⏸️ Wstrzymano",
    },
    "state.error": {
        "en": "🔴 Error",
        "de": "🔴 Fehler",
        "ru": "🔴 Ошибка",
        "pl": "🔴 Błąd",
    },
    "state.shutdown": {
        "en": "⚫ Shutdown",
        "de": "⚫ Heruntergefahren",
        "ru": "⚫ Выключен",
        "pl": "⚫ Wyłączona",
    },
    "state.startup": {
        "en": "🟡 Starting",
        "de": "🟡 Startet",
        "ru": "🟡 Запуск",
        "pl": "🟡 Uruchamianie",
    },
    "state.cancelled": {
        "en": "🟠 Cancelled",
        "de": "🟠 Abgebrochen",
        "ru": "🟠 Отменено",
        "pl": "🟠 Anulowano",
    },
    "state.complete": {
        "en": "✅ Complete",
        "de": "✅ Fertig",
        "ru": "✅ Завершено",
        "pl": "✅ Ukończono",
    },

    # ── Temperatures ─────────────────────────────────────────────────────
    "temps.title": {
        "en": "🌡️ *Temperatures*",
        "de": "🌡️ *Temperaturen*",
        "ru": "🌡️ *Температуры*",
        "pl": "🌡️ *Temperatury*",
    },
    "temps.power": {
        "en": "Power",
        "de": "Leistung",
        "ru": "Мощность",
        "pl": "Moc",
    },
    "temps.set_hotend": {
        "en": "🔥 Set Hotend",
        "de": "🔥 Hotend einstellen",
        "ru": "🔥 Установить хотэнд",
        "pl": "🔥 Ustaw hotend",
    },
    "temps.set_bed": {
        "en": "🛏️ Set Bed",
        "de": "🛏️ Bett einstellen",
        "ru": "🛏️ Установить стол",
        "pl": "🛏️ Ustaw stół",
    },
    "temps.cool_all": {
        "en": "❄️ Cool All",
        "de": "❄️ Alles kühlen",
        "ru": "❄️ Охладить всё",
        "pl": "❄️ Schłodź wszystko",
    },
    "temps.cooled": {
        "en": "❄️ Cooling all heaters",
        "de": "❄️ Alle Heizer kühlen",
        "ru": "❄️ Охлаждение всех нагревателей",
        "pl": "❄️ Chłodzenie wszystkich grzałek",
    },
    "temps.hotend_title": {
        "en": "🔥 *Set Hotend Temperature*\n\nChoose a preset or enter custom:",
        "de": "🔥 *Hotend-Temperatur einstellen*\n\nWähle eine Vorlage oder gib einen Wert ein:",
        "ru": "🔥 *Температура хотэнда*\n\nВыберите пресет или введите вручную:",
        "pl": "🔥 *Temperatura hotendu*\n\nWybierz preset lub wpisz ręcznie:",
    },
    "temps.bed_title": {
        "en": "🛏️ *Set Bed Temperature*\n\nChoose a preset or enter custom:",
        "de": "🛏️ *Bett-Temperatur einstellen*\n\nWähle eine Vorlage oder gib einen Wert ein:",
        "ru": "🛏️ *Температура стола*\n\nВыберите пресет или введите вручную:",
        "pl": "🛏️ *Temperatura stołu*\n\nWybierz preset lub wpisz ręcznie:",
    },
    "temps.custom": {
        "en": "✏️ Custom",
        "de": "✏️ Manuell",
        "ru": "✏️ Вручную",
        "pl": "✏️ Ręcznie",
    },
    "temps.custom_hotend_prompt": {
        "en": "✏️ *Custom Hotend Temperature*\n\nType the temperature in °C (0-300):",
        "de": "✏️ *Hotend-Temperatur manuell*\n\nGib die Temperatur in °C ein (0-300):",
        "ru": "✏️ *Температура хотэнда вручную*\n\nВведите температуру в °C (0-300):",
        "pl": "✏️ *Temperatura hotendu ręcznie*\n\nWpisz temperaturę w °C (0-300):",
    },
    "temps.custom_bed_prompt": {
        "en": "✏️ *Custom Bed Temperature*\n\nType the temperature in °C (0-120):",
        "de": "✏️ *Bett-Temperatur manuell*\n\nGib die Temperatur in °C ein (0-120):",
        "ru": "✏️ *Температура стола вручную*\n\nВведите температуру в °C (0-120):",
        "pl": "✏️ *Temperatura stołu ręcznie*\n\nWpisz temperaturę w °C (0-120):",
    },
    "temps.invalid_hotend": {
        "en": "❌ Enter a number between 0 and 300.",
        "de": "❌ Gib eine Zahl zwischen 0 und 300 ein.",
        "ru": "❌ Введите число от 0 до 300.",
        "pl": "❌ Wpisz liczbę od 0 do 300.",
    },
    "temps.invalid_bed": {
        "en": "❌ Enter a number between 0 and 120.",
        "de": "❌ Gib eine Zahl zwischen 0 und 120 ein.",
        "ru": "❌ Введите число от 0 до 120.",
        "pl": "❌ Wpisz liczbę od 0 do 120.",
    },
    "temps.back": {
        "en": "🔙 Temperatures",
        "de": "🔙 Temperaturen",
        "ru": "🔙 Температуры",
        "pl": "🔙 Temperatury",
    },

    # ── Print Control ────────────────────────────────────────────────────
    "ctrl.title": {
        "en": "🖨️ *Print Control*",
        "de": "🖨️ *Drucksteuerung*",
        "ru": "🖨️ *Управление печатью*",
        "pl": "🖨️ *Sterowanie drukiem*",
    },
    "ctrl.pause": {
        "en": "⏸️ Pause",
        "de": "⏸️ Pause",
        "ru": "⏸️ Пауза",
        "pl": "⏸️ Pauza",
    },
    "ctrl.resume": {
        "en": "▶️ Resume",
        "de": "▶️ Fortsetzen",
        "ru": "▶️ Продолжить",
        "pl": "▶️ Wznów",
    },
    "ctrl.cancel": {
        "en": "🛑 Cancel",
        "de": "🛑 Abbrechen",
        "ru": "🛑 Отменить",
        "pl": "🛑 Anuluj",
    },
    "ctrl.browse": {
        "en": "📂 Browse Files to Print",
        "de": "📂 Dateien zum Drucken",
        "ru": "📂 Выбрать файл для печати",
        "pl": "📂 Przeglądaj pliki do druku",
    },
    "ctrl.home": {
        "en": "🏠 Home All",
        "de": "🏠 Alle homen",
        "ru": "🏠 Домой",
        "pl": "🏠 Bazowanie",
    },
    "ctrl.motors_off": {
        "en": "🔓 Motors Off",
        "de": "🔓 Motoren aus",
        "ru": "🔓 Моторы выкл.",
        "pl": "🔓 Silniki wył.",
    },
    "ctrl.cancel_confirm": {
        "en": "⚠️ *Cancel Print?*\n\nAre you sure you want to cancel the current print?",
        "de": "⚠️ *Druck abbrechen?*\n\nBist du sicher, dass du den aktuellen Druck abbrechen möchtest?",
        "ru": "⚠️ *Отменить печать?*\n\nВы уверены, что хотите отменить текущую печать?",
        "pl": "⚠️ *Anulować druk?*\n\nCzy na pewno chcesz anulować bieżący druk?",
    },
    "ctrl.yes_cancel": {
        "en": "✅ Yes, cancel",
        "de": "✅ Ja, abbrechen",
        "ru": "✅ Да, отменить",
        "pl": "✅ Tak, anuluj",
    },
    "ctrl.no_keep": {
        "en": "❌ No, keep printing",
        "de": "❌ Nein, weiterdrucken",
        "ru": "❌ Нет, продолжить",
        "pl": "❌ Nie, kontynuuj druk",
    },
    "ctrl.paused": {
        "en": "⏸️ Paused",
        "de": "⏸️ Pausiert",
        "ru": "⏸️ Пауза",
        "pl": "⏸️ Wstrzymano",
    },
    "ctrl.resumed": {
        "en": "▶️ Resumed",
        "de": "▶️ Fortgesetzt",
        "ru": "▶️ Продолжено",
        "pl": "▶️ Wznowiono",
    },
    "ctrl.cancelled": {
        "en": "🛑 Cancelled",
        "de": "🛑 Abgebrochen",
        "ru": "🛑 Отменено",
        "pl": "🛑 Anulowano",
    },
    "ctrl.homing": {
        "en": "🏠 Homing...",
        "de": "🏠 Home-Fahrt...",
        "ru": "🏠 Парковка...",
        "pl": "🏠 Bazowanie...",
    },
    "ctrl.motors_disabled": {
        "en": "🔓 Motors off",
        "de": "🔓 Motoren aus",
        "ru": "🔓 Моторы выкл.",
        "pl": "🔓 Silniki wył.",
    },

    # ── Files ────────────────────────────────────────────────────────────
    "files.title": {
        "en": "📂 *Files* — Page {page}/{total}",
        "de": "📂 *Dateien* — Seite {page}/{total}",
        "ru": "📂 *Файлы* — Стр. {page}/{total}",
        "pl": "📂 *Pliki* — Strona {page}/{total}",
    },
    "files.empty": {
        "en": "📂 No gcode files found.",
        "de": "📂 Keine GCode-Dateien gefunden.",
        "ru": "📂 Файлы GCode не найдены.",
        "pl": "📂 Nie znaleziono plików GCode.",
    },
    "files.prev": {
        "en": "⬅️ Prev",
        "de": "⬅️ Zurück",
        "ru": "⬅️ Назад",
        "pl": "⬅️ Wstecz",
    },
    "files.next": {
        "en": "Next ➡️",
        "de": "Weiter ➡️",
        "ru": "Далее ➡️",
        "pl": "Dalej ➡️",
    },
    "files.by_date": {
        "en": "📅 By Date",
        "de": "📅 Nach Datum",
        "ru": "📅 По дате",
        "pl": "📅 Wg daty",
    },
    "files.by_name": {
        "en": "🔤 By Name",
        "de": "🔤 Nach Name",
        "ru": "🔤 По имени",
        "pl": "🔤 Wg nazwy",
    },
    "files.info_title": {
        "en": "ℹ️ *File Info*",
        "de": "ℹ️ *Datei-Info*",
        "ru": "ℹ️ *Информация о файле*",
        "pl": "ℹ️ *Info o pliku*",
    },
    "files.name": {
        "en": "Name",
        "de": "Name",
        "ru": "Имя",
        "pl": "Nazwa",
    },
    "files.size": {
        "en": "Size",
        "de": "Größe",
        "ru": "Размер",
        "pl": "Rozmiar",
    },
    "files.est_time": {
        "en": "Est. Time",
        "de": "Gesch. Zeit",
        "ru": "Расч. время",
        "pl": "Szac. czas",
    },
    "files.slicer": {
        "en": "Slicer",
        "de": "Slicer",
        "ru": "Слайсер",
        "pl": "Slicer",
    },
    "files.layer_height": {
        "en": "Layer Height",
        "de": "Schichthöhe",
        "ru": "Высота слоя",
        "pl": "Wysokość warstwy",
    },
    "files.first_layer": {
        "en": "First Layer",
        "de": "Erste Schicht",
        "ru": "Первый слой",
        "pl": "Pierwsza warstwa",
    },
    "files.obj_height": {
        "en": "Object Height",
        "de": "Objekthöhe",
        "ru": "Высота объекта",
        "pl": "Wysokość obiektu",
    },
    "files.filament_usage": {
        "en": "Filament",
        "de": "Filament",
        "ru": "Филамент",
        "pl": "Filament",
    },
    "files.print_this": {
        "en": "🖨️ Print This",
        "de": "🖨️ Drucken",
        "ru": "🖨️ Печатать",
        "pl": "🖨️ Drukuj",
    },
    "files.delete": {
        "en": "🗑️ Delete",
        "de": "🗑️ Löschen",
        "ru": "🗑️ Удалить",
        "pl": "🗑️ Usuń",
    },
    "files.back": {
        "en": "🔙 Files",
        "de": "🔙 Dateien",
        "ru": "🔙 Файлы",
        "pl": "🔙 Pliki",
    },
    "files.start_confirm": {
        "en": "🖨️ *Start Print?*\n\nFile: `{filename}`",
        "de": "🖨️ *Druck starten?*\n\nDatei: `{filename}`",
        "ru": "🖨️ *Начать печать?*\n\nФайл: `{filename}`",
        "pl": "🖨️ *Rozpocząć druk?*\n\nPlik: `{filename}`",
    },
    "files.start_btn": {
        "en": "✅ Start",
        "de": "✅ Starten",
        "ru": "✅ Начать",
        "pl": "✅ Start",
    },
    "files.started": {
        "en": "🖨️ Print started!",
        "de": "🖨️ Druck gestartet!",
        "ru": "🖨️ Печать начата!",
        "pl": "🖨️ Druk rozpoczęty!",
    },
    "files.delete_confirm": {
        "en": "🗑️ *Delete file?*\n\n`{filename}`\n\nThis cannot be undone.",
        "de": "🗑️ *Datei löschen?*\n\n`{filename}`\n\nDas kann nicht rückgängig gemacht werden.",
        "ru": "🗑️ *Удалить файл?*\n\n`{filename}`\n\nЭто действие нельзя отменить.",
        "pl": "🗑️ *Usunąć plik?*\n\n`{filename}`\n\nTej operacji nie można cofnąć.",
    },
    "files.delete_btn": {
        "en": "✅ Delete",
        "de": "✅ Löschen",
        "ru": "✅ Удалить",
        "pl": "✅ Usuń",
    },
    "files.keep_btn": {
        "en": "❌ Keep",
        "de": "❌ Behalten",
        "ru": "❌ Оставить",
        "pl": "❌ Zachowaj",
    },
    "files.deleted": {
        "en": "🗑️ Deleted",
        "de": "🗑️ Gelöscht",
        "ru": "🗑️ Удалено",
        "pl": "🗑️ Usunięto",
    },

    # ── Camera ───────────────────────────────────────────────────────────
    "camera.title": {
        "en": "📷 *Camera*",
        "de": "📷 *Kamera*",
        "ru": "📷 *Камера*",
        "pl": "📷 *Kamera*",
    },
    "camera.no_config": {
        "en": "📷 *Camera*\n\nNo camera configured.\n\nSet `snapshot_url` in config.yaml.",
        "de": "📷 *Kamera*\n\nKeine Kamera konfiguriert.\n\n`snapshot_url` in config.yaml setzen.",
        "ru": "📷 *Камера*\n\nКамера не настроена.\n\nУстановите `snapshot_url` в config.yaml.",
        "pl": "📷 *Kamera*\n\nKamera nie skonfigurowana.\n\nUstaw `snapshot_url` w config.yaml.",
    },
    "camera.snapshot": {
        "en": "📷 Camera Snapshot",
        "de": "📷 Kamera-Foto",
        "ru": "📷 Снимок камеры",
        "pl": "📷 Zdjęcie z kamery",
    },
    "camera.new_snapshot": {
        "en": "🔄 New Snapshot",
        "de": "🔄 Neues Foto",
        "ru": "🔄 Новый снимок",
        "pl": "🔄 Nowe zdjęcie",
    },
    "camera.stream": {
        "en": "📹 Live Stream",
        "de": "📹 Livestream",
        "ru": "📹 Трансляция",
        "pl": "📹 Transmisja na żywo",
    },
    "camera.failed": {
        "en": "❌ Failed to get snapshot.",
        "de": "❌ Foto fehlgeschlagen.",
        "ru": "❌ Не удалось получить снимок.",
        "pl": "❌ Nie udało się zrobić zdjęcia.",
    },
    "camera.retry": {
        "en": "🔄 Retry",
        "de": "🔄 Nochmal",
        "ru": "🔄 Повторить",
        "pl": "🔄 Ponów",
    },
    "camera.capturing": {
        "en": "📷 Capturing...",
        "de": "📷 Aufnehmen...",
        "ru": "📷 Съёмка...",
        "pl": "📷 Robię zdjęcie...",
    },

    # ── GCode Console ────────────────────────────────────────────────────
    "gcode.title": {
        "en": "💻 *GCode Console*\n\nQuick commands below, or type any GCode command:",
        "de": "💻 *GCode-Konsole*\n\nSchnellbefehle unten, oder tippe einen GCode-Befehl:",
        "ru": "💻 *Консоль GCode*\n\nБыстрые команды ниже, или введите любую команду GCode:",
        "pl": "💻 *Konsola GCode*\n\nSzybkie polecenia poniżej lub wpisz dowolne polecenie GCode:",
    },
    "gcode.ok": {
        "en": "✅ `{cmd}` — OK",
        "de": "✅ `{cmd}` — OK",
        "ru": "✅ `{cmd}` — OK",
        "pl": "✅ `{cmd}` — OK",
    },
    "gcode.fail": {
        "en": "❌ `{cmd}` — Failed",
        "de": "❌ `{cmd}` — Fehlgeschlagen",
        "ru": "❌ `{cmd}` — Ошибка",
        "pl": "❌ `{cmd}` — Błąd",
    },
    "gcode.another": {
        "en": "Send another command or press Menu:",
        "de": "Sende einen weiteren Befehl oder drücke Menü:",
        "ru": "Отправьте ещё команду или нажмите Меню:",
        "pl": "Wyślij kolejne polecenie lub naciśnij Menu:",
    },

    # ── Macros ───────────────────────────────────────────────────────────
    "macros.title": {
        "en": "⚡ *Macros* ({count} found)\n\nTap to run:",
        "de": "⚡ *Makros* ({count} gefunden)\n\nTippe zum Ausführen:",
        "ru": "⚡ *Макросы* ({count} найдено)\n\nНажмите для запуска:",
        "pl": "⚡ *Makra* ({count} znaleziono)\n\nKliknij, aby uruchomić:",
    },
    "macros.empty": {
        "en": "⚡ *Macros*\n\nNo macros found.",
        "de": "⚡ *Makros*\n\nKeine Makros gefunden.",
        "ru": "⚡ *Макросы*\n\nМакросы не найдены.",
        "pl": "⚡ *Makra*\n\nNie znaleziono makr.",
    },
    "macros.run_confirm": {
        "en": "⚡ Run macro *{name}*?",
        "de": "⚡ Makro *{name}* ausführen?",
        "ru": "⚡ Запустить макрос *{name}*?",
        "pl": "⚡ Uruchomić makro *{name}*?",
    },
    "macros.run_btn": {
        "en": "✅ Run",
        "de": "✅ Ausführen",
        "ru": "✅ Запустить",
        "pl": "✅ Uruchom",
    },
    "macros.page": {
        "en": "⚡ *Macros* — Page {page}/{total} ({count} total)",
        "de": "⚡ *Makros* — Seite {page}/{total} ({count} gesamt)",
        "ru": "⚡ *Макросы* — Стр. {page}/{total} ({count} всего)",
        "pl": "⚡ *Makra* — Strona {page}/{total} ({count} łącznie)",
    },

    # ── Adjust controls ──────────────────────────────────────────────────
    "adjust.title": {
        "en": "🔧 *Adjustments*",
        "de": "🔧 *Anpassungen*",
        "ru": "🔧 *Настройки печати*",
        "pl": "🔧 *Dostosowania*",
    },
    "adjust.speed": {
        "en": "⚡ Speed: {val}%",
        "de": "⚡ Geschwindigkeit: {val}%",
        "ru": "⚡ Скорость: {val}%",
        "pl": "⚡ Prędkość: {val}%",
    },
    "adjust.flow": {
        "en": "💧 Flow: {val}%",
        "de": "💧 Fluss: {val}%",
        "ru": "💧 Поток: {val}%",
        "pl": "💧 Przepływ: {val}%",
    },
    "adjust.fan": {
        "en": "🌀 Fan: {val}%",
        "de": "🌀 Lüfter: {val}%",
        "ru": "🌀 Вентилятор: {val}%",
        "pl": "🌀 Wentylator: {val}%",
    },
    "adjust.z_offset": {
        "en": "📐 Z-Offset: {val}mm",
        "de": "📐 Z-Offset: {val}mm",
        "ru": "📐 Z-смещение: {val}мм",
        "pl": "📐 Z-Offset: {val}mm",
    },
    "adjust.btn": {
        "en": "🔧 Adjust",
        "de": "🔧 Anpassen",
        "ru": "🔧 Настройка",
        "pl": "🔧 Dostosuj",
    },
    "adjust.speed_set": {
        "en": "Speed set to {val}%",
        "de": "Geschwindigkeit auf {val}% gesetzt",
        "ru": "Скорость установлена: {val}%",
        "pl": "Prędkość ustawiona na {val}%",
    },
    "adjust.flow_set": {
        "en": "Flow set to {val}%",
        "de": "Fluss auf {val}% gesetzt",
        "ru": "Поток установлен: {val}%",
        "pl": "Przepływ ustawiony na {val}%",
    },
    "adjust.fan_set": {
        "en": "Fan set to {val}%",
        "de": "Lüfter auf {val}% gesetzt",
        "ru": "Вентилятор установлен: {val}%",
        "pl": "Wentylator ustawiony na {val}%",
    },
    "adjust.z_up": {
        "en": "📐 Z+{step}",
        "de": "📐 Z+{step}",
        "ru": "📐 Z+{step}",
        "pl": "📐 Z+{step}",
    },
    "adjust.z_down": {
        "en": "📐 Z-{step}",
        "de": "📐 Z-{step}",
        "ru": "📐 Z-{step}",
        "pl": "📐 Z-{step}",
    },
    "adjust.z_reset": {
        "en": "📐 Z Reset",
        "de": "📐 Z Zurücksetzen",
        "ru": "📐 Z Сброс",
        "pl": "📐 Z Reset",
    },

    # ── Bed Mesh ─────────────────────────────────────────────────────────
    "mesh.title": {
        "en": "📐 *Bed Mesh*",
        "de": "📐 *Bett-Mesh*",
        "ru": "📐 *Сетка стола*",
        "pl": "📐 *Siatka stołu*",
    },
    "mesh.no_data": {
        "en": "No bed mesh data available.",
        "de": "Keine Bett-Mesh-Daten verfügbar.",
        "ru": "Данные сетки стола недоступны.",
        "pl": "Brak danych siatki stołu.",
    },
    "mesh.name": {
        "en": "Profile: {name}",
        "de": "Profil: {name}",
        "ru": "Профиль: {name}",
        "pl": "Profil: {name}",
    },
    "mesh.range": {
        "en": "Range: {min}mm — {max}mm",
        "de": "Bereich: {min}mm — {max}mm",
        "ru": "Диапазон: {min}мм — {max}мм",
        "pl": "Zakres: {min}mm — {max}mm",
    },
    "mesh.btn": {
        "en": "📐 Bed Mesh",
        "de": "📐 Bett-Mesh",
        "ru": "📐 Сетка стола",
        "pl": "📐 Siatka stołu",
    },

    # ── History ──────────────────────────────────────────────────────────
    "history.title": {
        "en": "📜 *Print History*",
        "de": "📜 *Druckverlauf*",
        "ru": "📜 *История печати*",
        "pl": "📜 *Historia druku*",
    },
    "history.empty": {
        "en": "No print history available.",
        "de": "Kein Druckverlauf vorhanden.",
        "ru": "История печати недоступна.",
        "pl": "Brak historii druku.",
    },
    "history.entry": {
        "en": "{status} `{filename}`\n  ⏱️ {duration} | {date}",
        "de": "{status} `{filename}`\n  ⏱️ {duration} | {date}",
        "ru": "{status} `{filename}`\n  ⏱️ {duration} | {date}",
        "pl": "{status} `{filename}`\n  ⏱️ {duration} | {date}",
    },
    "history.btn": {
        "en": "📜 History",
        "de": "📜 Verlauf",
        "ru": "📜 История",
        "pl": "📜 Historia",
    },

    # ── Notifications ────────────────────────────────────────────────────
    "notif.complete": {
        "en": "✅ *Print Complete!*\n\nFile: `{filename}`\nDuration: {duration}\nFilament: {filament} m",
        "de": "✅ *Druck fertig!*\n\nDatei: `{filename}`\nDauer: {duration}\nFilament: {filament} m",
        "ru": "✅ *Печать завершена!*\n\nФайл: `{filename}`\nДлительность: {duration}\nФиламент: {filament} м",
        "pl": "✅ *Druk ukończony!*\n\nPlik: `{filename}`\nCzas: {duration}\nFilament: {filament} m",
    },
    "notif.error": {
        "en": "🔴 *Print Error!*\n\nFile: `{filename}`\nError: {error}",
        "de": "🔴 *Druckfehler!*\n\nDatei: `{filename}`\nFehler: {error}",
        "ru": "🔴 *Ошибка печати!*\n\nФайл: `{filename}`\nОшибка: {error}",
        "pl": "🔴 *Błąd druku!*\n\nPlik: `{filename}`\nBłąd: {error}",
    },
    "notif.started": {
        "en": "🖨️ *Print Started*\n\nFile: `{filename}`",
        "de": "🖨️ *Druck gestartet*\n\nDatei: `{filename}`",
        "ru": "🖨️ *Печать начата*\n\nФайл: `{filename}`",
        "pl": "🖨️ *Druk rozpoczęty*\n\nPlik: `{filename}`",
    },
    "notif.cancelled": {
        "en": "🟠 *Print Cancelled*\n\nFile: `{filename}`",
        "de": "🟠 *Druck abgebrochen*\n\nDatei: `{filename}`",
        "ru": "🟠 *Печать отменена*\n\nФайл: `{filename}`",
        "pl": "🟠 *Druk anulowany*\n\nPlik: `{filename}`",
    },
    "notif.temp_alert": {
        "en": "🌡️ *Temp Alert!*\n\nHotend: {temp}°C (threshold: {threshold}°C)",
        "de": "🌡️ *Temperatur-Alarm!*\n\nHotend: {temp}°C (Schwelle: {threshold}°C)",
        "ru": "🌡️ *Тревога температуры!*\n\nХотэнд: {temp}°C (порог: {threshold}°C)",
        "pl": "🌡️ *Alarm temperatury!*\n\nHotend: {temp}°C (próg: {threshold}°C)",
    },
    "notif.filament_runout": {
        "en": "🔴 *Filament Runout Detected!*\n\nThe filament sensor triggered — printer should be paused.\nCheck the printer immediately!",
        "de": "🔴 *Filament leer!*\n\nDer Filament-Sensor hat ausgelöst — Drucker sollte pausiert sein.\nPrüfe den Drucker sofort!",
        "ru": "🔴 *Обнаружен конец филамента!*\n\nСработал датчик филамента — принтер должен быть на паузе.\nПроверьте принтер немедленно!",
        "pl": "🔴 *Wykryto brak filamentu!*\n\nCzujnik filamentu się uruchomił — drukarka powinna być wstrzymana.\nSprawdź drukarkę natychmiast!",
    },
    "notif.milestone": {
        "en": "📊 *Print Progress: {pct}%*\n\nFile: `{filename}`",
        "de": "📊 *Druckfortschritt: {pct}%*\n\nDatei: `{filename}`",
        "ru": "📊 *Прогресс печати: {pct}%*\n\nФайл: `{filename}`",
        "pl": "📊 *Postęp druku: {pct}%*\n\nPlik: `{filename}`",
    },

    # ── Printers (multi-printer) ─────────────────────────────────────────
    "printers.title": {
        "en": "🖨️ *Select Printer*\n\nTap to switch:",
        "de": "🖨️ *Drucker auswählen*\n\nTippe zum Wechseln:",
        "ru": "🖨️ *Выбор принтера*\n\nНажмите для переключения:",
        "pl": "🖨️ *Wybierz drukarkę*\n\nKliknij, aby przełączyć:",
    },
    "printers.overview": {
        "en": "🖨️ *All Printers*",
        "de": "🖨️ *Alle Drucker*",
        "ru": "🖨️ *Все принтеры*",
        "pl": "🖨️ *Wszystkie drukarki*",
    },

    # ── System ───────────────────────────────────────────────────────────
    "system.title": {
        "en": "🔧 *System Info*",
        "de": "🔧 *Systeminfo*",
        "ru": "🔧 *Информация о системе*",
        "pl": "🔧 *Informacje o systemie*",
    },
    "system.fw_restart": {
        "en": "🔁 Restart Firmware",
        "de": "🔁 Firmware neustarten",
        "ru": "🔁 Перезагрузить прошивку",
        "pl": "🔁 Restart firmware",
    },
    "system.host_restart": {
        "en": "🔁 Restart Host",
        "de": "🔁 Host neustarten",
        "ru": "🔁 Перезагрузить хост",
        "pl": "🔁 Restart hosta",
    },
    "system.fw_confirm": {
        "en": "🔁 *Firmware Restart?*\n\nThis will restart the printer firmware.",
        "de": "🔁 *Firmware neustarten?*\n\nDie Drucker-Firmware wird neu gestartet.",
        "ru": "🔁 *Перезагрузить прошивку?*\n\nПрошивка принтера будет перезагружена.",
        "pl": "🔁 *Restart firmware?*\n\nFirmware drukarki zostanie zrestartowana.",
    },
    "system.host_confirm": {
        "en": "🔁 *Host Reboot?*\n\nThis will reboot the printer host system.",
        "de": "🔁 *Host neustarten?*\n\nDas Host-System wird neu gestartet.",
        "ru": "🔁 *Перезагрузить хост?*\n\nХост-система принтера будет перезагружена.",
        "pl": "🔁 *Restart hosta?*\n\nSystem hosta drukarki zostanie zrestartowany.",
    },

    # ── Emergency Stop ───────────────────────────────────────────────────
    "estop.confirm": {
        "en": "🚨 *EMERGENCY STOP*\n\nThis will IMMEDIATELY halt the printer.\nYou will need to restart firmware after.\n\nAre you sure?",
        "de": "🚨 *NOT-HALT*\n\nDer Drucker wird SOFORT gestoppt.\nDanach muss die Firmware neu gestartet werden.\n\nBist du sicher?",
        "ru": "🚨 *АВАРИЙНАЯ ОСТАНОВКА*\n\nПринтер будет НЕМЕДЛЕННО остановлен.\nПосле этого потребуется перезагрузка прошивки.\n\nВы уверены?",
        "pl": "🚨 *ZATRZYMANIE AWARYJNE*\n\nDrukarka zostanie NATYCHMIAST zatrzymana.\nPo tym wymagany będzie restart firmware.\n\nCzy na pewno?",
    },
    "estop.yes": {
        "en": "🚨 YES, STOP NOW",
        "de": "🚨 JA, SOFORT STOPPEN",
        "ru": "🚨 ДА, ОСТАНОВИТЬ",
        "pl": "🚨 TAK, ZATRZYMAJ",
    },
    "estop.done": {
        "en": "🚨 *EMERGENCY STOP EXECUTED*\n\nRestart firmware to continue.",
        "de": "🚨 *NOT-HALT AUSGEFÜHRT*\n\nFirmware neustarten um fortzufahren.",
        "ru": "🚨 *АВАРИЙНАЯ ОСТАНОВКА ВЫПОЛНЕНА*\n\nПерезагрузите прошивку для продолжения.",
        "pl": "🚨 *ZATRZYMANIE AWARYJNE WYKONANE*\n\nZrestartuj firmware, aby kontynuować.",
    },
    "estop.failed": {
        "en": "❌ E-Stop failed! Check connection.",
        "de": "❌ Not-Halt fehlgeschlagen! Verbindung prüfen.",
        "ru": "❌ Аварийная остановка не удалась! Проверьте соединение.",
        "pl": "❌ Zatrzymanie awaryjne nie powiodło się! Sprawdź połączenie.",
    },

    # ── Settings ─────────────────────────────────────────────────────────
    "settings.title": {
        "en": "⚙️ *Settings*\n\nTap to toggle or cycle values:",
        "de": "⚙️ *Einstellungen*\n\nTippe zum Umschalten:",
        "ru": "⚙️ *Настройки*\n\nНажмите для переключения:",
        "pl": "⚙️ *Ustawienia*\n\nKliknij, aby przełączyć:",
    },
    "settings.print_complete": {
        "en": "Print Complete",
        "de": "Druck fertig",
        "ru": "Печать завершена",
        "pl": "Druk ukończony",
    },
    "settings.print_error": {
        "en": "Print Error",
        "de": "Druckfehler",
        "ru": "Ошибка печати",
        "pl": "Błąd druku",
    },
    "settings.print_start": {
        "en": "Print Start",
        "de": "Druck gestartet",
        "ru": "Начало печати",
        "pl": "Początek druku",
    },
    "settings.print_cancelled": {
        "en": "Print Cancelled",
        "de": "Druck abgebrochen",
        "ru": "Печать отменена",
        "pl": "Druk anulowany",
    },
    "settings.filament_runout": {
        "en": "Filament Runout",
        "de": "Filament leer",
        "ru": "Конец филамента",
        "pl": "Brak filamentu",
    },
    "settings.progress_milestone": {
        "en": "Progress Milestones",
        "de": "Fortschritts-Meilensteine",
        "ru": "Уведомления о прогрессе",
        "pl": "Kamienie milowe postępu",
    },
    "settings.temp_alert": {
        "en": "Temp Alert",
        "de": "Temp-Alarm",
        "ru": "Тревога темп.",
        "pl": "Alarm temp.",
    },
    "settings.estop_menu": {
        "en": "E-Stop in Menu",
        "de": "Not-Halt im Menü",
        "ru": "Авар. стоп в меню",
        "pl": "Aw. stop w menu",
    },
    "settings.estop_confirm": {
        "en": "E-Stop Confirmation",
        "de": "Not-Halt Bestätigung",
        "ru": "Подтв. авар. стопа",
        "pl": "Potw. aw. stopu",
    },
    "settings.poll": {
        "en": "Poll",
        "de": "Abfrage",
        "ru": "Опрос",
        "pl": "Odpytywanie",
    },
    "settings.files_per_page": {
        "en": "Files/page",
        "de": "Dateien/Seite",
        "ru": "Файлов/стр.",
        "pl": "Plików/str.",
    },
    "settings.language": {
        "en": "🌐 Language: English",
        "de": "🌐 Sprache: Deutsch",
        "ru": "🌐 Язык: Русский",
        "pl": "🌐 Język: Polski",
    },

    # ── Generic ──────────────────────────────────────────────────────────
    "generic.failed": {
        "en": "❌ Failed",
        "de": "❌ Fehlgeschlagen",
        "ru": "❌ Ошибка",
        "pl": "❌ Błąd",
    },
    "generic.done": {
        "en": "✅ Done",
        "de": "✅ Fertig",
        "ru": "✅ Готово",
        "pl": "✅ Gotowe",
    },
}


def t(key: str, lang: str = "en") -> str:
    """Get a translated string. Falls back to English."""
    entry = STRINGS.get(key)
    if not entry:
        return f"[{key}]"
    return entry.get(lang, entry.get("en", f"[{key}]"))
