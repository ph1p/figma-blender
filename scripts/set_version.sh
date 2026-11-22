#!/usr/bin/env bash
# Write one release version into every place that carries it.
#   scripts/set_version.sh 1.2.3
set -euo pipefail

version="${1:?usage: set_version.sh <version>}"
root="$(cd "$(dirname "$0")/.." && pwd)"

if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
	echo "Not a plain semver version: $version" >&2
	exit 1
fi

# Blender rejects pre-release suffixes, so only X.Y.Z gets this far.
# perl instead of sed: in-place flags differ between GNU and BSD sed.
perl -pi -e "s/^version = \".*\"\$/version = \"$version\"/" "$root/addon/blender_manifest.toml"
# First "version" key only: the top-level one, not anything nested.
perl -0pi -e "s/\"version\": \"[^\"]*\"/\"version\": \"$version\"/" "$root/plugin/package.json"

grep -n '^version' "$root/addon/blender_manifest.toml"
grep -n '"version"' "$root/plugin/package.json"
