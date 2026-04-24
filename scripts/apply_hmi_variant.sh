#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
WORKDIR="$ROOT_DIR/workdir/scalableui-poc"
VARIANT="${1:-}"

if [[ -z "$VARIANT" ]]; then
  echo "usage: $0 <variant-slug>" >&2
  echo "example: $0 map-first" >&2
  exit 1
fi

VARIANT_DIR="$WORKDIR/variants/$VARIANT"
if [[ ! -d "$VARIANT_DIR" ]]; then
  echo "error: unknown HMI variant: $VARIANT" >&2
  echo "available variants:" >&2
  find "$WORKDIR/variants" -mindepth 1 -maxdepth 1 -type d -printf '  %f\n' | sort >&2
  exit 1
fi

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
    echo "No changes were applied for this patch. Use a clean AAOS15 checkout or inspect the overlapping files." >&2
    exit 1
  fi

  git -C "$repo_path" apply "$patch_path"
  echo "applied: $patch_rel"
}

variant_device_patch="$(find "$VARIANT_DIR/patches/device-generic-car" -maxdepth 1 -name '*.patch' | sort | head -n 1)"
variant_services_patch="$(find "$VARIANT_DIR/patches/packages-services-Car" -maxdepth 1 -name '*.patch' | sort | head -n 1)"

if [[ -z "$variant_device_patch" || -z "$variant_services_patch" ]]; then
  echo "error: missing generated patches for variant: $VARIANT" >&2
  exit 1
fi

variant_device_rel="${variant_device_patch#"$WORKDIR/"}"
variant_services_rel="${variant_services_patch#"$WORKDIR/"}"

apply_one_patch "device/generic/car" "$variant_device_rel"
for patch_path in "$WORKDIR"/common/patches/packages-services-Car/*.patch; do
  rel="${patch_path#"$WORKDIR/"}"
  apply_one_patch "packages/services/Car" "$rel"
done
apply_one_patch "packages/services/Car" "$variant_services_rel"
apply_one_patch "packages/apps/Car/SystemUI" "patches/packages-apps-Car-SystemUI/0001-app-grid-launch-root-and-grip-fixes.patch"
apply_one_patch "packages/apps/Car/Launcher" "patches/packages-apps-Car-Launcher/0001-all-apps-launch-to-app-panel.patch"

echo "ScalableUI HMI variant '$VARIANT' patches are in place."
