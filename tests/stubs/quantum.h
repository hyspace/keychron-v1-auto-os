#pragma once
#include <stdbool.h>
#include <stdint.h>
#include "../../qmk_firmware/quantum/keycodes.h"
typedef struct { struct { bool pressed; } event; } keyrecord_t;
void register_code(uint8_t code);
void unregister_code(uint8_t code);
uint32_t timer_elapsed32(uint32_t start);
extern uint32_t default_layer_state;
void default_layer_set(uint32_t value);
uint8_t get_highest_layer(uint32_t value);
uint32_t timer_read32(void);
bool dip_switch_update_user(uint8_t index, bool active);
