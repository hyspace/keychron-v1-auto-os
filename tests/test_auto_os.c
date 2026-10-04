#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../keyboards/keychron/v1/ansi_encoder/keymaps/auto_os/auto_os.c"
#define DIP_SWITCH_ENABLE
#include "../qmk_firmware/keyboards/keychron/v1/v1.c"

uint32_t default_layer_state;
static unsigned set_calls;
static unsigned send_calls;
static uint8_t sent[32];
static os_variant_t guess = OS_MACOS;

void default_layer_set(uint32_t value) { default_layer_state = value; ++set_calls; }
uint8_t get_highest_layer(uint32_t value) {
    uint8_t result = 0;
    while (value >>= 1) { ++result; }
    return result;
}
uint32_t timer_read32(void) { return 0x01234567; }
os_variant_t detected_host_os(void) { return guess; }
bool dip_switch_update_user(uint8_t index, bool active) {
    (void)index; (void)active; return true;
}
void raw_hid_send(uint8_t *data, uint8_t length) {
    assert(length == 32); memcpy(sent, data, length); ++send_calls;
}

int main(void) {
    dip_switch_update_kb(0, true);
    assert(default_layer_state == (1UL << WIN_BASE));
    assert(process_detected_host_os_user(OS_MACOS));
    assert(default_layer_state == (1UL << MAC_BASE));
    process_detected_host_os_user(OS_WINDOWS);
    assert(default_layer_state == (1UL << WIN_BASE));
    process_detected_host_os_user(OS_IOS);
    assert(default_layer_state == (1UL << MAC_BASE));

    // A Mac layout must not survive a recognized Linux host (the reported bug).
    process_detected_host_os_user(OS_LINUX);
    assert(default_layer_state == (1UL << WIN_BASE));
    process_detected_host_os_user(OS_MACOS);
    assert(default_layer_state == (1UL << MAC_BASE));
    unsigned previous = set_calls;
    process_detected_host_os_user(OS_UNSURE);
    assert(set_calls == previous && default_layer_state == (1UL << MAC_BASE));

    dip_switch_update_kb(0, true);
    previous = set_calls;
    process_detected_host_os_user(OS_UNSURE);
    assert(set_calls == previous);
    assert(default_layer_state == (1UL << WIN_BASE));

    const os_variant_t hosts[] = {OS_MACOS, OS_IOS, OS_WINDOWS, OS_LINUX};
    const uint8_t bases[] = {MAC_BASE, MAC_BASE, WIN_BASE, WIN_BASE};
    for (unsigned from = 0; from < 4; ++from) {
        for (unsigned to = 0; to < 4; ++to) {
            process_detected_host_os_user(hosts[from]);
            process_detected_host_os_user(hosts[to]);
            assert(default_layer_state == (1UL << bases[to]));
        }
    }

    // The manual Mac override remains available even on a detected Linux host.
    process_detected_host_os_user(OS_LINUX);
    dip_switch_update_kb(0, false);
    assert(default_layer_state == (1UL << MAC_BASE));
    uint8_t linux_packet[32] = {0x02, 0x80};
    guess = OS_LINUX;
    assert(via_command_kb(linux_packet, 32));
    assert(sent[6] == OS_LINUX && sent[7] == MAC_BASE && sent[9] == OS_LINUX);
    send_calls = 0;
    guess = OS_MACOS;

    process_detected_host_os_user(OS_WINDOWS);
    dip_switch_update_kb(0, false);
    assert(default_layer_state == (1UL << MAC_BASE));
    previous = set_calls;
    dip_switch_update_kb(1, true);
    assert(set_calls == previous);

    uint8_t packet[32] = {0x02, 0x80};
    assert(via_command_kb(packet, 32));
    assert(send_calls == 1 && set_calls == previous);
    assert(memcmp(sent + 2, "AOS1", 4) == 0);
    assert(sent[6] == OS_WINDOWS && sent[7] == MAC_BASE);
    assert(sent[8] == 1 && sent[9] == OS_MACOS);
    assert(memcmp(sent + 10, "\x01\x23\x45\x67", 4) == 0);
    packet[0] = 0x03;
    assert(!via_command_kb(packet, 32));
    packet[0] = 0x02; packet[1] = 0x04;
    assert(!via_command_kb(packet, 32));
    packet[1] = 0x80;
    assert(!via_command_kb(packet, 13));
    assert(send_calls == 1);
    puts("PASS: 16 OS transitions incl. Mac/Linux, unknown fallback, manual override, diagnostics");
}
