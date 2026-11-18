#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "driver/gpio.h"
#include "driver/i2c_master.h"
#include "esp_log.h"
#include "esp_chip_info.h"
#include "esp_flash.h"
#include "esp_heap_caps.h"
#include "esp_idf_version.h"
#include "led.h"
#include "hw_pins.h"

static const char *TAG = "main";

void configure(void) {
    ESP_LOGI(TAG, 
        "LED pin config result: %s", 
        esp_err_to_name(led_init_pin(HW_BATT_LED, GPIO_MODE_OUTPUT, GPIO_PULLUP_ENABLE, GPIO_PULLDOWN_DISABLE, GPIO_INTR_DISABLE)));
}

void print_config(void)
{
    // esp_chip_info_t chip;
    // esp_chip_info(&chip);
    // uint32_t flash_size = 0;
    // esp_flash_get_size(NULL, &flash_size);

    // ESP_LOGI(TAG, "ESP-IDF %s, %d cores", esp_get_idf_version(), chip.cores);
    // ESP_LOGI(TAG, "Flash: %lu MB", (unsigned long)(flash_size / (1024 * 1024)));
    // ESP_LOGI(TAG, "PSRAM: %u KB", (unsigned)(heap_caps_get_total_size(MALLOC_CAP_SPIRAM) / 1024));
    // ESP_LOGI(TAG, "Free internal RAM: %u KB", (unsigned)(heap_caps_get_free_size(MALLOC_CAP_INTERNAL) / 1024));
    // ESP_LOGI(TAG, "FreeRTOS tick: %d Hz", configTICK_RATE_HZ);
}

int app_main(void) {
    static uint32_t led_level = false;
    configure();
    while(1) {
        led_set_level(HW_BATT_LED, led_level);
        led_level = !led_level;
        vTaskDelay(1000);
    }
    return 0;
}