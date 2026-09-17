#!/data/data/com.termux/files/usr/bin/bash
#
# install.sh — Setup script for Termux Fastboot Utility
# =====================================================
# Run this script inside Termux to install all required packages
# and set executable permissions.
#
# Usage:
#   bash install.sh
#

set -euo pipefail

# Colors for output
GOLD="\033[38;5;220m"
GREEN="\033[92m"
RED="\033[91m"
YELLOW="\033[93m"
CYAN="\033[96m"
RESET="\033[0m"
BOLD="\033[1m"

echo -e "${GOLD}${BOLD}"
echo "╔══════════════════════════════════════════════════════╗"
echo "║     Termux Fastboot Utility — Installer              ║"
echo "╚══════════════════════════════════════════════════════╝"
echo -e "${RESET}"

# ─────────────────────────────────────────────────────────────
# 1. Update package lists
# ─────────────────────────────────────────────────────────────
echo -e "${CYAN}[*] Updating Termux package lists...${RESET}"
pkg update -y

# ─────────────────────────────────────────────────────────────
# 2. Install required packages
# ─────────────────────────────────────────────────────────────
echo -e "${CYAN}[*] Installing dependencies...${RESET}"
echo -e "    • python"
echo -e "    • android-tools (provides fastboot & adb)"
echo -e "    • termux-api"
echo ""

pkg install -y python android-tools termux-api

# ─────────────────────────────────────────────────────────────
# 3. Verify installations
# ─────────────────────────────────────────────────────────────
echo -e "${CYAN}[*] Verifying installations...${RESET}"

MISSING=0

if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[!] python3 not found after installation.${RESET}"
    MISSING=1
else
    echo -e "${GREEN}[+] python3  → $(command -v python3)${RESET}"
fi

if ! command -v fastboot &>/dev/null; then
    echo -e "${RED}[!] fastboot not found after installation.${RESET}"
    MISSING=1
else
    echo -e "${GREEN}[+] fastboot → $(command -v fastboot)${RESET}"
fi

if ! command -v termux-usb &>/dev/null; then
    echo -e "${YELLOW}[!] termux-usb not found (part of termux-api).${RESET}"
    echo -e "${YELLOW}    Make sure the Termux:API Android app is installed from F-Droid/Play Store.${RESET}"
else
    echo -e "${GREEN}[+] termux-usb → $(command -v termux-usb)${RESET}"
fi

if [ "$MISSING" -eq 1 ]; then
    echo -e "${RED}[!] Some packages failed to install. Please check your network and try again.${RESET}"
    exit 1
fi

# ─────────────────────────────────────────────────────────────
# 4. Set executable permissions
# ─────────────────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${CYAN}[*] Setting executable permissions...${RESET}"

chmod +x "${SCRIPT_DIR}/main.py"
chmod +x "${SCRIPT_DIR}/install.sh"

echo -e "${GREEN}[+] Permissions set.${RESET}"

# ─────────────────────────────────────────────────────────────
# 5. Final instructions
# ─────────────────────────────────────────────────────────────
echo ""
echo -e "${GOLD}${BOLD}Installation complete!${RESET}"
echo ""
echo -e "${YELLOW}IMPORTANT next steps:${RESET}"
echo -e "  1. Install the ${BOLD}Termux:API${RESET} Android app (F-Droid recommended)."
echo -e "  2. Connect your device via USB OTG / USB-C cable."
echo -e "  3. Put the target device into ${BOLD}fastboot / bootloader${RESET} mode."
echo -e "  4. Grant USB permission:"
echo -e "       ${CYAN}termux-usb -l${RESET}          # list devices"
echo -e "       ${CYAN}termux-usb -r <path>${RESET}  # request access"
echo -e "  5. Run the tool:"
echo -e "       ${CYAN}python main.py${RESET}"
echo ""
echo -e "${GOLD}Read DISCLAIMER.md before performing any erase or flash operations.${RESET}"
echo ""
