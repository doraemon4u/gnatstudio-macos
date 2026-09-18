#!/usr/bin/env bash
set -euo pipefail

OVERLAY_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_REPO="${1:-$(pwd)}"

if [[ ! -d "$TARGET_REPO/.git" ]]; then
  echo "usage: $0 /path/to/gnatstudio-checkout" >&2
  exit 2
fi

install -m 0644 "$OVERLAY_DIR/Makefile.in" "$TARGET_REPO/osx_bundle/Makefile.in"
install -m 0644 "$OVERLAY_DIR/srcs/Info.plist" "$TARGET_REPO/osx_bundle/srcs/Info.plist"
install -m 0755 "$OVERLAY_DIR/srcs/gps_bundle_main" "$TARGET_REPO/osx_bundle/srcs/gps_bundle_main"
install -m 0755 "$OVERLAY_DIR/srcs/gps_command_line" "$TARGET_REPO/osx_bundle/srcs/gps_command_line"
install -m 0644 "$OVERLAY_DIR/scripts/bundle_python.py" "$TARGET_REPO/osx_bundle/scripts/bundle_python.py"
install -m 0755 "$OVERLAY_DIR/scripts/bundle_dylibs.sh" "$TARGET_REPO/osx_bundle/scripts/bundle_dylibs.sh"

printf 'Applied GNAT Studio macOS 27 bundle overlay to %s\n' "$TARGET_REPO"
printf 'Review with: git -C %q diff -- osx_bundle\n' "$TARGET_REPO"
