#!/usr/bin/env bash
# Source this file; keep all configuration local to this process.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export QMK_HOME="$ROOT/qmk_firmware"
export QMK_USERSPACE="$ROOT"
export PATH="$ROOT/.venv/bin:/opt/homebrew/opt/make/libexec/gnubin:/opt/homebrew/opt/arm-none-eabi-gcc@8/bin:/opt/homebrew/opt/arm-none-eabi-binutils/bin:$PATH"
mkdir -p "$ROOT/work" "$ROOT/dist"
