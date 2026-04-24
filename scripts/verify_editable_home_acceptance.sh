#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  verify_editable_home_acceptance.sh [serial]

Environment:
  ADB_BIN           adb binary path. Defaults to adb, then /mnt/f/Android/Sdk/platform-tools/adb.exe.
  OUT_DIR           screenshot / report output directory. Defaults to /tmp/editable-home-acceptance.

This script validates the editable-home acceptance flow on a booted emulator:
  - L2 baseline restore
  - open editor from Home
  - save L1 with unique assignments
  - confirm SharedPreferences changed
  - confirm panel bounds changed
  - attempt duplicate assignment
  - confirm prefs did not change on duplicate save
EOF
}

SERIAL="${1:-emulator-5554}"
if [[ "${SERIAL}" == "-h" || "${SERIAL}" == "--help" ]]; then
  usage
  exit 0
fi

ADB_BIN="${ADB_BIN:-adb}"
if ! command -v "${ADB_BIN}" >/dev/null 2>&1; then
  if [[ -x /mnt/f/Android/Sdk/platform-tools/adb.exe ]]; then
    ADB_BIN="/mnt/f/Android/Sdk/platform-tools/adb.exe"
  else
    echo "adb not found; set ADB_BIN" >&2
    exit 1
  fi
fi

OUT_DIR="${OUT_DIR:-/tmp/editable-home-acceptance}"
mkdir -p "${OUT_DIR}"
REPORT_PATH="${OUT_DIR}/acceptance_report.md"

HOME_PKG="com.android.car.scalableui.hmi.home"
HOME_ACTIVITY="${HOME_PKG}/.HomeActivity"
HOME_EDIT_ACTIVITY="${HOME_PKG}/.HomeEditActivity"
PREFS_PATH="/data/user/10/${HOME_PKG}/shared_prefs/com.android.systemui.scalableui_poc_preferences.xml"

adb_cmd() {
  "${ADB_BIN}" -s "${SERIAL}" "$@"
}

shell() {
  adb_cmd shell "$@"
}

shell_root() {
  adb_cmd shell sh -c "$*"
}

init_report() {
  cat > "${REPORT_PATH}" <<EOF
# Editable-home Acceptance Report

- Serial: \`${SERIAL}\`
- Output dir: \`${OUT_DIR}\`
- Generated: \`$(date -Iseconds)\`

## Checks

EOF
}

record_check() {
  local name="$1"
  local result="$2"
  local detail="$3"
  printf -- "- [%s] %s: %s\n" "${result}" "${name}" "${detail}" >> "${REPORT_PATH}"
}

wait_for_device() {
  adb_cmd wait-for-device >/dev/null
  for _ in $(seq 1 90); do
    local boot
    boot="$(shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')"
    if [[ "${boot}" == "1" ]]; then
      return 0
    fi
    sleep 2
  done
  echo "device ${SERIAL} did not finish booting" >&2
  exit 1
}

ui_dump() {
  local dest="$1"
  shell uiautomator dump /data/local/tmp/view.xml >/dev/null
  adb_cmd exec-out cat /data/local/tmp/view.xml > "${dest}"
}

find_center_by_text() {
  local xml_path="$1"
  local needle="$2"
  local index="${3:-1}"
  python3 - "$xml_path" "$needle" "$index" <<'PY'
import re
import sys
import xml.etree.ElementTree as ET

xml_path, needle, index = sys.argv[1], sys.argv[2].lower(), int(sys.argv[3])
tree = ET.parse(xml_path)
matches = []
for node in tree.iter():
    text = (node.attrib.get("text", "") + " " + node.attrib.get("content-desc", "")).lower()
    if needle not in text:
        continue
    bounds = node.attrib.get("bounds", "")
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not m:
        continue
    left, top, right, bottom = map(int, m.groups())
    matches.append(f"{(left + right) // 2} {(top + bottom) // 2}")
if 1 <= index <= len(matches):
    print(matches[index - 1])
    sys.exit(0)
sys.exit(1)
PY
}

tap_text() {
  local needle="$1"
  local index="${2:-1}"
  local xml="${OUT_DIR}/ui.xml"
  ui_dump "${xml}"
  local coords
  coords="$(find_center_by_text "${xml}" "${needle}" "${index}")" || {
    echo "unable to find UI node containing text: ${needle} (index ${index})" >&2
    exit 1
  }
  shell input tap ${coords}
  sleep 1
}

ui_contains_text() {
  local needle="$1"
  local xml="${OUT_DIR}/ui-check.xml"
  ui_dump "${xml}"
  grep -Fqi "${needle}" "${xml}"
}

capture() {
  local name="$1"
  adb_cmd exec-out screencap -p > "${OUT_DIR}/${name}.png"
}

write_prefs() {
  local layout="$1"
  local primary="$2"
  local top="$3"
  local bottom="$4"
  local tmp="${OUT_DIR}/prefs.xml"
  cat > "${tmp}" <<EOF
<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map>
    <string name="selected_layout">${layout}</string>
    <boolean name="edit_mode_enabled" value="false" />
    <long name="last_updated_epoch_ms" value="0" />
    <string name="assignment_home_panel_primary">${primary}</string>
    <string name="assignment_home_panel_secondary_top">${top}</string>
    <string name="assignment_home_panel_secondary_bottom">${bottom}</string>
</map>
EOF
  adb_cmd push "${tmp}" /data/local/tmp/editable-home-prefs.xml >/dev/null
  local uid
  uid="$(shell dumpsys package "${HOME_PKG}" | tr -d '\r' | sed -n 's/.*userId=\\([0-9][0-9]*\\).*/\\1/p' | head -n 1)"
  if [[ -z "${uid}" ]]; then
    echo "unable to resolve uid for ${HOME_PKG}" >&2
    exit 1
  fi
  shell_root "mkdir -p \$(dirname '${PREFS_PATH}') && cp /data/local/tmp/editable-home-prefs.xml '${PREFS_PATH}' && chown ${uid}:${uid} '${PREFS_PATH}' && chmod 660 '${PREFS_PATH}'"
}

read_prefs() {
  shell_root "cat '${PREFS_PATH}'" | tr -d '\r'
}

assert_prefs_contains() {
  local content="$1"
  local pattern="$2"
  if ! grep -Fq "${pattern}" <<<"${content}"; then
    echo "expected prefs to contain: ${pattern}" >&2
    exit 1
  fi
}

assert_component_present() {
  local dump_path="$1"
  local component="$2"
  if ! grep -Fq "${component}" "${dump_path}"; then
    echo "expected component in activity dump: ${component}" >&2
    exit 1
  fi
}

extract_bounds() {
  local dump_path="$1"
  local component="$2"
  python3 - "$dump_path" "$component" <<'PY'
import re
import sys

path, component = sys.argv[1], sys.argv[2]
text = open(path, encoding="utf-8").read()
pattern = re.compile(re.escape(component) + r".*?mBounds=Rect\((\d+), (\d+) - (\d+), (\d+)\)", re.S)
m = pattern.search(text)
if not m:
    sys.exit(1)
print(" ".join(m.groups()))
PY
}

dump_activities() {
  local path="$1"
  shell dumpsys activity activities | tr -d '\r' > "${path}"
}

assert_bounds_changed() {
  local before="$1"
  local after="$2"
  if [[ "${before}" == "${after}" ]]; then
    echo "expected bounds to change, but they stayed the same: ${before}" >&2
    exit 1
  fi
}

assert_bounds_inset() {
  local bounds="$1"
  local width="$2"
  local height="$3"
  read -r left top right bottom <<<"${bounds}"
  if (( left <= 0 || top <= 0 || right >= width || bottom >= height )); then
    echo "expected inset bounds inside display ${width}x${height}, got ${bounds}" >&2
    exit 1
  fi
}

display_size() {
  shell wm size | tr -d '\r' | sed -n 's/.*Physical size: \([0-9][0-9]*\)x\([0-9][0-9]*\).*/\1 \2/p' | head -n 1
}

finish_report() {
  {
    echo
    echo "## Artifacts"
    echo
    echo "- Screenshots: \`${OUT_DIR}/*.png\`"
    echo "- Activity dumps: \`${OUT_DIR}/activities-*.txt\`"
    echo "- UI dumps: \`${OUT_DIR}/ui*.xml\`"
    echo "- Pref snapshots: embedded in this run via \`${PREFS_PATH}\`"
  } >> "${REPORT_PATH}"
}

main() {
  init_report
  adb_cmd root >/dev/null 2>&1 || true
  wait_for_device

  local product
  product="$(shell getprop ro.product.name | tr -d '\r')"
  if [[ "${product}" != "sdk_car_scalableui_editable_home_x86_64" ]]; then
    echo "device product is ${product}, not editable-home" >&2
    exit 1
  fi
  record_check "Product match" "PASS" "ro.product.name=${product}"

  local size width height
  size="$(display_size)"
  if [[ -z "${size}" ]]; then
    echo "unable to determine display size" >&2
    exit 1
  fi
  read -r width height <<<"${size}"
  record_check "Display size detected" "PASS" "${width}x${height}"

  write_prefs "L2" \
    "com.android.car.scalableui.hmi.map/.MapActivity" \
    "com.android.car.scalableui.hmi.media/.MediaActivity" \
    "com.android.car.scalableui.hmi.controls/.ControlsActivity"

  shell am force-stop "${HOME_PKG}" >/dev/null
  shell am start -W -n "${HOME_ACTIVITY}" >/dev/null
  sleep 3
  capture "home-l2"
  record_check "Boot into editable-home" "PASS" "captured ${OUT_DIR}/home-l2.png"

  local before_dump="${OUT_DIR}/activities-l2.txt"
  dump_activities "${before_dump}"
  assert_component_present "${before_dump}" "com.android.car.scalableui.hmi.map/.MapActivity"
  assert_component_present "${before_dump}" "com.android.car.scalableui.hmi.media/.MediaActivity"
  assert_component_present "${before_dump}" "com.android.car.scalableui.hmi.controls/.ControlsActivity"
  local before_primary
  before_primary="$(extract_bounds "${before_dump}" "com.android.car.scalableui.hmi.map/.MapActivity")"
  assert_bounds_inset "${before_primary}" "${width}" "${height}"
  record_check "L2 baseline apps" "PASS" "map/media/controls tasks found; primary bounds=${before_primary}"

  tap_text "Edit"
  capture "editor-open"
  if ui_contains_text "Home layout editor"; then
    record_check "Edit mode open" "PASS" "editor visible in ${OUT_DIR}/editor-open.png"
  else
    echo "editor UI did not appear after tapping Edit" >&2
    exit 1
  fi

  tap_text "L1"
  tap_text "Calendar mock" 2
  tap_text "Settings shortcut" 3
  capture "editor-before-save-l1"
  tap_text "Save"
  sleep 4
  capture "home-l1"

  local prefs_after_l1
  prefs_after_l1="$(read_prefs)"
  assert_prefs_contains "${prefs_after_l1}" '<string name="selected_layout">L1</string>'
  assert_prefs_contains "${prefs_after_l1}" 'assignment_home_panel_primary">com.android.car.scalableui.hmi.map/.MapActivity'
  assert_prefs_contains "${prefs_after_l1}" 'assignment_home_panel_secondary_top">com.android.car.scalableui.hmi.calendar/.CalendarActivity'
  assert_prefs_contains "${prefs_after_l1}" 'assignment_home_panel_secondary_bottom">com.android.car.scalableui.hmi.settings/.SettingsActivity'
  record_check "Preferences saved" "PASS" "selected_layout=L1 and assignments updated in shared_prefs"

  local after_dump="${OUT_DIR}/activities-l1.txt"
  dump_activities "${after_dump}"
  assert_component_present "${after_dump}" "com.android.car.scalableui.hmi.map/.MapActivity"
  assert_component_present "${after_dump}" "com.android.car.scalableui.hmi.calendar/.CalendarActivity"
  assert_component_present "${after_dump}" "com.android.car.scalableui.hmi.settings/.SettingsActivity"
  local after_primary
  after_primary="$(extract_bounds "${after_dump}" "com.android.car.scalableui.hmi.map/.MapActivity")"
  assert_bounds_changed "${before_primary}" "${after_primary}"
  assert_bounds_inset "${after_primary}" "${width}" "${height}"
  record_check "L1 layout transition" "PASS" "primary bounds changed from ${before_primary} to ${after_primary}"
  record_check "Per-panel assignment" "PASS" "map/calendar/settings tasks found after Save"

  shell am force-stop "${HOME_PKG}" >/dev/null
  shell am start -W -n "${HOME_ACTIVITY}" >/dev/null
  sleep 3
  capture "home-l1-restored"
  local restore_dump="${OUT_DIR}/activities-l1-restored.txt"
  dump_activities "${restore_dump}"
  assert_component_present "${restore_dump}" "com.android.car.scalableui.hmi.map/.MapActivity"
  assert_component_present "${restore_dump}" "com.android.car.scalableui.hmi.calendar/.CalendarActivity"
  assert_component_present "${restore_dump}" "com.android.car.scalableui.hmi.settings/.SettingsActivity"
  local restore_primary
  restore_primary="$(extract_bounds "${restore_dump}" "com.android.car.scalableui.hmi.map/.MapActivity")"
  if [[ "${restore_primary}" != "${after_primary}" ]]; then
    echo "restored primary bounds differ from saved L1 state: ${restore_primary} vs ${after_primary}" >&2
    exit 1
  fi
  record_check "Persistence" "PASS" "after force-stop/relaunch, L1 layout and assignments restored"

  tap_text "Edit"
  tap_text "Maps mock" 2
  capture "editor-duplicate-attempt"
  local prefs_before_duplicate
  prefs_before_duplicate="$(read_prefs)"
  tap_text "Save"
  sleep 2
  local prefs_after_duplicate
  prefs_after_duplicate="$(read_prefs)"
  if [[ "${prefs_before_duplicate}" != "${prefs_after_duplicate}" ]]; then
    echo "prefs changed during duplicate assignment attempt" >&2
    exit 1
  fi
  record_check "Duplicate assignment rejection" "PASS" "prefs unchanged after duplicate Save attempt"

  finish_report

  echo "editable-home acceptance check passed on ${SERIAL}"
  echo "artifacts: ${OUT_DIR}"
  echo "report: ${REPORT_PATH}"
}

main "$@"
