/* Copyright 2022 @ Keychron (https://www.keychron.com)
 * SPDX-License-Identifier: GPL-2.0-or-later
 *
 * Adapted from Keychron/qmk_firmware, commit
 * 0456ffb38e67160e2c59a91ab00f424d3765f1f6,
 * keyboards/keychron/common/keychron_common.c.
 * Preserve the official HID sequences and the 500 ms Siri timer.
 */
#include "keychron_compat.h"

static bool siri_active;
static uint32_t siri_timer;

static const uint8_t single_keys[] = {
    KC_MISSION_CONTROL, KC_LAUNCHPAD, KC_LOPT, KC_ROPT, KC_LCMD, KC_RCMD,
};

static const struct {
    uint8_t count;
    uint8_t keys[3];
} combinations[] = {
    {2, {KC_LWIN, KC_TAB}},
    {2, {KC_LWIN, KC_E}},
    {3, {KC_LSFT, KC_LCMD, KC_4}},
    {2, {KC_LWIN, KC_C}},
};

bool process_record_user(uint16_t keycode, keyrecord_t *record) {
    if (keycode >= KCH_MISSION_CONTROL && keycode <= KCH_RIGHT_COMMAND) {
        uint8_t key = single_keys[keycode - KCH_MISSION_CONTROL];
        if (record->event.pressed) {
            register_code(key);
        } else {
            unregister_code(key);
        }
        return false;
    }

    if (keycode == KCH_SIRI) {
        if (record->event.pressed) {
            if (!siri_active) {
                siri_active = true;
                register_code(KC_LCMD);
                register_code(KC_SPACE);
            }
            siri_timer = timer_read32();
        }
        return false;
    }

    if (keycode >= KCH_TASK_VIEW && keycode <= KCH_CORTANA) {
        uint8_t index = keycode - KCH_TASK_VIEW;
        for (uint8_t i = 0; i < combinations[index].count; ++i) {
            if (record->event.pressed) {
                register_code(combinations[index].keys[i]);
            } else {
                unregister_code(combinations[index].keys[i]);
            }
        }
        return false;
    }
    return true;
}

void housekeeping_task_user(void) {
    if (siri_active && timer_elapsed32(siri_timer) >= 500) {
        unregister_code(KC_LCMD);
        unregister_code(KC_SPACE);
        siri_active = false;
    }
}
