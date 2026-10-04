#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/env.sh"
cd "$ROOT"
for test in auto_os keychron_compat; do
    clang -std=c11 -Wall -Wextra -Werror -I tests/stubs "tests/test_$test.c" -o "work/test_$test"
    "work/test_$test"
done
.venv/bin/python -m unittest discover -s tests -p 'test_*.py' -v
node scripts/validate_via.cjs 2> work/via-validator-warnings.log
.venv/bin/python scripts/verify_firmware.py
