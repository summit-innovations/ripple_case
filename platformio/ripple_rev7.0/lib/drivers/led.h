#include <stdint.h>
#include "driver/gpio.h"

// Initialize the GPIO pin (mode, pullup/pulldown enable, and the interrupt type - if associated with an interrupt)
esp_err_t led_init_pin(uint64_t pin_number, gpio_mode_t mode, gpio_pullup_t pull_up_en, gpio_pulldown_t pull_down_en, gpio_int_type_t intr_type);

// Write to LED (turning on or off)
esp_err_t led_set_level(gpio_num_t gpio_num, uint32_t level);

// Read from pin
uint32_t led_get_level(gpio_num_t gpio_num);