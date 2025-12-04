#include <Arduino.h>

// 5x3 button matrix scan for Arduino Nano
// Columns: D2, D3, D4, D5, D6
// Rows:    D9, D10, D11
// Uses INPUT_PULLUP on rows and drives columns LOW one-by-one.

const byte ROWS = 5;
const byte COLS = 3;

const byte rowPins[ROWS] = {2, 3, 4, 5, 6};
const byte colPins[COLS] = {9, 10, 11};

bool matrixState[COLS][ROWS];       // current stable state: true = pressed 
bool matrixPrev[COLS][ROWS];        // previous stable state

const unsigned long DEBOUNCE_MS = 20; // debounce time

// karaktertérkép: keymap[col][row] — A..O
char keymap[COLS][ROWS] = {
  {'A','B','C','D','E'},   // col 0
  {'F','G','H','I','J'},   // col 1
  {'K','L','M','S','O'}    // col 2
};

char lastChar = 0; // utoljára lenyomott karakter

void setup() {
  Serial.begin(115200);
  // init columns as INPUT (high-Z) — ne tartsuk őket állandóan driven
  for (byte c = 0; c < COLS; c++) {
    pinMode(colPins[c], INPUT); // float (high-Z)
  }
  // init rows as inputs with pull-up
  for (byte r = 0; r < ROWS; r++) {
    pinMode(rowPins[r], INPUT_PULLUP);
  }

  // clear states
  for (byte c = 0; c < COLS; c++)
    for (byte r = 0; r < ROWS; r++)
      matrixState[c][r] = matrixPrev[c][r] = false;

  Serial.println("5x3 matrix scanner ready (cols high-Z).");
}

void loop() {
  // scan each column
  for (byte c = 0; c < COLS; c++) {
    // make all columns high-Z first
    for (byte j = 0; j < COLS; j++) {
      pinMode(colPins[j], INPUT);
    }

    // activate this column by driving it LOW
    pinMode(colPins[c], OUTPUT);
    digitalWrite(colPins[c], LOW);
    delayMicroseconds(5); // small settle time

    // read all rows for this column
    for (byte r = 0; r < ROWS; r++) {
      bool pressed = (digitalRead(rowPins[r]) == LOW); // active low

      // simple debounce (blocking but short)
      if (pressed) {
        unsigned long t0 = millis();
        while (millis() - t0 < DEBOUNCE_MS) {
          if (digitalRead(rowPins[r]) == HIGH) { pressed = false; break; }
        }
      } else {
        unsigned long t0 = millis();
        while (millis() - t0 < 5) {
          if (digitalRead(rowPins[r]) == LOW) { pressed = true; break; }
        }
      }

      matrixState[c][r] = pressed;

      if (matrixState[c][r] != matrixPrev[c][r]) {
        matrixPrev[c][r] = matrixState[c][r];
        if (matrixState[c][r]) {
          // csak a karaktert tároljuk és kiírjuk (pl. "A")
          lastChar = keymap[c][r];
          Serial.println(lastChar);
        }
      }
    }

    // deactivate column -> set to high-Z
    pinMode(colPins[c], INPUT);
  }

  // optional: small pause to limit CPU usage
  delay(5);
}





