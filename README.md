# **Tiny ESP32-S3 USB HID**

Tiny ESP32-S3 USB HID is a project that transforms an ESP32-S3-based microcontroller into a versatile USB HID (Human Interface Device). It allows sending keystrokes from Bluetooth (BLE) to a connected USB host, effectively acting as a BLE-to-USB keyboard bridge.

This project is ideal for applications requiring a programmable USB keyboard controlled via BLE, such as automation, accessibility tools, or custom input devices.

---

## **Features**
- Emulates a USB keyboard using the ESP32-S3's native USB functionality.
- Receives text input over BLE and sends it to a USB host as keystrokes.
- Real-time BLE interaction with support for special keys (e.g., backspace, return).
- LED feedback for device status:
  - **Red**: Device initializing.
  - **Green**: USB HID ready.
  - **Blue**: BLE connected.
  - **Yellow (blinking)**: BLE data being received.

---

## **Hardware Requirements**

### **Parts List**
1. **Waveshare ESP32-S3 Zero** (or any ESP32-S3 development board with native USB support)
   - [Waveshare ESP32-S3 Zero](https://www.waveshare.com/esp32-s3-zero.htm)
2. **WS2812 RGB LED** (integrated on Waveshare ESP32-S3 Zero)
   - Used for visual feedback.
3. **USB-C Data Cable**
   - Ensure it supports data transfer, not just charging.
4. **A Computer or Host Device**
   - For receiving USB keyboard input.

---

## **Software Requirements**

### **Arduino IDE**
1. Install the [Arduino IDE](https://www.arduino.cc/en/software) (version 1.8 or 2.x).
2. Add the ESP32 board support:
   - Go to **File > Preferences**.
   - Add the following URL to **Additional Board Manager URLs**:
     ```
     https://dl.espressif.com/dl/package_esp32_index.json
     ```
   - Go to **Tools > Board > Boards Manager**, search for `esp32`, and install the latest version.

### **Python Environment**
1. Install Python 3.8+ from [python.org](https://www.python.org/).
2. Install the required Python packages:
   ```bash
   pip install bleak
