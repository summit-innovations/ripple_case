#include "driver/gpio.h"

// Define pins for UART connection with nRF5340
#define HW_NRF_UART_PORT     1
#define HW_NRF_UART_TX       1    // D0
#define HW_NRF_UART_RX       2    // D1
#define HW_NRF_UART_BAUD     115200

// Define pins for UART connection with Teensy 4.1
#define HW_TEENSY_UART_PORT  2
#define HW_TEENSY_UART_TX    7    // D8
#define HW_TEENSY_UART_RX    8    // D9
#define HW_TEENSY_UART_BAUD  115200

// Define pins for battery
#define HW_BATT_I2C_PORT     0
#define HW_BATT_I2C_SDA      5    // D4
#define HW_BATT_I2C_SCL      6    // D5
#define HW_BATT_I2C_HZ       100000 // Standard speed, 100kHz

// Define pins for LED
#define HW_BATT_LED          (gpio_num_t) 4    // D3
#define HW_BATT_ALRT         9    // D10, active-low, open-drain