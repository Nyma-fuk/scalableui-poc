#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../.." && pwd)"
WORKDIR="$ROOT_DIR/workdir/scalableui-poc"

generate_patch() {
  local repo_rel="$1"
  local patch_rel="$2"
  shift 2
  local repo_path="$ROOT_DIR/$repo_rel"
  local patch_path="$WORKDIR/$patch_rel"
  local patch_dir
  patch_dir="$(dirname "$patch_path")"
  mkdir -p "$patch_dir"

  local tmp_patch
  tmp_patch="$(mktemp)"

  (
    cd "$repo_path"
    local tracked_files=()
    local new_files=()
    local mode="tracked"
    for item in "$@"; do
      if [[ "$item" == "--new-files" ]]; then
        mode="new"
        continue
      fi
      if [[ "$mode" == "tracked" ]]; then
        tracked_files+=("$item")
      else
        new_files+=("$item")
      fi
    done

    if [[ ${#tracked_files[@]} -gt 0 ]]; then
      git diff --binary --full-index -- "${tracked_files[@]}" >> "$tmp_patch"
    fi
    if [[ ${#new_files[@]} -gt 0 ]]; then
      for file in "${new_files[@]}"; do
        git diff --binary --full-index --no-index -- /dev/null "$file" >> "$tmp_patch" || true
      done
    fi
  )

  mv "$tmp_patch" "$patch_path"
  echo "exported: $patch_rel"
}

generate_patch \
  "device/generic/car" \
  "patches/device-generic-car/0001-add-sdk_car_scalableui_x86_64-product.patch" \
  "AndroidProducts.mk" \
  --new-files \
  "sdk_car_scalableui_x86_64.mk"

generate_patch \
  "packages/services/Car" \
  "patches/packages-services-Car/0001-add-scalableui-poc-rro.patch" \
  --new-files \
  "car_product/scalableui_poc/car_scalableui_poc.mk" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/Android.bp" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/AndroidManifest.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/drawable/poc_grip_bar_background.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/layout/scalableui_left_background_panel.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/config.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/dimens.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/integers.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/values/strings.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/app_panel.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/calendar_panel.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/decor_horizontal_grip_panel.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/decor_left_background_panel.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/decor_vertical_grip_panel.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/horizontal_grip_controller.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/map_panel.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/overlays.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/panel_app_grid.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/radio_panel.xml" \
  "car_product/scalableui_poc/rro/CarSystemUIScalableUiPocRRO/res/xml/vertical_grip_controller.xml" \
  "car_product/scalableui_poc/rro/rro.mk"

generate_patch \
  "packages/apps/Car/SystemUI" \
  "patches/packages-apps-Car-SystemUI/0001-app-grid-launch-root-and-grip-fixes.patch" \
  "src/com/android/systemui/car/wm/scalableui/PanelAutoTaskStackTransitionHandlerDelegate.java" \
  "src/com/android/systemui/car/wm/scalableui/systemevents/SystemEventHandler.java" \
  "src/com/android/systemui/car/wm/scalableui/panel/TaskPanelInfoRepository.java" \
  "src/com/android/systemui/car/wm/scalableui/view/GripBarViewController.java" \
  "tests/src/com/android/systemui/car/wm/scalableui/PanelAutoTaskStackTransitionHandlerDelegateTest.java"

generate_patch \
  "packages/apps/Car/Launcher" \
  "patches/packages-apps-Car-Launcher/0001-all-apps-launch-to-app-panel.patch" \
  "app/AndroidManifest.xml" \
  "libs/appgrid/lib/src/com/android/car/carlauncher/recyclerview/AppItemViewHolder.java" \
  "libs/appgrid/lib/src/com/android/car/carlauncher/repositories/appactions/AppLaunchProvider.kt"

echo "Exported ScalableUI PoC patches into $WORKDIR/patches"
