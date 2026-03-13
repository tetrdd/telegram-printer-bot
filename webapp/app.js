/**
 * Telegram Mini App — Printer Control Dashboard
 *
 * Connects directly to Moonraker API.
 * Moonraker URL is passed via the bot's web_app_data or falls back to config.
 */

// ── Telegram WebApp Init ────────────────────────────────────────────────────
const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
  tg.enableClosingConfirmation();
}

// ── Configuration ───────────────────────────────────────────────────────────
// The Moonraker URL can be passed via URL hash: #moonraker=http://192.168.1.100:7125
// Or set it here directly:
const DEFAULT_MOONRAKER = 'http://192.168.1.100:7125';

function getMoonrakerUrl() {
  const hash = window.location.hash;
  const match = hash.match(/moonraker=([^&]+)/);
  if (match) return decodeURIComponent(match[1]).replace(/\/$/, '');
  return DEFAULT_MOONRAKER;
}

const MOONRAKER = getMoonrakerUrl();
const POLL_INTERVAL = 3000; // 3s refresh

let pollTimer = null;
let connected = false;
let pendingModalAction = null;

// ── DOM Refs ────────────────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);
const dot = $('connection-dot');
const stateIcon = $('state-icon');
const stateText = $('state-text');
const stateFile = $('state-file');
const progressFill = $('progress-fill');
const progressPct = $('progress-pct');

// ── Tab Navigation ──────────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    tab.classList.add('active');
    const target = tab.dataset.tab;
    document.getElementById(`tab-${target}`).classList.add('active');

    if (target === 'files') loadFiles();
  });
});

// ── Moonraker API ───────────────────────────────────────────────────────────
async function mrGet(endpoint) {
  try {
    const r = await fetch(`${MOONRAKER}${endpoint}`, { signal: AbortSignal.timeout(8000) });
    if (!r.ok) return null;
    return await r.json();
  } catch (e) {
    return null;
  }
}

async function mrPost(endpoint, body = null) {
  try {
    const opts = { method: 'POST', signal: AbortSignal.timeout(8000) };
    if (body) {
      opts.headers = { 'Content-Type': 'application/json' };
      opts.body = JSON.stringify(body);
    }
    const r = await fetch(`${MOONRAKER}${endpoint}`, opts);
    return r.ok;
  } catch (e) {
    return false;
  }
}

// ── Status Polling ──────────────────────────────────────────────────────────
async function pollStatus() {
  const data = await mrGet('/printer/objects/query?print_stats&virtual_sdcard&extruder&heater_bed');

  if (!data) {
    setConnected(false);
    return;
  }
  setConnected(true);

  const s = data.result?.status || {};
  const stats = s.print_stats || {};
  const vsd = s.virtual_sdcard || {};
  const ext = s.extruder || {};
  const bed = s.heater_bed || {};

  // State
  const state = stats.state || 'unknown';
  updateState(state, stats.filename || '');

  // Progress
  const pct = (vsd.progress || 0) * 100;
  progressFill.style.width = `${pct}%`;
  progressPct.textContent = `${pct.toFixed(1)}%`;

  // Duration & ETA
  const dur = stats.print_duration || 0;
  $('stat-duration').textContent = fmtDuration(dur);

  if (pct > 1 && state === 'printing') {
    const remaining = (dur / (pct / 100)) - dur;
    $('stat-eta').textContent = `~${fmtDuration(remaining)}`;
  } else {
    $('stat-eta').textContent = '—';
  }

  // Filament
  const fil = (stats.filament_used || 0) / 1000;
  $('stat-filament').textContent = `${fil.toFixed(2)} m`;

  // Temperatures
  $('temp-hotend').textContent = (ext.temperature || 0).toFixed(1);
  $('target-hotend').textContent = (ext.target || 0).toFixed(0);
  $('power-hotend').style.width = `${(ext.power || 0) * 100}%`;

  $('temp-bed').textContent = (bed.temperature || 0).toFixed(1);
  $('target-bed').textContent = (bed.target || 0).toFixed(0);
  $('power-bed').style.width = `${(bed.power || 0) * 100}%`;
}

function setConnected(c) {
  connected = c;
  dot.className = `dot ${c ? 'online' : 'offline'}`;
  dot.title = c ? 'Connected' : 'Disconnected';
}

function updateState(state, filename) {
  const labels = {
    ready: 'Ready', standby: 'Standby', printing: 'Printing',
    paused: 'Paused', error: 'Error', complete: 'Complete',
    cancelled: 'Cancelled', shutdown: 'Shutdown', startup: 'Starting',
  };
  const classes = {
    ready: 'ready', standby: 'ready', printing: 'printing',
    paused: 'paused', error: 'error', complete: 'ready',
    cancelled: 'other', shutdown: 'other', startup: 'other',
  };

  stateText.textContent = labels[state] || state;
  stateIcon.className = `state-dot ${classes[state] || 'other'}`;
  stateFile.textContent = filename || '—';
}

// ── Commands ────────────────────────────────────────────────────────────────
async function sendCmd(cmd) {
  const endpoints = {
    pause: '/printer/print/pause',
    resume: '/printer/print/resume',
    cancel: '/printer/print/cancel',
  };

  if (cmd === 'cancel') {
    showModal('Cancel the current print?', async () => {
      const ok = await mrPost(endpoints.cancel);
      toast(ok ? 'Print cancelled' : 'Failed to cancel', ok ? 'success' : 'error');
    });
    return;
  }

  const ok = await mrPost(endpoints[cmd]);
  toast(ok ? `${cmd} OK` : `${cmd} failed`, ok ? 'success' : 'error');
}

async function sendGcode(cmd) {
  const encoded = encodeURIComponent(cmd);
  const ok = await mrPost(`/printer/gcode/script?script=${encoded}`);
  toast(ok ? `${cmd} ✓` : `${cmd} ✗`, ok ? 'success' : 'error');
  return ok;
}

async function sendGcodeInput() {
  const input = $('gcode-input');
  const cmd = input.value.trim();
  if (!cmd) return;

  const ok = await sendGcode(cmd);
  const log = $('gcode-log');
  const entry = document.createElement('div');
  entry.className = `entry ${ok ? 'ok' : 'fail'}`;
  entry.textContent = `${ok ? '✓' : '✗'} ${cmd}`;
  log.prepend(entry);
  input.value = '';
}

// Enter key for GCode input
document.addEventListener('DOMContentLoaded', () => {
  $('gcode-input')?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') sendGcodeInput();
  });
});

async function setTemp(heater, temp) {
  const ok = await sendGcode(`SET_HEATER_TEMPERATURE HEATER=${heater} TARGET=${temp}`);
  if (ok) toast(`${heater === 'extruder' ? 'Hotend' : 'Bed'} → ${temp}°C`, 'success');
}

async function emergencyStop() {
  showModal('🚨 EMERGENCY STOP?\n\nThis will immediately halt the printer.', async () => {
    const ok = await mrPost('/printer/emergency_stop');
    toast(ok ? '🚨 STOPPED' : 'E-Stop failed!', ok ? 'error' : 'error');
  });
}

// ── File Browser ────────────────────────────────────────────────────────────
async function loadFiles() {
  const list = $('file-list');
  list.innerHTML = '<div class="file-loading">Loading...</div>';

  const data = await mrGet('/server/files/list?root=gcodes');
  if (!data || !data.result) {
    list.innerHTML = '<div class="file-loading">Failed to load files</div>';
    return;
  }

  const files = data.result.sort((a, b) => (b.modified || 0) - (a.modified || 0));

  if (files.length === 0) {
    list.innerHTML = '<div class="file-loading">No files found</div>';
    return;
  }

  list.innerHTML = files.map(f => {
    const name = f.path || 'unknown';
    const size = fmtSize(f.size || 0);
    const short = name.length > 35 ? '...' + name.slice(-32) : name;
    return `
      <div class="file-item">
        <div class="file-info">
          <div class="file-name" title="${esc(name)}">${esc(short)}</div>
          <div class="file-meta">${size}</div>
        </div>
        <div class="file-actions">
          <button class="btn btn-sm" onclick="printFile('${esc(name)}')">🖨️</button>
        </div>
      </div>
    `;
  }).join('');
}

function printFile(name) {
  showModal(`Print "${name.length > 30 ? '...' + name.slice(-27) : name}"?`, async () => {
    const encoded = encodeURIComponent(name);
    const ok = await mrPost(`/printer/print/start?filename=${encoded}`);
    toast(ok ? 'Print started!' : 'Failed to start', ok ? 'success' : 'error');
  });
}

// ── Camera ──────────────────────────────────────────────────────────────────
async function takeSnapshot() {
  const container = $('camera-container');
  container.innerHTML = '<div class="camera-placeholder">Capturing...</div>';

  // Try common webcam URLs
  const snapUrl = `${MOONRAKER.replace(':7125', '')}/webcam/?action=snapshot`;

  const img = new Image();
  img.onload = () => {
    container.innerHTML = '';
    container.appendChild(img);
  };
  img.onerror = () => {
    container.innerHTML = '<div class="camera-placeholder">No camera found. Check config.</div>';
  };
  img.src = `${snapUrl}&t=${Date.now()}`;
  img.alt = 'Printer camera snapshot';
}

// ── Modal ────────────────────────────────────────────────────────────────────
function showModal(text, onConfirm) {
  $('modal-text').textContent = text;
  $('modal-overlay').classList.remove('hidden');
  pendingModalAction = onConfirm;
}

function modalConfirm() {
  $('modal-overlay').classList.add('hidden');
  if (pendingModalAction) pendingModalAction();
  pendingModalAction = null;
}

function modalCancel() {
  $('modal-overlay').classList.add('hidden');
  pendingModalAction = null;
}

// ── Toast ────────────────────────────────────────────────────────────────────
function toast(msg, type = '') {
  const el = $('toast');
  el.textContent = msg;
  el.className = `toast ${type}`;
  setTimeout(() => el.classList.add('hidden'), 2500);

  // Haptic feedback via Telegram
  if (tg?.HapticFeedback) {
    if (type === 'error') tg.HapticFeedback.notificationOccurred('error');
    else if (type === 'success') tg.HapticFeedback.notificationOccurred('success');
  }
}

// ── Helpers ──────────────────────────────────────────────────────────────────
function fmtDuration(sec) {
  const h = Math.floor(sec / 3600);
  const m = Math.floor((sec % 3600) / 60);
  const s = Math.floor(sec % 60);
  if (h > 0) return `${h}h ${m}m`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}

function fmtSize(bytes) {
  if (bytes >= 1024 ** 3) return `${(bytes / 1024 ** 3).toFixed(1)} GB`;
  if (bytes >= 1024 ** 2) return `${(bytes / 1024 ** 2).toFixed(1)} MB`;
  if (bytes >= 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${bytes} B`;
}

function esc(str) {
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#039;');
}

// ── Start ───────────────────────────────────────────────────────────────────
pollStatus();
pollTimer = setInterval(pollStatus, POLL_INTERVAL);
