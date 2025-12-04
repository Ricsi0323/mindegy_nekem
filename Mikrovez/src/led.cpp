#include <Arduino.h>
#include <FastLED.h>

// FastLED beállítások
#define LED_PIN     7
#define LED_COUNT   8
#define CHIPSET     WS2812B
#define COLOR_ORDER GRB
#define BRIGHTNESS  70

CRGB leds[LED_COUNT];

// Függvények előre deklarálva
void colorWipe(const CRGB &color, int wait);
void rainbowCycle(int wait);

void setup() {
  FastLED.addLeds<CHIPSET, LED_PIN, COLOR_ORDER>(leds, LED_COUNT);
  FastLED.setBrightness(BRIGHTNESS);
  FastLED.clear(true);
}

void loop() {
  // Egyszerű tesztek: piros, zöld, kék, majd szivárvány
  //colorWipe(CRGB::Red, 100);
  //colorWipe(CRGB::Green, 100);
  //colorWipe(CRGB::Blue, 100);
  rainbowCycle(10);
}

// --- Függvények implementációja ---
void colorWipe(const CRGB &color, int wait) {
  for (uint16_t i = 0; i < LED_COUNT; i++) {
    leds[i] = color;
    FastLED.show();
    delay(wait);
  }
}

void rainbowCycle(int wait) {
  for (uint16_t j = 0; j < 256 * 5; j++) { // 5 kör
    for (uint16_t i = 0; i < LED_COUNT; i++) {
      uint8_t hue = ((i * 256 / LED_COUNT) + j) & 0xFF;
      leds[i] = CHSV(hue, 255, BRIGHTNESS);
    }
    FastLED.show();
    delay(wait);
  }
}