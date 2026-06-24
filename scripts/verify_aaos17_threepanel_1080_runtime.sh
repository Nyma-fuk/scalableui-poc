#!/usr/bin/env bash
set -euo pipefail

ADB_BIN="${ADB_BIN:-adb}"
ADB_SERIAL="${ADB_SERIAL:-}"
OUT_DIR="${OUT_DIR:-/tmp/aaos17-threepanel-1080-runtime-$(date +%Y%m%d-%H%M%S)}"

ADB_ARGS=()
if [[ -n "${ADB_SERIAL}" ]]; then
    ADB_ARGS=(-s "${ADB_SERIAL}")
fi

adb_shell() {
    "${ADB_BIN}" "${ADB_ARGS[@]}" shell "$@"
}

capture() {
    local name="$1"
    mkdir -p "${OUT_DIR}"
    "${ADB_BIN}" "${ADB_ARGS[@]}" exec-out screencap -p > "${OUT_DIR}/${name}.png"
    adb_shell dumpsys activity activities > "${OUT_DIR}/${name}_activities.txt"
    adb_shell dumpsys window > "${OUT_DIR}/${name}_window.txt"
    adb_shell logcat -d > "${OUT_DIR}/${name}_logcat.txt"
}

assert_file_contains() {
    local file="$1"
    local pattern="$2"
    local message="$3"
    if ! grep -Fq "${pattern}" "${file}"; then
        echo "FAIL: ${message}" >&2
        echo "  file: ${file}" >&2
        echo "  expected: ${pattern}" >&2
        exit 1
    fi
}

assert_no_crash() {
    if grep -R -E "FATAL EXCEPTION|incorrect safe bounds|SystemUI.*crash|has died" "${OUT_DIR}"/*.txt >/dev/null; then
        echo "FAIL: crash or safe-bounds error found in ${OUT_DIR}" >&2
        grep -R -n -E "FATAL EXCEPTION|incorrect safe bounds|SystemUI.*crash|has died" "${OUT_DIR}"/*.txt >&2
        exit 1
    fi
}

dismiss_initial_user_notice() {
    local dump_file="/sdcard/aaos17_threepanel_uidump.xml"
    adb_shell uiautomator dump "${dump_file}" >/dev/null 2>&1 || return 0
    if adb_shell cat "${dump_file}" 2>/dev/null | grep -Fq "Dismiss for now"; then
        adb_shell input tap 1476 583
        sleep 1
    fi
}

reset_demo_apps() {
    adb_shell am force-stop com.google.android.car.kitchensink || true
    adb_shell am force-stop com.android.car.ui.paintbooth || true
}

"${ADB_BIN}" "${ADB_ARGS[@]}" wait-for-device
mkdir -p "${OUT_DIR}"

adb_shell wm size > "${OUT_DIR}/wm_size.txt"
adb_shell wm density > "${OUT_DIR}/wm_density.txt"
adb_shell cmd overlay list --user 0 > "${OUT_DIR}/overlay_user0.txt"
adb_shell cmd overlay list --user 10 > "${OUT_DIR}/overlay_user10.txt" || true
adb_shell cmd resource get-array com.android.systemui array/window_states > "${OUT_DIR}/window_states.txt" 2>&1 || true

assert_file_contains "${OUT_DIR}/wm_size.txt" "Physical size: 1920x1080" "emulator must be 1920x1080"
assert_file_contains "${OUT_DIR}/overlay_user0.txt" "[x] com.android.systemui.rro.scalableUI.threePanel1080.codelab" "ThreePanel1080 overlay must be enabled for user 0"

reset_demo_apps

adb_shell logcat -c
adb_shell input keyevent HOME
sleep 3
dismiss_initial_user_notice
capture "01_home"
assert_file_contains "${OUT_DIR}/01_home_activities.txt" "topDisplayFocusedRootTask=Task" "home must have a focused root task"
assert_file_contains "${OUT_DIR}/01_home_activities.txt" "name=map_panel" "home must show map_panel"
assert_file_contains "${OUT_DIR}/01_home_activities.txt" "bounds=[0,67][1920,940]" "home map_panel bounds must cover content area"

adb_shell logcat -c
adb_shell input tap 782 1032
sleep 4
capture "02_all_apps"
assert_file_contains "${OUT_DIR}/02_all_apps_activities.txt" "name=app_panel" "All Apps must be routed to app_panel"
assert_file_contains "${OUT_DIR}/02_all_apps_activities.txt" "com.android.car.carlauncher/.AppGridActivity" "All Apps must open AppGridActivity"
assert_file_contains "${OUT_DIR}/02_all_apps_activities.txt" "bounds=[960,67][1920,940]" "All Apps panel must use right half bounds"
assert_file_contains "${OUT_DIR}/02_all_apps_logcat.txt" "_System_TaskOpenEvent" "All Apps launch must produce task open event"
assert_file_contains "${OUT_DIR}/02_all_apps_logcat.txt" "panelId=app_panel" "All Apps event must target app_panel"

adb_shell logcat -c
adb_shell am start -n com.google.android.car.kitchensink/.KitchenSinkActivity > "${OUT_DIR}/03_kitchensink_start.txt"
sleep 4
dismiss_initial_user_notice
capture "03_kitchensink"
assert_file_contains "${OUT_DIR}/03_kitchensink_activities.txt" "name=kitchen_sink_panel" "KitchenSink must be routed to kitchen_sink_panel"
assert_file_contains "${OUT_DIR}/03_kitchensink_activities.txt" "bounds=[960,67][1920,940]" "KitchenSink panel must use right half bounds"
assert_file_contains "${OUT_DIR}/03_kitchensink_activities.txt" "bounds=[0,67][960,940]" "map_panel must shrink to left half for KitchenSink"
assert_file_contains "${OUT_DIR}/03_kitchensink_logcat.txt" "_System_TaskOpenEvent" "KitchenSink launch must produce task open event"
assert_file_contains "${OUT_DIR}/03_kitchensink_logcat.txt" "panelId=kitchen_sink_panel" "KitchenSink event must target kitchen_sink_panel"

adb_shell logcat -c
adb_shell am start -n com.android.car.ui.paintbooth/.MainActivity > "${OUT_DIR}/04_paintbooth_start.txt"
sleep 4
dismiss_initial_user_notice
capture "04_paintbooth"
assert_file_contains "${OUT_DIR}/04_paintbooth_activities.txt" "name=paintbooth_panel" "PaintBooth must be routed to paintbooth_panel"
assert_file_contains "${OUT_DIR}/04_paintbooth_activities.txt" "bounds=[960,520][1920,940]" "PaintBooth panel must open at bottom-right"
assert_file_contains "${OUT_DIR}/04_paintbooth_activities.txt" "bounds=[0,67][960,940]" "map_panel must stay left for PaintBooth"
assert_file_contains "${OUT_DIR}/04_paintbooth_logcat.txt" "panelId=paintbooth_panel" "PaintBooth event must target paintbooth_panel"

adb_shell logcat -c
adb_shell input tap 960 760
sleep 3
capture "05_grip_top"
assert_file_contains "${OUT_DIR}/05_grip_top_activities.txt" "bounds=[960,67][1920,520]" "grip tap must move PaintBooth to top-right"
assert_file_contains "${OUT_DIR}/05_grip_top_activities.txt" "bounds=[0,520][960,940]" "grip tap must move map_panel to lower-left"
assert_file_contains "${OUT_DIR}/05_grip_top_logcat.txt" "_Drag_TaskSwitchEvent_top" "lower grip tap must emit top switch event"

adb_shell logcat -c
adb_shell input tap 960 280
sleep 3
capture "06_grip_bottom"
assert_file_contains "${OUT_DIR}/06_grip_bottom_activities.txt" "bounds=[960,520][1920,940]" "top grip tap must return PaintBooth to bottom-right"
assert_file_contains "${OUT_DIR}/06_grip_bottom_activities.txt" "bounds=[0,67][960,940]" "top grip tap must return map_panel to left half"
assert_file_contains "${OUT_DIR}/06_grip_bottom_logcat.txt" "_Drag_TaskSwitchEvent_bottom" "top grip tap must emit bottom switch event"

adb_shell logcat -c
adb_shell input keyevent HOME
sleep 3
capture "07_home_return"
assert_file_contains "${OUT_DIR}/07_home_return_activities.txt" "name=map_panel" "home return must focus map_panel"
assert_file_contains "${OUT_DIR}/07_home_return_activities.txt" "bounds=[0,67][1920,940]" "home return must restore map_panel content bounds"
assert_file_contains "${OUT_DIR}/07_home_return_logcat.txt" "_System_OnHomeEvent" "home return must emit home event"

assert_no_crash

echo "PASS: AAOS17 ThreePanel1080 runtime validation"
echo "Evidence: ${OUT_DIR}"
