#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
WORKDIR="$ROOT_DIR/workdir/scalableui-poc"

PATCH_TARGETS=(
  "device/generic/car|patches/device-generic-car/0001-add-sdk_car_scalableui_x86_64-product.patch"
  "packages/services/Car|patches/packages-services-Car/0001-add-scalableui-poc-rro.patch"
  "packages/apps/Car/SystemUI|patches/packages-apps-Car-SystemUI/0001-app-grid-launch-root-and-grip-fixes.patch"
  "packages/apps/Car/Launcher|patches/packages-apps-Car-Launcher/0001-all-apps-launch-to-app-panel.patch"
)

require_repo() {
  local repo_path="$1"
  if [[ ! -d "$repo_path" ]]; then
    echo "error: missing repo directory: $repo_path" >&2
    exit 1
  fi
  git -C "$repo_path" rev-parse --show-toplevel >/dev/null
}

extract_paths_from_patch() {
  local patch_file="$1"
  awk '
    /^\+\+\+ b\// {
      path = substr($0, 7)
      if (path != "/dev/null") {
        print path
      }
    }
  ' "$patch_file" | sort -u
}

ensure_no_local_overlap() {
  local repo_path="$1"
  local patch_file="$2"
  local -a patch_paths=()
  mapfile -t patch_paths < <(extract_paths_from_patch "$patch_file")
  if [[ ${#patch_paths[@]} -eq 0 ]]; then
    return
  fi

  local status
  status="$(git -C "$repo_path" status --short -- "${patch_paths[@]}")"
  if [[ -n "$status" ]]; then
    echo "error: local changes overlap with patch $patch_file in $repo_path" >&2
    echo "$status" >&2
    echo "Resolve or stash those files first so this script does not overwrite local work." >&2
    exit 1
  fi
}

apply_one_patch() {
  local repo_rel="$1"
  local patch_rel="$2"
  local repo_path="$ROOT_DIR/$repo_rel"
  local patch_path="$WORKDIR/$patch_rel"

  require_repo "$repo_path"
  if [[ ! -f "$patch_path" ]]; then
    echo "error: missing patch file: $patch_path" >&2
    exit 1
  fi

  if git -C "$repo_path" apply --reverse --check "$patch_path" >/dev/null 2>&1; then
    echo "skip: already applied: $patch_rel"
    return
  fi

  ensure_no_local_overlap "$repo_path" "$patch_path"

  if ! git -C "$repo_path" apply --check "$patch_path"; then
    echo "error: patch does not apply cleanly: $patch_rel" >&2
    echo "The target checkout may differ from the expected AAOS15 base. No changes were applied." >&2
    exit 1
  fi

  git -C "$repo_path" apply "$patch_path"
  echo "applied: $patch_rel"
}

for target in "${PATCH_TARGETS[@]}"; do
  IFS="|" read -r repo_rel patch_rel <<<"$target"
  apply_one_patch "$repo_rel" "$patch_rel"
done

echo "ScalableUI PoC patches are in place."
