#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
python "$ROOT/scripts/check_upstream.py"
python "$ROOT/scripts/generate_via_definition.py"
cd "$QMK_HOME"
qmk compile -kb keychron/v1/ansi_encoder -km auto_os -j 4
