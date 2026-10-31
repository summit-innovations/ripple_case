#pragma once

#include <driver/i2s_std.h>

#define RT_BUTTON_PIN 34
#define T_BUTTON_PIN 35
#define PRD_BUTTON_PIN 39
#define DEV_BUTTON_PIN 36
#define RT_LED_PIN 14
#define T_LED_PIN 12
#define PRD_LED_PIN 25
#define DEV_LED_PIN 32
#define WAIT_LED_PIN 26
#define I2S_WS ((gpio_num_t) 27)
#define I2S_SCK ((gpio_num_t) 33)
#define I2S_SD ((gpio_num_t) 13)
#define I2S_PORT I2S_NUM_0

i2s_chan_handle_t rx_handle;

void config_i2s() {
  Serial.println("Configuring mic pins");
  i2s_chan_config_t chan_cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_PORT, I2S_ROLE_MASTER);
  ESP_ERROR_CHECK(i2s_new_channel(&chan_cfg, NULL, &rx_handle));
  i2s_std_config_t std_cfg = {
    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(16000),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT, I2S_SLOT_MODE_MONO),
    .gpio_cfg = {
      .mclk = I2S_GPIO_UNUSED,
      .bclk = I2S_SCK,
      .ws = I2S_WS,
      .dout = I2S_GPIO_UNUSED,
      .din = I2S_SD
    },
  };
  std_cfg.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT;
  ESP_ERROR_CHECK(i2s_channel_init_std_mode(rx_handle, &std_cfg));
  ESP_ERROR_CHECK(i2s_channel_enable(rx_handle));
  Serial.println("Mic pins configured correctly!!");
}

void config_fsm() {
  pinMode(RT_BUTTON_PIN, INPUT);
  pinMode(T_BUTTON_PIN, INPUT);
  pinMode(PRD_BUTTON_PIN, INPUT);
  pinMode(DEV_BUTTON_PIN, INPUT);
  pinMode(RT_LED_PIN, OUTPUT);
  pinMode(T_LED_PIN, OUTPUT);
  pinMode(WAIT_LED_PIN, OUTPUT);
  pinMode(PRD_LED_PIN, OUTPUT);
  pinMode(DEV_LED_PIN, OUTPUT);
  Serial.println("GPIO pin configuration successful");
}

void pin_config() {
  config_fsm();
  config_i2s();
}

