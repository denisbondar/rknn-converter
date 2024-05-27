#!/usr/bin/env bash
set -Eeuo pipefail

DIRNAME=$(realpath "$0" | sed 's|\(.*\)/.*|\1|')
TMPDIR="$DIRNAME"/tmp

echo
echo "Begin"
echo

rm -rf "$TMPDIR"
mkdir -p "$TMPDIR"

PYTHON_VERSIONS=("cp310" "cp311")

for VERSION in "${PYTHON_VERSIONS[@]}"
do
  URL=https://github.com/airockchip/rknn-toolkit2/raw/v1.6.0/rknn-toolkit2/packages/rknn_toolkit2-1.6.0+81f21f4d-${VERSION}-${VERSION}-linux_x86_64.whl
  WHL=$(basename "$URL")
  echo "Download ${WHL}"
  wget -q -O "$DIRNAME"/"$WHL" "$URL"
  echo "Unpack ${WHL}"
  wheel3.11 unpack -d "$TMPDIR" "$DIRNAME"/"$WHL"
  echo "Apply fixes for ${WHL}"
  sed -i "s@torch (==1.13.1)@torch (>=1.8.0)@g" "$TMPDIR"/rknn_toolkit2-1.6.0+81f21f4d/rknn_toolkit2-1.6.0+81f21f4d.dist-info/METADATA
  echo "Pack to ${WHL}"
  wheel3.11 pack -d "$DIRNAME" "$TMPDIR"/rknn_toolkit2-1.6.0+81f21f4d
  rm -rf "$TMPDIR"/rknn_toolkit2-1.6.0+81f21f4d
done

rm -rf "$TMPDIR"

echo
echo "Done!"
echo