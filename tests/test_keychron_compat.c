#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "../keyboards/keychron/v1/ansi_encoder/keymaps/auto_os/keychron_compat.c"

static uint32_t now;
static struct { bool pressed; uint8_t key; } events[128];
static unsigned count;
uint32_t timer_read32(void) { return now; }
uint32_t timer_elapsed32(uint32_t start) { return now - start; }
void register_code(uint8_t key) { events[count].pressed = true; events[count++].key = key; }
void unregister_code(uint8_t key) { events[count].pressed = false; events[count++].key = key; }

static bool key(uint16_t code, bool pressed) {
    keyrecord_t record = {.event = {.pressed = pressed}};
    return process_record_user(code, &record);
}

static void test_sequence(uint16_t code, const uint8_t *keys, unsigned length) {
    count = 0;
    assert(!key(code, true));
    assert(!key(code, false));
    assert(count == length * 2);
    for (unsigned i = 0; i < length; ++i) {
        assert(events[i].pressed && events[i].key == keys[i]);
        assert(!events[length + i].pressed && events[length + i].key == keys[i]);
    }
}

int main(void) {
    const uint8_t singles[] = {KC_MCTL, KC_LPAD, KC_LALT, KC_RALT, KC_LGUI, KC_RGUI};
    for (unsigned i = 0; i < 6; ++i) { test_sequence(QK_KB_0 + i, &singles[i], 1); }
    const uint8_t task[] = {KC_LGUI, KC_TAB};
    const uint8_t explorer[] = {KC_LGUI, KC_E};
    const uint8_t screenshot[] = {KC_LSFT, KC_LGUI, KC_4};
    const uint8_t cortana[] = {KC_LGUI, KC_C};
    test_sequence(QK_KB_7, task, 2);
    test_sequence(QK_KB_8, explorer, 2);
    test_sequence(QK_KB_9, screenshot, 3);
    test_sequence(QK_KB_10, cortana, 2);
    count = 0;
    assert(key(KC_A, true) && key(KC_A, false));
    assert(key(RM_TOGG, true) && key(QK_KB_11, true));
    assert(key(0x7F00, true)); // Legacy IDs are migrated, not aliased over QK_USER.
    assert(count == 0);

    now = 1000;
    assert(!key(QK_KB_6, true));
    assert(count == 2 && events[0].key == KC_LGUI && events[1].key == KC_SPACE);
    assert(events[0].pressed && events[1].pressed);
    assert(!key(QK_KB_6, false));
    now = 1499; housekeeping_task_user(); assert(count == 2);
    now = 1500; housekeeping_task_user(); assert(count == 4);
    assert(!events[2].pressed && events[2].key == KC_LGUI);
    assert(!events[3].pressed && events[3].key == KC_SPACE);
    now = 2000; housekeeping_task_user(); assert(count == 4);

    count = 0; now = 3000; key(QK_KB_6, true); key(QK_KB_6, false);
    now = 3400; key(QK_KB_6, true); key(QK_KB_6, false);
    assert(count == 2); // Repeated presses extend the timer without duplicate downs.
    now = 3899; housekeeping_task_user(); assert(count == 2);
    now = 3900; housekeeping_task_user(); assert(count == 4);

    count = 0; now = UINT32_MAX - 100; key(QK_KB_6, true);
    now += 499; housekeeping_task_user(); assert(count == 2);
    ++now; housekeeping_task_user(); assert(count == 4);
    key(QK_KB_6, false); assert(count == 4);
    puts("PASS: all 11 Custom keys, press/release sequences, Siri timing/retrigger/wraparound, passthrough");
}
