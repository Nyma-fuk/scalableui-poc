#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
WORKDIR="$ROOT_DIR/workdir/scalableui-poc"
IMAGE_ROOT="${AAOS_IMAGE_ROOT:-/mnt/f/aaos_images}"

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
PRODUCT_OUT="$IMAGE_DIR/product"

if [[ ! -d "$PRODUCT_OUT" ]]; then
  echo "error: saved image set not found: $PRODUCT_OUT" >&2
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
