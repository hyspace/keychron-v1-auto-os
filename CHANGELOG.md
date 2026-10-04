# Changelog

## Repository organization (no firmware behavior change)

- Move to QMK External Userspace; lock QMK by tag and exact SHA.
- Keep QMK core/hardware files unmodified. Add build/test CI and provenance packaging.
- Separate private flash/VIA backups and scratch downloads from publishable source.
- Document requirements, architecture, QMK upgrades and hardware-test evidence.

## 1.1.1 - 2026-10-04

- Linux now selects Windows base layer; macOS/iOS use Mac; unsure preserves current.
- Add transition/fallback/diagnostic tests. No changes to existing keymap or Custom handlers.
- Flashed, read back, direct Mac tested; user subsequently confirmed completion.

## 1.1.0 - 2026-10-04

- Complete all 11 Keychron Custom handlers and matched VIA v3 definition.
- Preserve saved keymap/encoder settings; migrate legacy Custom/RGB codes.
- Add read-only OS diagnostics, RGB enum checks and firmware readback verification.

## 1.0.0 - 2026-10-04 (not flashed)

- Initial QMK 0.34.6 OS-detection integration with physical switch fallback and VIA.
- Only existing Custom assignments translated; superseded by full compatibility in 1.1.0.
