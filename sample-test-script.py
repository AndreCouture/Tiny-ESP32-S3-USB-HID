import asyncio
from bleak import BleakClient, BleakScanner
import sys
import termios
import tty

# UUIDs for the BLE service and characteristic
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"


async def scan_and_connect():
    """
    Scan for the ESP32 device and connect to it.
    Returns the BLE client instance if successful.
    """
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    esp32_device = None

    # Find the ESP32 device
    for device in devices:
        print(f"Found device: {device.name} - {device.address}")
        if device.name == "ESP32-S3 Keyboard":  # Match your ESP32 device name
            esp32_device = device
            break

    if not esp32_device:
        print("ESP32 device not found. Ensure it is powered on and advertising.")
        return None

    print(f"Connecting to {esp32_device.name} ({esp32_device.address})...")
    client = BleakClient(esp32_device.address)
    await client.connect()

    if client.is_connected:
        print(f"Connected to {esp32_device.name}")
        return client
    else:
        print("Failed to connect.")
        return None


def get_character():
    """
    Read a single character from standard input without requiring ENTER.
    """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


async def live_typing(client):
    """
    Send characters in real-time as they're typed.
    """
    print("Start typing. Press CTRL+C to exit.")
    try:
        while True:
            char = get_character()

            # Handle special keys
            if char == "\x03":  # CTRL+C
                print("\nExiting live typing mode.")
                break
            elif char == "\b" or char == "\x7f":  # Backspace
                char = "\b"  # Send backspace
            elif char == "\r":  # Enter/Return
                char = "\n"  # Send newline

            # Send the character to the ESP32
            print(f"Sending: {repr(char)}")
            await client.write_gatt_char(CHARACTERISTIC_UUID, char.encode())
    except Exception as e:
        print(f"Error during live typing: {e}")


async def main():
    """
    Main function to scan for the ESP32 device and enter live typing mode.
    """
    client = await scan_and_connect()
    if client:
        try:
            await live_typing(client)
        finally:
            await client.disconnect()
            print("Disconnected from ESP32.")


if __name__ == "__main__":
    asyncio.run(main())
