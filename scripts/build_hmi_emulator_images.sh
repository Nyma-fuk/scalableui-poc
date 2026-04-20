#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
WORKDIR="$ROOT_DIR/workdir/scalableui-poc"
IMAGE_ROOT="${AAOS_IMAGE_ROOT:-/mnt/f/aaos_images}"
JOBS="${JOBS:-$(nproc)}"
BUILD_TARGET="${BUILD_TARGET:-}"

source "$WORKDIR/scripts/hmi_variants.sh"

if [[ ! -d "$IMAGE_ROOT" ]]; then
  mkdir -p "$IMAGE_ROOT"
fi

if [[ $# -gt 0 ]]; then
  SELECTED=()
  for requested in "$@"; do
    if ! match="$(find_hmi_product "$requested")"; then
      echo "error: unknown HMI variant: $requested" >&2
      echo "available variants:" >&2
      print_hmi_variants >&2
      exit 1
    fi
    SELECTED+=("$match")
  done
else
  SELECTED=("${HMI_VARIANTS[@]}")
fi

cd "$ROOT_DIR"
source build/envsetup.sh >/dev/null

copy_product_out() {
  local slug="$1"
  local product="$2"
  local dest="$IMAGE_ROOT/$slug"
  local product_dest="$dest/product"

  rm -rf "$dest"
  mkdir -p "$product_dest"

  cp -a "$ANDROID_PRODUCT_OUT"/. "$product_dest/"
  cat >"$dest/manifest.txt" <<EOF
slug=$slug
product=$product
lunch=${product}-trunk_staging-userdebug
build_top=$ROOT_DIR
android_product_out=$ANDROID_PRODUCT_OUT
saved_product_out=$product_dest
saved_at=$(date -Iseconds)
EOF

  cat >"$dest/run.sh" <<EOF
#!/bin/bash
set -euo pipefail
SCRIPT_DIR="\\$(cd "\\$(dirname "\\$0")" && pwd)"
"$WORKDIR/scripts/run_hmi_emulator.sh" "$slug" "\\$@"
EOF
  chmod +x "$dest/run.sh"
}

for entry in "${SELECTED[@]}"; do
  IFS="|" read -r slug product <<<"$entry"
  echo "==> lunch ${product}-trunk_staging-userdebug"
  lunch "${product}-trunk_staging-userdebug"

  echo "==> installclean"
  m installclean

  if [[ -n "$BUILD_TARGET" ]]; then
    echo "==> build $BUILD_TARGET with -j$JOBS"
    m -j"$JOBS" "$BUILD_TARGET"
  else
    echo "==> build full product with -j$JOBS"
    m -j"$JOBS"
  fi

  echo "==> save image set to $IMAGE_ROOT/$slug"
  copy_product_out "$slug" "$product"
done

cat >"$IMAGE_ROOT/README.txt" <<EOF
ScalableUI HMI emulator images

Build top:
  $ROOT_DIR

Run examples:
  $WORKDIR/scripts/run_hmi_emulator.sh map-first
  $IMAGE_ROOT/map-first/run.sh

Available image sets:
EOF

for entry in "${HMI_VARIANTS[@]}"; do
  IFS="|" read -r slug product <<<"$entry"
  if [[ -d "$IMAGE_ROOT/$slug/product" ]]; then
    echo "  $slug ($product)" >>"$IMAGE_ROOT/README.txt"
  fi
done

echo "All requested HMI emulator images are saved under $IMAGE_ROOT."
