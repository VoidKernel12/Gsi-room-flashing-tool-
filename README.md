# Termux Fastboot Flashing & Device Utility

A production-ready, interactive CLI tool for performing Fastboot operations (partition erase & GSI system image flashing) **entirely from Termux** on a non-rooted Android device using USB OTG.

Built for users who want a clean, menu-driven experience without relying on a PC.

---

## Features

- Golden-themed interactive terminal menu
- Safe confirmation prompts before any destructive action
- Device connection detection (`fastboot devices`)
- Partition erase:
  - System
  - Userdata
  - Cache
- Flash Generic System Image (GSI) / custom system image
- Robust error handling and clear status messages
- Designed for **non-root** operation via `termux-usb` + Termux:API

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Termux** | Install from [F-Droid](https://f-droid.org/en/packages/com.termux/) (recommended) or Google Play |
| **Termux:API** app | Must be installed from the same source as Termux |
| **USB OTG support** | Your host phone must support USB OTG / USB Host mode |
| **OTG cable / adapter** | USB-C to USB-A or USB-C to USB-C (depending on devices) |
| **Target device** | Must be unlockable / able to enter fastboot mode |
| **System image** | A valid `.img` (or raw) GSI / system image file |

> **Important:** This tool does **not** unlock bootloaders. You must already have an unlocked bootloader on the target device.

---

## Installation

1. Clone or download this repository into Termux:

   ```bash
   pkg install git -y
   ```
   ```bash
   git clone https://github.com/VoidKernel12/Gsi-room-flashing-tool-.git
   ```
   ```
   cd Gsi-room-flashing-tool-
   ```

2. Run the installer:

   ```bash
   bash install.sh
   ```

   The script will:
   - Update package lists
   - Install `python`, `android-tools`, and `termux-api`
   - Set executable permissions on the scripts

3. Install the **Termux:API** Android application if you haven’t already.

---

## USB Permission Setup (Non-Root)

Because Termux runs as a normal app, you must explicitly grant USB access:


# List connected USB devices
```bash
termux-usb -l
```
# Request permission for a specific device (replace with actual path)
```bash
termux-usb -r /dev/bus/usb/00X/00Y
```

After granting permission, the device should appear when you run `fastboot devices` from within the tool.

---

## Usage

```bash
python main.py
```

You will see a golden-themed menu:

```
1. Erase System Partition
2. Erase Userdata Partition
3. Erase Cache Partition
4. Flash GSI System Image
5. Exit
```

### Typical Workflow (GSI Flash)

1. Boot the target device into **fastboot / bootloader** mode.
2. Connect it to your Termux host via OTG.
3. Grant USB permission with `termux-usb`.
4. Launch `python main.py`.
5. (Optional) Erase system / userdata / cache as needed.
6. Select option **4**, provide the full path to your system image (e.g. `/sdcard/Download/system.img`), and confirm.
7. After a successful flash, reboot the device (`fastboot reboot` or use the device’s key combination).

---

## Project Structure

```
termux-fastboot-tool/
├── main.py          # Interactive CLI application
├── install.sh       # One-shot setup script for Termux
├── README.md        # This file
└── DISCLAIMER.md    # Legal & safety warning (read it!)
```

---

## Safety Notes

- Always double-check the image path before flashing.
- Erasing `userdata` will wipe all user data.
- Flashing an incompatible GSI can soft-brick or hard-brick the device.
- Keep a known-good stock firmware and a recovery method ready.
- This tool is provided **as-is**. You assume all risk.

See [DISCLAIMER.md](DISCLAIMER.md) for the full legal and technical warning.

---

## Troubleshooting

| Problem | Possible Solution |
|---------|-------------------|
| `fastboot: command not found` | Re-run `bash install.sh` |
| No devices listed | Check OTG connection, grant `termux-usb` permission, ensure device is in fastboot mode |
| Permission denied on USB | Run `termux-usb -r <device>` again |
| Flash fails with “partition not found” | Some devices use `system_a` / `system_b` (A/B). This tool targets the classic `system` partition. |
| Image too large / sparse issues | Convert the image with `simg2img` if needed, or use a properly prepared GSI |

---

## License

MIT License — feel free to use, modify, and distribute.

---

## Contributing

Pull requests and issue reports are welcome. Please keep the golden theme and safety confirmations intact.
