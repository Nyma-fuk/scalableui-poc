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

BUILD_DIR="${BUILD_DIR:-/tmp/aaos17-threepanel-1080-rro-build}"

if [[ ! -d "${AAOS_ROOT}/build" || ! -f "${AAOS_ROOT}/build/envsetup.sh" ]]; then
    echo "AAOS_ROOT does not look like an Android source tree: ${AAOS_ROOT}" >&2
    exit 1
fi

if [[ ! -d "${VARIANT_DIR}" ]]; then
    echo "Variant source not found: ${VARIANT_DIR}" >&2
    exit 1
fi

mkdir -p "${BUILD_DIR}/flat"
rm -rf "${BUILD_DIR}/flat"
mkdir -p "${BUILD_DIR}/flat"

AAPT2="${AAPT2:-${AAOS_ROOT}/prebuilts/sdk/tools/linux/bin/aapt2}"
ZIPALIGN="${ZIPALIGN:-${AAOS_ROOT}/prebuilts/build-tools/linux-x86/bin/zipalign}"
APKSIGNER_JAR="${APKSIGNER_JAR:-${AAOS_ROOT}/prebuilts/sdk/tools/linux/lib/apksigner.jar}"
ANDROID_JAR="${ANDROID_JAR:-${AAOS_ROOT}/prebuilts/sdk/current/public/android.jar}"
PLATFORM_PK8="${PLATFORM_PK8:-${AAOS_ROOT}/build/make/target/product/security/platform.pk8}"
PLATFORM_CERT="${PLATFORM_CERT:-${AAOS_ROOT}/build/make/target/product/security/platform.x509.pem}"
JAVA_BIN="${JAVA_BIN:-}"
if [[ -z "${JAVA_BIN}" ]]; then
    JAVA_BIN="$(ls "${AAOS_ROOT}"/prebuilts/jdk/*/linux-x86/bin/java | head -1)"
fi

for required in "${AAPT2}" "${ZIPALIGN}" "${APKSIGNER_JAR}" "${ANDROID_JAR}" \
        "${PLATFORM_PK8}" "${PLATFORM_CERT}" "${JAVA_BIN}"; do
    if [[ ! -e "${required}" ]]; then
        echo "Required build input not found: ${required}" >&2
        exit 1
    fi
done

"${AAPT2}" compile --dir "${VARIANT_DIR}/res" -o "${BUILD_DIR}/flat"
find "${BUILD_DIR}/flat" -name '*.flat' | sort > "${BUILD_DIR}/flats.list"
"${AAPT2}" link \
    -o "${BUILD_DIR}/ThreePanel1080RRO-unsigned.apk" \
    --manifest "${VARIANT_DIR}/AndroidManifest.xml" \
    -I "${ANDROID_JAR}" \
    --auto-add-overlay \
    @"${BUILD_DIR}/flats.list"
"${ZIPALIGN}" -f -p 4 \
    "${BUILD_DIR}/ThreePanel1080RRO-unsigned.apk" \
    "${BUILD_DIR}/ThreePanel1080RRO-aligned.apk"
"${JAVA_BIN}" -jar "${APKSIGNER_JAR}" sign \
    --key "${PLATFORM_PK8}" \
    --cert "${PLATFORM_CERT}" \
    --out "${BUILD_DIR}/ThreePanel1080RRO-platform.apk" \
    "${BUILD_DIR}/ThreePanel1080RRO-aligned.apk"

APK_PATH="${BUILD_DIR}/ThreePanel1080RRO-platform.apk"
if [[ ! -f "${APK_PATH}" ]]; then
    echo "ThreePanel1080RRO apk was not generated: ${APK_PATH}" >&2
    exit 1
fi

ADB_ARGS=()
if [[ -n "${ADB_SERIAL}" ]]; then
    ADB_ARGS=(-s "${ADB_SERIAL}")
fi

adb_shell() {
    "${ADB_BIN}" "${ADB_ARGS[@]}" shell "$@"
}

ensure_splitscreen_feature() {
    if adb_shell pm list features | grep -Fq "android.software.car.splitscreen_multitasking"; then
        return 0
    fi

    local feature_xml="${AAOS_ROOT}/packages/services/Car/car_product/dewd/android.software.car.splitscreen_multitasking.xml"
    if [[ ! -f "${feature_xml}" ]]; then
        echo "Missing split-screen feature XML: ${feature_xml}" >&2
        exit 1
    fi

    echo "android.software.car.splitscreen_multitasking is missing; trying to install it into /product/etc/permissions" >&2
    if ! "${ADB_BIN}" "${ADB_ARGS[@]}" root; then
        echo "Failed to restart adbd as root. Start the emulator with -writable-system or use an image that already includes the feature." >&2
        exit 1
    fi
    sleep 2
    if ! "${ADB_BIN}" "${ADB_ARGS[@]}" remount; then
        echo "Failed to remount partitions writable. Start the emulator with -writable-system or include the feature in the image build." >&2
        exit 1
    fi
    "${ADB_BIN}" "${ADB_ARGS[@]}" push "${feature_xml}" \
        /product/etc/permissions/android.software.car.splitscreen_multitasking.xml
    echo "Installed split-screen feature XML. Rebooting before applying the RRO." >&2
    "${ADB_BIN}" "${ADB_ARGS[@]}" reboot
    "${ADB_BIN}" "${ADB_ARGS[@]}" wait-for-device
    for _ in $(seq 1 120); do
        if adb_shell getprop sys.boot_completed 2>/dev/null | tr -d '\r' | grep -q '^1$'; then
            return 0
        fi
        sleep 2
    done
    echo "Timed out waiting for emulator after feature XML install." >&2
    exit 1
}

"${ADB_BIN}" "${ADB_ARGS[@]}" wait-for-device
ensure_splitscreen_feature
"${ADB_BIN}" "${ADB_ARGS[@]}" install -r "${APK_PATH}"
"${ADB_BIN}" "${ADB_ARGS[@]}" shell cmd overlay disable --user 0 com.android.systemui.rro.scalableUI.threePanel.codelab || true
"${ADB_BIN}" "${ADB_ARGS[@]}" shell cmd overlay disable --user 10 com.android.systemui.rro.scalableUI.threePanel.codelab || true
"${ADB_BIN}" "${ADB_ARGS[@]}" shell cmd overlay enable --user 0 com.android.systemui.rro.scalableUI.threePanel1080.codelab
"${ADB_BIN}" "${ADB_ARGS[@]}" shell cmd overlay enable --user 10 com.android.systemui.rro.scalableUI.threePanel1080.codelab || true
"${ADB_BIN}" "${ADB_ARGS[@]}" shell cmd overlay enable-exclusive --user 0 --category com.android.systemui.rro.scalableUI.threePanel1080.codelab
"${ADB_BIN}" "${ADB_ARGS[@]}" shell cmd overlay enable-exclusive --user 10 --category com.android.systemui.rro.scalableUI.threePanel1080.codelab || true

echo "Installed and enabled ${APK_PATH}"
