#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
WORKDIR="$ROOT_DIR/workdir/scalableui-poc"
IMAGE_ROOT="${AAOS_IMAGE_ROOT:-/mnt/f/aaos_images}"
EMU_IMAGE_ZIP_NAME="sdk-repo-linux-system-images.zip"

source "$WORKDIR/scripts/hmi_variants.sh"

REQUESTED="${1:-}"
if [[ -z "$REQUESTED" ]]; then
  echo "usage: $0 <variant-slug-or-product> [emulator args...]" >&2
  echo "available variants:" >&2
  print_hmi_variants >&2
  exit 1
fi
shift

if ! match="$(find_hmi_product "$REQUESTED")"; then
  echo "error: unknown HMI variant: $REQUESTED" >&2
  echo "available variants:" >&2
  print_hmi_variants >&2
  exit 1
fi

IFS="|" read -r SLUG PRODUCT <<<"$match"
IMAGE_DIR="$IMAGE_ROOT/$SLUG"
PRODUCT_OUT=""

find_extracted_image_dir() {
  local extracted_root="$1"
  local abi
  for abi in x86_64 x86 arm64-v8a armeabi-v7a; do
    if [[ -d "$extracted_root/$abi" ]]; then
      echo "$extracted_root/$abi"
      return 0
    fi
  done
  find "$extracted_root" -mindepth 1 -maxdepth 1 -type d | sort | head -n 1
}

if [[ -d "$IMAGE_DIR/extracted" ]]; then
  PRODUCT_OUT="$(find_extracted_image_dir "$IMAGE_DIR/extracted")"
fi

if [[ ( -z "$PRODUCT_OUT" || ! -d "$PRODUCT_OUT" ) && -f "$IMAGE_DIR/$EMU_IMAGE_ZIP_NAME" ]]; then
  mkdir -p "$IMAGE_DIR/extracted"
  unzip -oq "$IMAGE_DIR/$EMU_IMAGE_ZIP_NAME" -d "$IMAGE_DIR/extracted"
  PRODUCT_OUT="$(find_extracted_image_dir "$IMAGE_DIR/extracted")"
fi

if [[ ( -z "$PRODUCT_OUT" || ! -d "$PRODUCT_OUT" ) && -d "$IMAGE_DIR/product" ]]; then
  # Legacy layout from early PoC scripts. Kept so already-copied raw images still run.
  PRODUCT_OUT="$IMAGE_DIR/product"
fi

if [[ -z "$PRODUCT_OUT" || ! -d "$PRODUCT_OUT" ]]; then
  echo "error: saved image set not found under: $IMAGE_DIR" >&2
  echo "build it first:" >&2
  echo "  AAOS_IMAGE_ROOT=$IMAGE_ROOT $WORKDIR/scripts/build_hmi_emulator_images.sh $SLUG" >&2
  exit 1
fi

EMULATOR_BIN="$ROOT_DIR/prebuilts/android-emulator/linux-x86_64/emulator"
if [[ ! -x "$EMULATOR_BIN" ]]; then
  echo "error: emulator binary not found: $EMULATOR_BIN" >&2
  exit 1
fi

mkdir -p "$IMAGE_DIR/runtime"

export ANDROID_BUILD_TOP="$ROOT_DIR"
export ANDROID_PRODUCT_OUT="$PRODUCT_OUT"
export ANDROID_HOST_OUT="$ROOT_DIR/out/host/linux-x86"

echo "Starting ScalableUI HMI emulator:"
echo "  variant: $SLUG"
echo "  product: $PRODUCT"
echo "  images:  $PRODUCT_OUT"

exec "$EMULATOR_BIN" \
  -sysdir "$PRODUCT_OUT" \
  -datadir "$IMAGE_DIR/runtime" \
  -no-snapshot \
  -wipe-data \
  "$@"
