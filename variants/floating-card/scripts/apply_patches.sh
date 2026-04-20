#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/../../../../.." && pwd)"
exec "$ROOT_DIR/workdir/scalableui-poc/scripts/apply_hmi_variant.sh" "floating-card"
