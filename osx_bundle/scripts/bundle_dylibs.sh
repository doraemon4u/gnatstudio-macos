#!/usr/bin/env bash
set -euo pipefail

ROOT=${1:?bundle root is required (Contents/MacOS)}
FRAMEWORKS=${2:?framework directory is required (Contents/Frameworks)}

mkdir -p "$FRAMEWORKS"

DYLIBBUNDLER="$(command -v dylibbundler)"
[[ -x "$DYLIBBUNDLER" ]] || { echo "dylibbundler not found" >&2; exit 1; }

bundle_one() {
    local target="$1"
    [[ -f "$target" ]] || return 0
    if ! file -b "$target" | grep -q 'Mach-O'; then
        return 0
    fi

    echo "Bundling dependencies of: $target"
    "$DYLIBBUNDLER" \
        -od \
        -b \
        -x "$target" \
        -d "$FRAMEWORKS" \
        -p '@executable_path/../../Frameworks'
}

# Main executable and GTK utility.
bundle_one "$ROOT/bin/gnatstudio_exe"
bundle_one "$ROOT/bin/gdk-pixbuf-query-loaders"

# GTK plugins, GI modules, Python extensions and any copied dylibs.
while IFS= read -r -d '' target; do
    bundle_one "$target"
done < <(
    find "$ROOT" -type f \( \
        -name '*.dylib' -o \
        -name '*.so' -o \
        -name '*.bundle' \
    \) -print0
)

# Remove dependency artifacts dylibbundler may leave in the framework folder
# when a source file was encountered more than once.
find "$FRAMEWORKS" -type f -name '*.la' -delete
