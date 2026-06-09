#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  verify_declarative_multipanel_smoke.sh [serial]

Environment:
  ADB_BIN   adb binary path. Defaults to adb, then Windows adb.exe.
  OUT_DIR   report output directory.

Validates the aaos-scalable-ui-specs PoC baseline:
  - ScalableUI overlays and StubCarLauncher are installed
  - nav_panel / media_panel / user_slot_panel boot
  - empty user slot can open AppGrid and route an app into user_slot_panel
  - custom ScalableUI events drive page, resize, swap, edit, and camera override transitions
EOF
}

SERIAL="${1:-emulator-5564}"
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

OUT_DIR="${OUT_DIR:-/tmp/declarative-multipanel-smoke-$(date +%Y%m%d-%H%M%S)}"
mkdir -p "${OUT_DIR}"
SUMMARY="${OUT_DIR}/summary.txt"
REPORT="${OUT_DIR}/report.md"

SYSTEMUI_OVERLAY="com.android.systemui.rro.scalableui.declarative.multipanel"
FRAMEWORK_OVERLAY="android.car.config.rro.scalableui.declarative.multipanel"
CARSERVICE_OVERLAY="com.android.car.resources.scalableui.declarative.multipanel"
PANEL_EVENT_ACTION="com.android.car.scalableui.ACTION_PANEL_EVENT"

adb_cmd() {
  "${ADB_BIN}" -s "${SERIAL}" "$@"
}

shell() {
  adb_cmd shell "$@"
}

wait_boot() {
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

capture() {
  local name="$1"
  adb_cmd exec-out screencap -p > "${OUT_DIR}/${name}.png"
}

ui_dump() {
  local name="$1"
  shell uiautomator dump /data/local/tmp/view.xml >/dev/null
  adb_cmd exec-out cat /data/local/tmp/view.xml > "${OUT_DIR}/${name}.xml"
}

dump_activities() {
  local name="$1"
  shell dumpsys activity activities | tr -d '\r' > "${OUT_DIR}/${name}.txt"
}

dump_logcat() {
  local name="$1"
  adb_cmd logcat -d -v time | tr -d '\r' > "${OUT_DIR}/${name}.txt"
}

record() {
  printf '%s=%s\n' "$1" "$2" | tee -a "${SUMMARY}" >/dev/null
}

pass() {
  printf -- "- [PASS] %s\n" "$1" >> "${REPORT}"
}

fail() {
  printf -- "- [FAIL] %s\n" "$1" >> "${REPORT}"
  echo "FAIL: $1" >&2
  exit 1
}

assert_file_contains() {
  local path="$1"
  local needle="$2"
  local msg="$3"
  if grep -Fq "${needle}" "${path}"; then
    pass "${msg}"
  else
    fail "${msg}"
  fi
}

assert_file_not_contains() {
  local path="$1"
  local needle="$2"
  local msg="$3"
  if grep -Fq "${needle}" "${path}"; then
    fail "${msg}"
  else
    pass "${msg}"
  fi
}

center_by_text() {
  local xml="$1"
  local text="$2"
  python3 - "$xml" "$text" <<'PY'
import re
import sys
import xml.etree.ElementTree as ET

xml_path, needle = sys.argv[1], sys.argv[2].lower()
tree = ET.parse(xml_path)
for node in tree.iter():
    haystack = (node.attrib.get("text", "") + " " + node.attrib.get("content-desc", "")).lower()
    if needle not in haystack:
        continue
    bounds = node.attrib.get("bounds", "")
    m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
    if not m:
        continue
    left, top, right, bottom = map(int, m.groups())
    print((left + right) // 2, (top + bottom) // 2)
    sys.exit(0)
sys.exit(1)
PY
}

tap_text_from_dump() {
  local xml="$1"
  local text="$2"
  local coords
  coords="$(center_by_text "${xml}" "${text}")" || return 1
  shell input tap ${coords}
}

display_size() {
  shell wm size | tr -d '\r' | sed -n 's/.*Physical size: \([0-9][0-9]*\)x\([0-9][0-9]*\).*/\1 \2/p' | head -n 1
}

tap_system_bar_apps() {
  local width="$1"
  local height="$2"
  shell input tap $(( width * 407 / 1000 )) $(( height * 956 / 1000 ))
}

wait_for_text() {
  local text="$1"
  local dump_name="$2"
  for _ in $(seq 1 20); do
    ui_dump "${dump_name}"
    if grep -Fq "text=\"${text}\"" "${OUT_DIR}/${dump_name}.xml"; then
      return 0
    fi
    sleep 1
  done
  return 1
}

dispatch_event() {
  local event_id="$1"
  shell am broadcast -a "${PANEL_EVENT_ACTION}" --es event_id "${event_id}" >/dev/null
  sleep 1
}

init_report() {
  cat > "${REPORT}" <<EOF
# aaos-scalable-ui-specs PoC Smoke Report

- serial: \`${SERIAL}\`
- output: \`${OUT_DIR}\`
- generated: \`$(date -Iseconds)\`

## Checks

EOF
  : > "${SUMMARY}"
  record artifact "${OUT_DIR}"
  record serial "${SERIAL}"
}

main() {
  init_report
  wait_boot

  local size width height
  size="$(display_size)"
  read -r width height <<<"${size}"
  record wm_size "${width}x${height}"

  local pm_path
  pm_path="$(shell pm path com.android.car.carlauncher | tr -d '\r')"
  record pm_path "${pm_path}"
  [[ "${pm_path}" == *"/system_ext/priv-app/StubCarLauncher/"* ]] \
    && pass "StubCarLauncher is installed under system_ext" \
    || fail "StubCarLauncher is installed under system_ext"

  shell cmd overlay list | tr -d '\r' > "${OUT_DIR}/overlays.txt"
  assert_file_contains "${OUT_DIR}/overlays.txt" "[x] ${SYSTEMUI_OVERLAY}" "SystemUI ScalableUI overlay is enabled"
  assert_file_contains "${OUT_DIR}/overlays.txt" "[x] ${FRAMEWORK_OVERLAY}" "Framework ScalableUI overlay is enabled"
  assert_file_contains "${OUT_DIR}/overlays.txt" "[x] ${CARSERVICE_OVERLAY}" "CarService PoC overlay is enabled"

  local sysui_pid_home carlauncher_pid_home
  sysui_pid_home="$(shell pidof com.android.systemui | tr -d '\r')"
  carlauncher_pid_home="$(shell pidof com.android.car.carlauncher | tr -d '\r')"
  record systemui_pid_home "${sysui_pid_home}"
  record carlauncher_pid_home "${carlauncher_pid_home}"

  shell input keyevent KEYCODE_HOME
  sleep 2
  ui_dump "home-before-dismiss"
  if grep -Eq 'User Notice|KitchenSink' "${OUT_DIR}/home-before-dismiss.xml"; then
    tap_text_from_dump "${OUT_DIR}/home-before-dismiss.xml" "Dismiss for now" \
      || shell input tap $(( width * 755 / 1000 )) $(( height * 542 / 1000 ))
    sleep 1
  fi
  capture "01-home"
  ui_dump "home"
  dump_activities "activities-home"

  assert_file_contains "${OUT_DIR}/activities-home.txt" "com.android.car.mapsplaceholder/.MapsPlaceholderActivity" "nav_panel activity is present"
  assert_file_contains "${OUT_DIR}/activities-home.txt" "com.android.car.carlauncher/.ControlBarActivity" "media_panel activity is present"
  assert_file_contains "${OUT_DIR}/activities-home.txt" "com.android.car.carlauncher/.EmptySlotActivity" "user_slot_panel empty activity is present"
  assert_file_contains "${OUT_DIR}/activities-home.txt" "mBounds=Rect(1152, 572 - 1881, 1026)" "user_slot_panel uses expected empty slot bounds"
  pass "user slot empty hint is visible in screenshot 01-home"

  shell input tap $(( width * 790 / 1000 )) $(( height * 780 / 1000 ))
  wait_for_text "Choose app" "assign-appgrid" || fail "targeted AppGrid opens from empty user slot"
  capture "02-assign-appgrid"
  assert_file_contains "${OUT_DIR}/assign-appgrid.xml" "Target panel: user_slot_panel" "AppGrid carries user_slot_panel target"

  local calendar_xml=""
  for i in $(seq 0 6); do
    ui_dump "assign-calendar-${i}"
    if grep -Fq 'text="Calendar"' "${OUT_DIR}/assign-calendar-${i}.xml"; then
      calendar_xml="${OUT_DIR}/assign-calendar-${i}.xml"
      break
    fi
    shell input swipe $(( width / 2 )) $(( height * 850 / 1000 )) $(( width / 2 )) $(( height * 280 / 1000 )) 450
    sleep 1
  done
  [[ -n "${calendar_xml}" ]] || fail "Calendar row is visible in targeted AppGrid"
  tap_text_from_dump "${calendar_xml}" "Calendar" || fail "Calendar row can be tapped"
  sleep 3
  capture "03-calendar-user-slot"
  dump_activities "activities-calendar-user-slot"
  assert_file_contains "${OUT_DIR}/activities-calendar-user-slot.txt" "com.android.calendar/.AllInOneActivity" "Calendar launches"
  assert_file_contains "${OUT_DIR}/activities-calendar-user-slot.txt" "mBounds=Rect(1152, 572 - 1881, 1026)" "Calendar is routed to user_slot_panel bounds"

  dispatch_event "switch_workspace_page_2"
  capture "04-page-2"
  dump_activities "activities-page-2"
  assert_file_contains "${OUT_DIR}/activities-page-2.txt" "mBounds=Rect(38, 53 - 921, 1026)" "switch_workspace_page_2 changes nav_panel bounds"

  dispatch_event "resize_panel_nav_wide"
  capture "05-resize-nav-wide"
  dump_activities "activities-resize-nav-wide"
  assert_file_contains "${OUT_DIR}/activities-resize-nav-wide.txt" "mBounds=Rect(38, 53 - 1305, 1026)" "resize_panel_nav_wide changes nav_panel bounds"

  dispatch_event "swap_panel_position_nav_media"
  capture "06-swap-nav-media"
  dump_activities "activities-swap-nav-media"
  assert_file_contains "${OUT_DIR}/activities-swap-nav-media.txt" "mBounds=Rect(1152, 53 - 1881, 507)" "swap_panel_position_nav_media moves nav_panel to media position"

  adb_cmd logcat -c
  dispatch_event "enter_layout_edit"
  capture "07-layout-edit"
  ui_dump "layout-edit"
  dump_logcat "layout-edit-logcat"
  assert_file_contains "${OUT_DIR}/layout-edit-logcat.txt" "Layout edit mode" "layout edit overlay appears"
  dispatch_event "exit_layout_edit"

  dispatch_event "enter_camera_override"
  capture "08-camera-override"
  dump_activities "activities-camera-override"
  assert_file_contains "${OUT_DIR}/activities-camera-override.txt" "com.android.car.carlauncher/.CameraStubActivity" "camera override activity is present"
  assert_file_contains "${OUT_DIR}/activities-camera-override.txt" "mBounds=Rect(0, 0 - ${width}, ${height})" "camera override uses full display bounds"

  dispatch_event "exit_camera_override"
  sleep 1
  capture "09-camera-exit"
  dump_activities "activities-camera-exit"
  assert_file_contains "${OUT_DIR}/activities-camera-exit.txt" "com.android.car.carlauncher/.CameraStubActivity" "camera override activity remains restorable after exit"
  assert_file_contains "${OUT_DIR}/activities-camera-exit.txt" "mBounds=Rect(0, ${height} - ${width}, $(( height * 2 )))" "camera fullscreen is dismissed after exit"

  tap_system_bar_apps "${width}" "${height}"
  wait_for_text "Apps" "systembar-appgrid" || fail "System Bar Apps button opens fullscreen AppGrid"
  capture "10-systembar-appgrid"
  pass "System Bar Apps button opens fullscreen AppGrid"

  local sysui_pid_after carlauncher_pid_after fatal_count
  sysui_pid_after="$(shell pidof com.android.systemui | tr -d '\r')"
  carlauncher_pid_after="$(shell pidof com.android.car.carlauncher | tr -d '\r')"
  fatal_count="$(shell logcat -d -t 5000 | tr -d '\r' | grep -c 'FATAL EXCEPTION' || true)"
  record systemui_pid_after "${sysui_pid_after}"
  record carlauncher_pid_after "${carlauncher_pid_after}"
  record fatal_exception_count "${fatal_count}"

  [[ "${sysui_pid_home}" == "${sysui_pid_after}" ]] \
    && pass "SystemUI process stayed alive" \
    || fail "SystemUI process stayed alive"
  [[ "${carlauncher_pid_home}" == "${carlauncher_pid_after}" ]] \
    && pass "StubCarLauncher process stayed alive" \
    || fail "StubCarLauncher process stayed alive"
  [[ "${fatal_count}" == "0" ]] \
    && pass "No recent FATAL EXCEPTION in logcat tail" \
    || fail "No recent FATAL EXCEPTION in logcat tail"

  echo "PASS: report=${REPORT}"
}

main "$@"
