// SPDX-License-Identifier: GPL-2.0-or-later
#include "quantum.h"
#include "os_detection.h"
#include "raw_hid.h"
#include "auto_os.h"

static os_variant_t applied_os = OS_UNSURE;
static bool detection_reported = false;

bool process_detected_host_os_user(os_variant_t os) {
    applied_os = os;
    detection_reported = true;
    switch (os) {
        case OS_MACOS:
        case OS_IOS:
            default_layer_set(1UL << MAC_BASE);
            break;
        case OS_WINDOWS:
        case OS_LINUX:
            default_layer_set(1UL << WIN_BASE);
            break;
        default:
            // Keep the physical switch's choice when detection is inconclusive.
            break;
    }
    return true;
}

// Read-only diagnostic value on the existing VIA interface; no extra USB interface.
bool via_command_kb(uint8_t *data, uint8_t length) {
    if (length < 14 || data[0] != 0x02 || data[1] != 0x80) {
        return false;
    }
    for (uint8_t i = 2; i < length; ++i) {
        data[i] = 0;
    }
    data[2] = 'A';
    data[3] = 'O';
    data[4] = 'S';
    data[5] = '1';
    data[6] = applied_os;
    data[7] = get_highest_layer(default_layer_state);
    data[8] = detection_reported;
    data[9] = detected_host_os();
    uint32_t uptime = timer_read32();
    data[10] = uptime >> 24;
    data[11] = uptime >> 16;
    data[12] = uptime >> 8;
    data[13] = uptime;
    raw_hid_send(data, length);
    return true;
}
