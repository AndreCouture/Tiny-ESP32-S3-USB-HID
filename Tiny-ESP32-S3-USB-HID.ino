#ifndef ARDUINO_USB_MODE
#error This ESP32 SoC has no Native USB interface
#elif ARDUINO_USB_MODE == 1
#warning This sketch should be used when USB is in OTG mode
void setup() {}
void loop() {}
#else

#include "USB.h"
#include "USBHIDKeyboard.h"
#include <BLEDevice.h>
#include <BLEServer.h>
#include <BLEUtils.h>
#include <BLE2902.h>
#include <Adafruit_NeoPixel.h>

// USB Keyboard
USBHIDKeyboard Keyboard;

// LED Configuration
#define LED_PIN 21               // GPIO connected to WS2812 LED
#define NUM_PIXELS 1             // Number of WS2812 LEDs
Adafruit_NeoPixel pixels(NUM_PIXELS, LED_PIN, NEO_GRB + NEO_KHZ800);

// BLE Configuration
#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
BLECharacteristic *bleCharacteristic;
bool deviceConnected = false;
String bleReceivedText = "";

// LED State Variables
bool usbReady = false;          // Tracks if USB HID is recognized
bool blinkState = false;        // State for blinking
unsigned long previousMillis = 0;
const long blinkInterval = 500; // Blinking interval

// BLE Callbacks
class MyServerCallbacks : public BLEServerCallbacks {
  void onConnect(BLEServer *pServer) {
    deviceConnected = true;
    Serial.println("Debug: BLE device connected.");

    // Set LED to solid blue
    pixels.clear();
    pixels.setPixelColor(0, pixels.Color(0, 0, 255)); // Solid blue
    pixels.show();
  }

  void onDisconnect(BLEServer *pServer) {
    deviceConnected = false;
    Serial.println("Debug: BLE device disconnected.");
    BLEDevice::startAdvertising();

    // Set LED back to green if USB is ready
    if (usbReady) {
      pixels.clear();
      pixels.setPixelColor(0, pixels.Color(255, 0, 0)); // Solid green
      pixels.show();
    }
  }
};

class MyCallbacks : public BLECharacteristicCallbacks {
  void onWrite(BLECharacteristic *pCharacteristic) {
    String receivedData = pCharacteristic->getValue().c_str();
    Serial.print("Debug: Received via BLE: ");
    Serial.println(receivedData);

    bleReceivedText = receivedData; // Store the received text

    // Blink LED while receiving data
    pixels.clear();
    pixels.setPixelColor(0, pixels.Color(255, 255, 0)); // Yellow (indicates data received)
    pixels.show();
    delay(100);
    if (deviceConnected) {
      pixels.clear();
      pixels.setPixelColor(0, pixels.Color(0, 0, 255)); // Back to solid blue
      pixels.show();
    }
  }
};

void setup() {
  Serial.begin(115200);
  Serial.println("Debug: Starting setup...");

  // Initialize LED
  pixels.begin();
  pixels.clear();
  pixels.setPixelColor(0, pixels.Color(0, 255, 0)); // Red on boot
  pixels.show();

  // Initialize BLE
  BLEDevice::init("ESP32-S3 Keyboard");
  BLEServer *bleServer = BLEDevice::createServer();
  bleServer->setCallbacks(new MyServerCallbacks());

  BLEService *bleService = bleServer->createService(SERVICE_UUID);
  bleCharacteristic = bleService->createCharacteristic(
    CHARACTERISTIC_UUID,
    BLECharacteristic::PROPERTY_READ | BLECharacteristic::PROPERTY_WRITE
  );
  bleCharacteristic->setCallbacks(new MyCallbacks());
  bleCharacteristic->addDescriptor(new BLE2902());
  bleService->start();

  BLEAdvertising *bleAdvertising = BLEDevice::getAdvertising();
  bleAdvertising->addServiceUUID(SERVICE_UUID);
  bleAdvertising->start();
  Serial.println("Debug: BLE advertising started.");

  // Initialize USB HID Keyboard
  Keyboard.begin();
  USB.begin();
  usbReady = true;

  // Set LED to green to indicate USB HID ready
  pixels.clear();
  pixels.setPixelColor(0, pixels.Color(255, 0, 0)); // Solid green
  pixels.show();
}

void loop() {
  // Send BLE Received Text to USB Host
  if (deviceConnected && bleReceivedText.length() > 0) {
    Serial.print("Debug: Sending to USB Keyboard: ");
    Serial.println(bleReceivedText);

    Keyboard.print(bleReceivedText); // Send text as keyboard input
    bleReceivedText = "";            // Clear the buffer
  }

  // LED Behavior if BLE is not connected
  if (!deviceConnected && usbReady) {
    unsigned long currentMillis = millis();
    if (currentMillis - previousMillis >= blinkInterval) {
      previousMillis = currentMillis;
      blinkState = !blinkState;

      // Blink green LED
      pixels.clear();
      if (blinkState) {
        pixels.setPixelColor(0, pixels.Color(255, 0, 0)); // Green
      } else {
        pixels.setPixelColor(0, pixels.Color(0, 0, 0));   // Off
      }
      pixels.show();
    }
  }
}
#endif /* ARDUINO_USB_MODE */