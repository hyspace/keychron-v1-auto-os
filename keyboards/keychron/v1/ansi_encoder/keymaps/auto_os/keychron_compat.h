/* Copyright 2022 @ Keychron (https://www.keychron.com)
 * SPDX-License-Identifier: GPL-2.0-or-later
 */
#pragma once
#include "quantum.h"

// Order matches the official VIA customKeycodes array; use current QMK IDs.
enum keychron_custom_keycodes {
    KCH_MISSION_CONTROL = QK_KB_0,
    KCH_LAUNCHPAD,
    KCH_LEFT_OPTION,
    KCH_RIGHT_OPTION,
    KCH_LEFT_COMMAND,
    KCH_RIGHT_COMMAND,
    KCH_SIRI,
    KCH_TASK_VIEW,
    KCH_FILE_EXPLORER,
    KCH_SCREENSHOT,
    KCH_CORTANA,
};

_Static_assert((uint16_t)KCH_CORTANA == (uint16_t)QK_KB_10, "VIA custom keycode order changed");
