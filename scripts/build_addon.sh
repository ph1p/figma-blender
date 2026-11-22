#!/usr/bin/env bash
# Build the Blender extension zip (for Gumroad or extensions.blender.org).
#
#   scripts/build_addon.sh            -> dist/figma_connect-<version>.zip
#   BLENDER=/path/to/blender scripts/build_addon.sh
set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"

blender="${BLENDER:-}"
if [[ -z "$blender" ]]; then
	if command -v blender >/dev/null 2>&1; then
		blender="$(command -v blender)"
	elif [[ -x /Applications/Blender.app/Contents/MacOS/Blender ]]; then
		blender=/Applications/Blender.app/Contents/MacOS/Blender
	else
		echo "Blender not found. Set BLENDER=/path/to/blender." >&2
		exit 1
	fi
fi

mkdir -p "$root/dist"
# Old zips would also match the release asset glob.
rm -f "$root"/dist/figma_connect-*.zip
find "$root/addon" -name __pycache__ -type d -prune -exec rm -rf {} +

"$blender" --factory-startup --command extension validate "$root/addon"
"$blender" --factory-startup --command extension build \
	--source-dir "$root/addon" \
	--output-dir "$root/dist"

ls -1 "$root"/dist/*.zip
