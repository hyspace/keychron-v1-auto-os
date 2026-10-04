# Project rules

- This repository is QMK External Userspace. Edit `keyboards/.../auto_os/`, not
  the ignored `qmk_firmware/` checkout. Keep QMK locked by tag and SHA in
  `data/upstream.lock.json`; upstream upgrades are separate reviewed changes.
- OS policy: macOS/iOS -> Mac; Windows/Linux -> Win; unsure -> unchanged.
  Preserve the physical switch override and the 11 Keychron Custom keys.
- Never commit `backups/`, `work/`, raw flash, raw VIA macros, device serials or
  credentials. The layout source and sanitized fixtures are intentionally tracked.
- Run `bash scripts/build.sh` and `bash scripts/test.sh`. Version changes also
  update `VERSION`, `VIA_FIRMWARE_VERSION`, generated VIA definition and changelog.
- Keep `data/expected-keymap.json` an independently reviewed baseline. Do not
  automatically overwrite it just to make a failing test pass.
- A successful compile/CI is not a hardware test. Preserve exact binary hashes,
  distinguish user-reported checks from measured results, and never flash as part
  of repository organization or an upstream update without user authorization.
- Use `docs/` for requirements, design, upgrade and test history; keep README short.
