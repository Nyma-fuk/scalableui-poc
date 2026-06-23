#!/usr/bin/env bash
set -euo pipefail

ANDROID_ROOT="${ANDROID_ROOT:-$HOME/work/android17-r1}"
PATTERN='soong_build|soong_ui|build/soong/bin/m|prebuilts/build-tools/linux-x86/bin/ninja|ckati|kati'

usage() {
  cat <<'USAGE'
Usage:
  scripts/aaos17_scalableui_build_action.sh status
  scripts/aaos17_scalableui_build_action.sh stop
  scripts/aaos17_scalableui_build_action.sh commands

Environment:
  ANDROID_ROOT=/home/y-fuk/work/android17-r1

Purpose:
  Manual preflight/action helper for the AAOS17 ScalableUI PoC.
  Use the standard sdk_car_x86_64 target and layer the ScalableUI PoC
  RRO/launcher/SystemUI deltas onto it.
USAGE
}

status() {
  cd "$ANDROID_ROOT"
  echo "== Android root =="
  pwd
  echo
  echo "== Build processes =="
  pgrep -af "$PATTERN" || true
  echo
  echo "== out/.lock holder =="
  if [ -e out/.lock ] && command -v lsof >/dev/null 2>&1; then
    lsof out/.lock || true
  elif [ -e out/.lock ]; then
    echo "out/.lock exists; lsof is not available."
  else
    echo "out/.lock does not exist."
  fi
  echo
  echo "== Memory =="
  free -h
  echo
  echo "== Disk =="
  df -h "$ANDROID_ROOT" /mnt/f 2>/dev/null || df -h "$ANDROID_ROOT"
}

stop_builds() {
  cd "$ANDROID_ROOT"
  mapfile -t pgids < <(
    ps -eo pid=,pgid=,cmd= |
      awk -v pat="$PATTERN" -v root="$ANDROID_ROOT" '
        $0 ~ pat && $0 ~ root {print $2}
      ' |
      sort -u
  )

  if [ "${#pgids[@]}" -eq 0 ]; then
    echo "No matching Android build process groups found."
    status
    return 0
  fi

  printf 'TERM process groups: %s\n' "${pgids[*]}"
  for pgid in "${pgids[@]}"; do
    kill -TERM -- "-$pgid" 2>/dev/null || true
  done
  sleep 5

  mapfile -t remaining < <(
    ps -eo pgid=,cmd= |
      awk -v pat="$PATTERN" -v root="$ANDROID_ROOT" '
        $0 ~ pat && $0 ~ root {print $1}
      ' |
      sort -u
  )
  if [ "${#remaining[@]}" -gt 0 ]; then
    printf 'KILL remaining process groups: %s\n' "${remaining[*]}"
    for pgid in "${remaining[@]}"; do
      kill -KILL -- "-$pgid" 2>/dev/null || true
    done
    sleep 2
  fi

  status
}

commands() {
  cat <<'COMMANDS'
cd ~/work/android17-r1
source build/envsetup.sh
lunch sdk_car_x86_64-trunk_staging-userdebug

# Stable Soong preflight.
SOONG_NINJA=ninja SOONG_INCREMENTAL_ANALYSIS=false m -j1 nothing

# PoC module build.
SOONG_NINJA=ninja m -j4 \
  ScalableUiStubCarLauncher \
  CarServiceScalableUiDeclarativeMultipanelRRO \
  CarFrameworkScalableUiDeclarativeMultipanelRRO \
  CarSystemUIScalableUiDeclarativeMultipanelRRO

# Runtime image build.
SOONG_NINJA=ninja m -j6 emu_img_zip
COMMANDS
}

case "${1:-}" in
  status)
    status
    ;;
  stop)
    stop_builds
    ;;
  commands)
    commands
    ;;
  *)
    usage
    exit 2
    ;;
esac
