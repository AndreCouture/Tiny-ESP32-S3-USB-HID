import asyncio
from bleak import BleakClient, BleakScanner
import tkinter as tk
from tkinter import messagebox, filedialog

# UUIDs for the BLE service and characteristic
SERVICE_UUID = "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
CHARACTERISTIC_UUID = "beb5483e-36e1-4688-b7f5-ea07361b26a8"


class BLEApp:
    def __init__(self, root):
        self.root = root
        self.client = None
        self.live_input_enabled = False
        self.loop = asyncio.new_event_loop()  # Create a new asyncio event loop
        asyncio.set_event_loop(self.loop)    # Set the loop for asyncio tasks
        self.create_ui()
        self.run_asyncio_loop()

    def create_ui(self):
        self.root.title("ESP32 BLE Keyboard")
        self.root.geometry("400x400")

        self.status_label = tk.Label(self.root, text="Status: Not Connected", fg="red")
        self.status_label.pack(pady=10)

        self.connect_button = tk.Button(self.root, text="Connect to ESP32", command=self.connect_to_device)
        self.connect_button.pack(pady=5)

        self.text_input = tk.Entry(self.root, state="disabled", width=50)
        self.text_input.pack(pady=10)

        self.send_button = tk.Button(self.root, text="Send Text", state="disabled", command=self.send_text)
        self.send_button.pack(pady=5)

        self.live_input_button = tk.Button(
            self.root, text="Enable Live Input", state="disabled", command=self.toggle_live_input
        )
        self.live_input_button.pack(pady=5)

        self.file_button = tk.Button(self.root, text="Send File", state="disabled", command=self.send_file)
        self.file_button.pack(pady=5)

        self.text_input.bind("<Key>", self.send_character)

    def run_asyncio_loop(self):
        """
        Run the asyncio event loop periodically using tkinter's after method.
        """
        self.loop.call_soon(self.loop.stop)  # Stop the loop if it's already running
        self.loop.run_forever()
        self.root.after(100, self.run_asyncio_loop)  # Run again after 100ms

    async def scan_and_connect(self):
        """
        Scan for the ESP32 device and connect to it.
        """
        self.status_label.config(text="Scanning for BLE devices...", fg="blue")
        devices = await BleakScanner.discover()
        esp32_device = next((d for d in devices if d.name in {"ESP32-S3 Keyboard", "ESP32"}), None)

        if not esp32_device:
            self.status_label.config(text="ESP32 device not found!", fg="red")
            return None

        self.status_label.config(text=f"Connecting to {esp32_device.name}...", fg="blue")
        self.client = BleakClient(esp32_device.address)

        try:
            await self.client.connect()
            if self.client.is_connected:
                self.status_label.config(text=f"Connected to {esp32_device.name}", fg="green")
                self.text_input.config(state="normal")
                self.send_button.config(state="normal")
                self.live_input_button.config(state="normal")
                self.file_button.config(state="normal")
                return self.client
        except Exception as e:
            self.status_label.config(text=f"Failed to connect: {e}", fg="red")
            return None

    def connect_to_device(self):
        """
        Start scanning and connect asynchronously.
        """
        self.loop.create_task(self.scan_and_connect())

    async def write_character(self, char):
        """
        Write a character to the BLE device.
        """
        if self.client and self.client.is_connected:
            try:
                await self.client.write_gatt_char(CHARACTERISTIC_UUID, char.encode())
            except Exception as e:
                self.status_label.config(text=f"Error sending data: {e}", fg="red")

    def send_character(self, event):
        """
        Handle keyboard input and send it to the BLE device in live mode.
        """
        if self.live_input_enabled:
            char = event.char
            if char == "":
                # Handle special keys
                if event.keysym == "BackSpace":
                    char = "\b"  # Backspace
                elif event.keysym == "Return":
                    char = "\n"  # Newline
                else:
                    print(f"Unhandled special key: {event.keysym}")
                    return

            if char:
                print(f"Sending: {repr(char)}")
                self.loop.create_task(self.write_character(char))

    def toggle_live_input(self):
        """
        Enable or disable live input mode.
        """
        self.live_input_enabled = not self.live_input_enabled
        state = "enabled" if self.live_input_enabled else "disabled"
        self.live_input_button.config(text=f"Disable Live Input" if self.live_input_enabled else "Enable Live Input")
        self.status_label.config(text=f"Live input {state}.", fg="blue")

    def send_text(self):
        """
        Send the content of the text input box to the BLE device.
        """
        text = self.text_input.get()
        if text:
            for char in text:
                self.loop.create_task(self.write_character(char))

    def send_file(self):
        """
        Open a file dialog and send the content of the selected text file to the BLE device.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    content = file.read()
                    for char in content:
                        self.loop.create_task(self.write_character(char))
                self.status_label.config(text="File sent successfully.", fg="green")
            except Exception as e:
                self.status_label.config(text=f"Error sending file: {e}", fg="red")


# Run the app
if __name__ == "__main__":
    root = tk.Tk()
    app = BLEApp(root)
    root.mainloop()
