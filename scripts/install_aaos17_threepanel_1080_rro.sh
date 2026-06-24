#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VARIANT_DIR="${REPO_ROOT}/variants/aaos17-codelab-threepanel-1080/rro/ThreePanel1080RRO"

AAOS_ROOT="${AAOS_ROOT:?set AAOS_ROOT to the Android 17 source tree root}"
TARGET_PRODUCT="${TARGET_PRODUCT:-sdk_car_x86_64-trunk_staging}"
TARGET_VARIANT="${TARGET_VARIANT:-userdebug}"
ADB_BIN="${ADB_BIN:-adb}"
ADB_SERIAL="${ADB_SERIAL:-}"

DEST_DIR="${AAOS_ROOT}/packages/apps/Car/References/scalable-ui/codelab/ThreePanel1080RRO"

if [[ ! -d "${AAOS_ROOT}/build" || ! -f "${AAOS_ROOT}/build/envsetup.sh" ]]; then
    echo "AAOS_ROOT does not look like an Android source tree: ${AAOS_ROOT}" >&2
    exit 1
fi

if [[ ! -d "${VARIANT_DIR}" ]]; then
    echo "Variant source not found: ${VARIANT_DIR}" >&2
    exit 1
fi

mkdir -p "$(dirname "${DEST_DIR}")"
rm -rf "${DEST_DIR}"
cp -a "${VARIANT_DIR}" "${DEST_DIR}"

(
    cd "${AAOS_ROOT}"
    # shellcheck disable=SC1091
    source build/envsetup.sh
    lunch "${TARGET_PRODUCT}-${TARGET_VARIANT}"
    SOONG_NINJA="${SOONG_NINJA:-ninja}" m ThreePanel1080RRO
)

APK_PATH="$(find "${AAOS_ROOT}/out/target/product" -path '*/ThreePanel1080RRO.apk' -type f | head -1)"
if [[ -z "${APK_PATH}" ]]; then
    echo "ThreePanel1080RRO.apk was not found under ${AAOS_ROOT}/out/target/product" >&2
    exit 1
fi

ADB_ARGS=()
if [[ -n "${ADB_SERIAL}" ]]; then
    ADB_ARGS=(-s "${ADB_SERIAL}")
fi

"${ADB_BIN}" "${ADB_ARGS[@]}" wait-for-device
"${ADB_BIN}" "${ADB_ARGS[@]}" install -r "${APK_PATH}"
"${ADB_BIN}" "${ADB_ARGS[@]}" shell cmd overlay disable --user 0 com.android.systemui.rro.scalableUI.threePanel.codelab || true
"${ADB_BIN}" "${ADB_ARGS[@]}" shell cmd overlay disable --user 10 com.android.systemui.rro.scalableUI.threePanel.codelab || true
"${ADB_BIN}" "${ADB_ARGS[@]}" shell cmd overlay enable --user 0 com.android.systemui.rro.scalableUI.threePanel1080.codelab
"${ADB_BIN}" "${ADB_ARGS[@]}" shell cmd overlay enable --user 10 com.android.systemui.rro.scalableUI.threePanel1080.codelab || true

echo "Installed and enabled ${APK_PATH}"
