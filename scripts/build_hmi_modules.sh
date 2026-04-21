#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
WORKDIR="$ROOT_DIR/workdir/scalableui-poc"
JOBS="${JOBS:-$(nproc)}"

source "$WORKDIR/scripts/hmi_variants.sh"
mapfile -t DEMO_APP_MODULES < <(hmi_demo_app_modules)

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
set +u
source build/envsetup.sh >/dev/null
set -u

for entry in "${SELECTED[@]}"; do
  IFS="|" read -r slug product <<<"$entry"
  rro_module="$(hmi_rro_module_for_slug "$slug")"

  echo "==> lunch ${product}-trunk_staging-userdebug"
  set +u
  lunch "${product}-trunk_staging-userdebug"
  set -u

  echo "==> build demo app/RRO modules for $slug with -j$JOBS"
  m -j"$JOBS" "${DEMO_APP_MODULES[@]}" "$rro_module"
done

echo "All requested HMI app/RRO modules built successfully."
