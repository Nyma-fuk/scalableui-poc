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
  - baseline restore with 3 panels
  - header-based app picker launch
  - per-panel app assignment
  - same-app move semantics
  - grip-driven split persistence
  - restore after Home relaunch
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
  local split_x="$2"
  local split_y="$3"
  local primary="$4"
  local top="$5"
  local bottom="$6"
  local tmp="${OUT_DIR}/prefs.xml"
  local prefs_dir
  prefs_dir="$(dirname "${PREFS_PATH}")"
  cat > "${tmp}" <<EOF
<?xml version='1.0' encoding='utf-8' standalone='yes' ?>
<map>
    <string name="selected_layout">${layout}</string>
    <boolean name="edit_mode_enabled" value="false" />
    <long name="last_updated_epoch_ms" value="0" />
    <float name="split_ratio_x" value="${split_x}" />
    <float name="split_ratio_right_y" value="${split_y}" />
    <string name="assignment_home_panel_primary">${primary}</string>
    <string name="assignment_home_panel_secondary_top">${top}</string>
    <string name="assignment_home_panel_secondary_bottom">${bottom}</string>
</map>
EOF
  adb_cmd push "${tmp}" /data/local/tmp/editable-home-prefs.xml >/dev/null
  local uid
  uid="$(shell dumpsys package "${HOME_PKG}" | tr -d '\r' | sed -n -e 's/.*userId=\([0-9][0-9]*\).*/\1/p' -e 's/.*appId=\([0-9][0-9]*\).*/\1/p' -e 's/.*uid=\([0-9][0-9]*\).*/\1/p' | head -n 1)"
  if [[ -z "${uid}" ]]; then
    echo "unable to resolve uid for ${HOME_PKG}" >&2
    exit 1
  fi
  adb_cmd shell mkdir -p "${prefs_dir}" >/dev/null
  adb_cmd shell cp /data/local/tmp/editable-home-prefs.xml "${PREFS_PATH}" >/dev/null
  adb_cmd shell chown "${uid}:${uid}" "${PREFS_PATH}" >/dev/null
  adb_cmd shell chmod 660 "${PREFS_PATH}" >/dev/null
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
pattern = re.compile(
    re.escape(component)
    + r".*?taskBounds=Rect\((\d+), (\d+) - (\d+), (\d+)\)",
    re.S,
)
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

compute_vertical_grip_coords() {
  local width="$1"
  local height="$2"
  local ratio="$3"
  python3 - "$width" "$height" "$ratio" <<'PY'
import sys
w, h, ratio = int(sys.argv[1]), int(sys.argv[2]), float(sys.argv[3])
left = round(w * 0.04)
right = round(w * 0.96)
top = round(h * 0.12)
bottom = round(h * 0.84)
x = round(left + (right - left) * ratio)
y = (top + bottom) // 2
print(f"{x} {y}")
PY
}

compute_horizontal_grip_coords() {
  local width="$1"
  local height="$2"
  local split_x="$3"
  local split_y="$4"
  python3 - "$width" "$height" "$split_x" "$split_y" <<'PY'
import sys
w, h = int(sys.argv[1]), int(sys.argv[2])
split_x, split_y = float(sys.argv[3]), float(sys.argv[4])
left = round(w * 0.04)
right = round(w * 0.96)
top = round(h * 0.12)
bottom = round(h * 0.84)
x = round(left + (right - left) * split_x)
y = round(top + (bottom - top) * split_y)
center_x = (x + right) // 2
print(f"{center_x} {y}")
PY
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

  write_prefs "L2" "0.62" "0.50" \
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

  if ui_contains_text "Primary panel" && ui_contains_text "Secondary top panel" \
      && ui_contains_text "Secondary bottom panel"; then
    record_check "Header panels visible" "PASS" "primary/top/bottom header text visible"
  else
    echo "header panels are not visible on Home" >&2
    exit 1
  fi

  tap_text "Primary panel"
  capture "picker-primary"
  if ui_contains_text "この panel に表示するアプリを選択します。"; then
    record_check "Primary app picker open" "PASS" "picker opened from primary header"
  else
    echo "primary app picker did not open" >&2
    exit 1
  fi
  tap_text "com.android.car.scalableui.hmi.calendar"
  sleep 4
  capture "home-primary-calendar"
  local prefs_after_primary
  prefs_after_primary="$(read_prefs)"
  assert_prefs_contains "${prefs_after_primary}" 'assignment_home_panel_primary">com.android.car.scalableui.hmi.calendar/.CalendarActivity'
  local after_primary_dump="${OUT_DIR}/activities-primary-calendar.txt"
  dump_activities "${after_primary_dump}"
  assert_component_present "${after_primary_dump}" "com.android.car.scalableui.hmi.calendar/.CalendarActivity"
  record_check "Primary assignment" "PASS" "primary panel assignment changed to calendar"

  tap_text "Secondary bottom panel"
  tap_text "com.android.car.scalableui.hmi.calendar"
  sleep 4
  capture "home-bottom-calendar"
  local prefs_after_move
  prefs_after_move="$(read_prefs)"
  assert_prefs_contains "${prefs_after_move}" 'assignment_home_panel_primary">com.android.car.scalableui.hmi.controls/.ControlsActivity'
  assert_prefs_contains "${prefs_after_move}" 'assignment_home_panel_secondary_bottom">com.android.car.scalableui.hmi.calendar/.CalendarActivity'
  local after_move_dump="${OUT_DIR}/activities-calendar-moved.txt"
  dump_activities "${after_move_dump}"
  assert_component_present "${after_move_dump}" "com.android.car.scalableui.hmi.controls/.ControlsActivity"
  assert_component_present "${after_move_dump}" "com.android.car.scalableui.hmi.calendar/.CalendarActivity"
  record_check "Same-app move semantics" "PASS" "calendar moved to secondary bottom and primary restored to controls"

  local vertical_before vertical_after horizontal_before horizontal_after
  vertical_before="$(extract_bounds "${after_move_dump}" "com.android.car.scalableui.hmi.controls/.ControlsActivity")"
  horizontal_before="$(extract_bounds "${after_move_dump}" "com.android.car.scalableui.hmi.media/.MediaActivity")"
  read -r vertical_x vertical_y <<<"$(compute_vertical_grip_coords "${width}" "${height}" "0.62")"
  shell input swipe "${vertical_x}" "${vertical_y}" "$((vertical_x + 140))" "${vertical_y}" 250
  sleep 2
  read -r horizontal_x horizontal_y <<<"$(compute_horizontal_grip_coords "${width}" "${height}" "0.72" "0.50")"
  shell input swipe "${horizontal_x}" "${horizontal_y}" "${horizontal_x}" "$((horizontal_y + 120))" 250
  sleep 2
  capture "home-after-grip"
  local after_grip_prefs
  after_grip_prefs="$(read_prefs)"
  assert_prefs_contains "${after_grip_prefs}" 'name="split_ratio_x"'
  assert_prefs_contains "${after_grip_prefs}" 'name="split_ratio_right_y"'
  local after_grip_dump="${OUT_DIR}/activities-after-grip.txt"
  dump_activities "${after_grip_dump}"
  vertical_after="$(extract_bounds "${after_grip_dump}" "com.android.car.scalableui.hmi.controls/.ControlsActivity")"
  horizontal_after="$(extract_bounds "${after_grip_dump}" "com.android.car.scalableui.hmi.media/.MediaActivity")"
  assert_bounds_changed "${vertical_before}" "${vertical_after}"
  assert_bounds_changed "${horizontal_before}" "${horizontal_after}"
  record_check "Grip resize persistence" "PASS" "panel bounds changed after grip drag and split ratios stored"

  shell am force-stop "${HOME_PKG}" >/dev/null
  shell am start -W -n "${HOME_ACTIVITY}" >/dev/null
  sleep 3
  capture "home-restored"
  local restore_dump="${OUT_DIR}/activities-restored.txt"
  dump_activities "${restore_dump}"
  assert_component_present "${restore_dump}" "com.android.car.scalableui.hmi.calendar/.CalendarActivity"
  assert_component_present "${restore_dump}" "com.android.car.scalableui.hmi.controls/.ControlsActivity"
  local restore_controls
  restore_controls="$(extract_bounds "${restore_dump}" "com.android.car.scalableui.hmi.controls/.ControlsActivity")"
  if [[ "${restore_controls}" != "${vertical_after}" ]]; then
    echo "restored control bounds differ from saved split state: ${restore_controls} vs ${vertical_after}" >&2
    exit 1
  fi
  record_check "Persistence" "PASS" "after force-stop/relaunch, assignments and split geometry restored"

  finish_report

  echo "editable-home acceptance check passed on ${SERIAL}"
  echo "artifacts: ${OUT_DIR}"
  echo "report: ${REPORT_PATH}"
}

main "$@"
