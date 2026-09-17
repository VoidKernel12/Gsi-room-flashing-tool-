#!/usr/bin/env python3
"""
Termux Fastboot Flashing & Device Utility
=========================================
A CLI tool for non-root Fastboot operations via Termux + termux-usb / termux-api.
Designed for safe GSI flashing and partition management on Android devices.

Author: Community Project
License: MIT
"""

import os
import sys
import subprocess
import time
from typing import Optional, List

# ─────────────────────────────────────────────────────────────
# ANSI Color Codes (Golden / Amber Theme)
# ─────────────────────────────────────────────────────────────
class Colors:
    GOLD        = "\033[38;5;220m"   # Bright gold
    GOLD_DIM    = "\033[38;5;178m"   # Dimmer gold
    AMBER       = "\033[38;5;214m"   # Amber
    YELLOW      = "\033[93m"
    WHITE       = "\033[97m"
    GRAY        = "\033[90m"
    RED         = "\033[91m"
    GREEN       = "\033[92m"
    CYAN        = "\033[96m"
    BOLD        = "\033[1m"
    RESET       = "\033[0m"
    CLEAR       = "\033[2J\033[H"    # Clear screen + home


# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────
def clear_screen() -> None:
    """Clear the terminal screen."""
    print(Colors.CLEAR, end="")


def print_banner() -> None:
    """Print the golden-themed application banner."""
    banner = f"""
{Colors.GOLD}{Colors.BOLD}
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║     ████████╗███████╗██████╗ ███╗   ███╗██╗   ██╗██╗  ██╗║
    ║     ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║   ██║╚██╗██╔╝║
    ║        ██║   █████╗  ██████╔╝██╔████╔██║██║   ██║ ╚███╔╝ ║
    ║        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║   ██║ ██╔██╗ ║
    ║        ██║   ███████╗██║  ██║██║ ╚═╝ ██║╚██████╔╝██╔╝ ██╗║
    ║        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═╝║
    ║                                                          ║
    ║          Fastboot Flashing & Device Utility              ║
    ║               Termux • Non-Root • OTG                    ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
{Colors.RESET}
{Colors.GOLD_DIM}  ────────────────────────────────────────────────────────────{Colors.RESET}
{Colors.AMBER}  Warning: Partition erase & flashing can brick your device.{Colors.RESET}
{Colors.GOLD_DIM}  ────────────────────────────────────────────────────────────{Colors.RESET}
"""
    print(banner)


def print_menu() -> None:
    """Display the main interactive menu."""
    menu = f"""
{Colors.GOLD}{Colors.BOLD}  MAIN MENU{Colors.RESET}
{Colors.GOLD_DIM}  ─────────{Colors.RESET}

  {Colors.GOLD}1.{Colors.RESET}  Erase System Partition      {Colors.GRAY}(fastboot erase system){Colors.RESET}
  {Colors.GOLD}2.{Colors.RESET}  Erase Userdata Partition    {Colors.GRAY}(fastboot erase userdata){Colors.RESET}
  {Colors.GOLD}3.{Colors.RESET}  Erase Cache Partition       {Colors.GRAY}(fastboot erase cache){Colors.RESET}
  {Colors.GOLD}4.{Colors.RESET}  Flash GSI System Image      {Colors.GRAY}(fastboot flash system <path>){Colors.RESET}
  {Colors.GOLD}5.{Colors.RESET}  Exit

{Colors.GOLD_DIM}  ────────────────────────────────────────────────────────────{Colors.RESET}
"""
    print(menu)


def run_command(cmd: List[str], timeout: int = 120) -> subprocess.CompletedProcess:
    """
    Execute a shell command and return the CompletedProcess object.
    Captures both stdout and stderr.
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        return result
    except subprocess.TimeoutExpired:
        print(f"\n{Colors.RED}[ERROR] Command timed out after {timeout}s.{Colors.RESET}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"\n{Colors.RED}[ERROR] Command not found: {cmd[0]}{Colors.RESET}")
        print(f"{Colors.YELLOW}Make sure android-tools is installed (run install.sh).{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] Unexpected error: {e}{Colors.RESET}")
        sys.exit(1)


def check_fastboot_available() -> bool:
    """Verify that the 'fastboot' binary is present in PATH."""
    result = run_command(["which", "fastboot"])
    return result.returncode == 0 and result.stdout.strip() != ""


def get_connected_devices() -> List[str]:
    """
    Run 'fastboot devices' and return a list of connected device serials.
    Returns empty list if no devices are found.
    """
    result = run_command(["fastboot", "devices"])
    if result.returncode != 0:
        return []

    devices = []
    for line in result.stdout.strip().splitlines():
        line = line.strip()
        if line and "fastboot" in line.lower():
            # Format is usually: <serial>    fastboot
            parts = line.split()
            if parts:
                devices.append(parts[0])
    return devices


def ensure_device_connected() -> bool:
    """
    Check that at least one device is connected in fastboot mode.
    Prints status messages and returns True if a device is ready.
    """
    print(f"\n{Colors.CYAN}[*] Checking for fastboot devices...{Colors.RESET}")
    devices = get_connected_devices()

    if not devices:
        print(f"{Colors.RED}[!] No devices detected in fastboot mode.{Colors.RESET}")
        print(f"{Colors.YELLOW}")
        print("  Possible causes:")
        print("  • Device is not in fastboot/bootloader mode")
        print("  • USB OTG cable / adapter not properly connected")
        print("  • termux-usb permission not granted")
        print("  • Driver / authorization issue")
        print(f"{Colors.RESET}")
        print(f"{Colors.GOLD_DIM}Tip: Put the device into fastboot mode, then run:{Colors.RESET}")
        print(f"     {Colors.WHITE}termux-usb -l{Colors.RESET}   # list USB devices")
        print(f"     {Colors.WHITE}termux-usb -r <device>{Colors.RESET}  # request permission")
        return False

    print(f"{Colors.GREEN}[+] Device(s) found:{Colors.RESET}")
    for d in devices:
        print(f"    {Colors.GOLD}→ {d}{Colors.RESET}")
    return True


def confirm_action(action_description: str) -> bool:
    """
    Ask the user for explicit confirmation before a destructive action.
    Returns True only if the user types 'yes' (case-insensitive).
    """
    print(f"\n{Colors.AMBER}{Colors.BOLD}⚠  CONFIRMATION REQUIRED{Colors.RESET}")
    print(f"{Colors.YELLOW}You are about to: {action_description}{Colors.RESET}")
    print(f"{Colors.RED}This operation is irreversible and may cause data loss or brick the device.{Colors.RESET}")
    response = input(f"\n{Colors.GOLD}Type 'yes' to proceed, anything else to cancel: {Colors.RESET}").strip().lower()
    return response == "yes"


def erase_partition(partition: str) -> None:
    """
    Erase the specified partition using fastboot.
    partition: one of 'system', 'userdata', 'cache'
    """
    if not ensure_device_connected():
        return

    if not confirm_action(f"ERASE the '{partition}' partition"):
        print(f"{Colors.GRAY}Operation cancelled by user.{Colors.RESET}")
        return

    print(f"\n{Colors.CYAN}[*] Erasing {partition} partition...{Colors.RESET}")
    result = run_command(["fastboot", "erase", partition], timeout=180)

    if result.returncode == 0:
        print(f"{Colors.GREEN}[+] Successfully erased '{partition}' partition.{Colors.RESET}")
        if result.stdout.strip():
            print(f"{Colors.GRAY}{result.stdout.strip()}{Colors.RESET}")
    else:
        print(f"{Colors.RED}[!] Failed to erase '{partition}' partition.{Colors.RESET}")
        if result.stderr.strip():
            print(f"{Colors.RED}{result.stderr.strip()}{Colors.RESET}")
        if result.stdout.strip():
            print(f"{Colors.GRAY}{result.stdout.strip()}{Colors.RESET}")


def flash_system_image() -> None:
    """
    Option 4 flow:
    1. Check if a fastboot device is connected.
    2. If connected, ask for the GSI / system image path.
    3. After a valid path is given → flash automatically (no extra confirmation).
    """
    # Step 1: Check device connection
    if not ensure_device_connected():
        return

    # Step 2: Ask for GSI file path
    print(f"\n{Colors.GOLD}Flash GSI / System Image{Colors.RESET}")
    print(f"{Colors.GOLD_DIM}────────────────────────{Colors.RESET}")
    print(f"{Colors.GRAY}Supported formats: .img, .bin (raw system image){Colors.RESET}")
    print(f"{Colors.GRAY}Example: /sdcard/Download/system.img{Colors.RESET}\n")

    image_path = input(f"{Colors.GOLD}GSI ROM-এর ফাইল পাথ দিন: {Colors.RESET}").strip()

    # Expand ~ if present
    image_path = os.path.expanduser(image_path)

    if not image_path:
        print(f"{Colors.RED}[!] কোনো পাথ দেওয়া হয়নি। বাতিল করা হলো।{Colors.RESET}")
        return

    if not os.path.isfile(image_path):
        print(f"{Colors.RED}[!] ফাইল পাওয়া যায়নি: {image_path}{Colors.RESET}")
        return

    # Show image size
    try:
        size_mb = os.path.getsize(image_path) / (1024 * 1024)
        print(f"{Colors.CYAN}[*] Image size: {size_mb:.1f} MB{Colors.RESET}")
        if size_mb < 100:
            print(f"{Colors.YELLOW}[!] Warning: Image is unusually small (<100 MB).{Colors.RESET}")
    except OSError:
        pass

    # Step 3: Automatic flash (no extra confirmation)
    print(f"\n{Colors.CYAN}[*] Flashing শুরু হচ্ছে... কয়েক মিনিট লাগতে পারে।{Colors.RESET}")
    print(f"{Colors.GRAY}ডিভাইস ডিসকানেক্ট করবেন না, Termux বন্ধ করবেন না।{Colors.RESET}\n")

    result = run_command(["fastboot", "flash", "system", image_path], timeout=600)

    if result.returncode == 0:
        print(f"{Colors.GREEN}[+] সফলভাবে system image ফ্ল্যাশ হয়েছে।{Colors.RESET}")
        if result.stdout.strip():
            print(f"{Colors.GRAY}{result.stdout.strip()}{Colors.RESET}")
        print(f"\n{Colors.GOLD}পরবর্তী ধাপ (সাধারণত):{Colors.RESET}")
        print(f"  • fastboot reboot")
        print(f"  • অথবা recovery-তে গিয়ে data wipe করুন (প্রয়োজন হলে)")
    else:
        print(f"{Colors.RED}[!] System image ফ্ল্যাশ ব্যর্থ হয়েছে।{Colors.RESET}")
        if result.stderr.strip():
            print(f"{Colors.RED}{result.stderr.strip()}{Colors.RESET}")
        if result.stdout.strip():
            print(f"{Colors.GRAY}{result.stdout.strip()}{Colors.RESET}")


def pause() -> None:
    """Wait for user to press Enter before returning to the menu."""
    input(f"\n{Colors.GOLD_DIM}Press Enter to return to the main menu...{Colors.RESET}")


# ─────────────────────────────────────────────────────────────
# Main Application Loop
# ─────────────────────────────────────────────────────────────
def main() -> None:
    """Entry point for the interactive CLI."""
    # Verify fastboot is available early
    if not check_fastboot_available():
        print(f"{Colors.RED}[ERROR] 'fastboot' binary not found in PATH.{Colors.RESET}")
        print(f"{Colors.YELLOW}Please run the install.sh script first:{Colors.RESET}")
        print(f"  {Colors.WHITE}bash install.sh{Colors.RESET}")
        sys.exit(1)

    while True:
        clear_screen()
        print_banner()
        print_menu()

        try:
            choice = input(f"{Colors.GOLD}Select an option [1-5]: {Colors.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{Colors.GRAY}Exiting...{Colors.RESET}")
            sys.exit(0)

        if choice == "1":
            erase_partition("system")
            pause()
        elif choice == "2":
            erase_partition("userdata")
            pause()
        elif choice == "3":
            erase_partition("cache")
            pause()
        elif choice == "4":
            flash_system_image()
            pause()
        elif choice == "5":
            print(f"\n{Colors.GOLD}Goodbye. Stay safe while flashing!{Colors.RESET}\n")
            sys.exit(0)
        else:
            print(f"{Colors.RED}[!] Invalid option. Please choose 1-5.{Colors.RESET}")
            time.sleep(1.2)


if __name__ == "__main__":
    main()
