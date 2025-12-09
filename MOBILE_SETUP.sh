#!/bin/bash

# IQOO Z6 Pro Mobile App Viewing Setup
# This script will help you access the mobile app from your IQOO Z6 Pro

echo "========================================="
echo "Mobile App - IQOO Z6 Pro Setup Guide"
echo "========================================="
echo ""

# Get the local IP address
echo "Step 1: Finding your computer's IP address..."

# Windows PowerShell command to get local IP
IP_ADDR=$(ipconfig | grep -oP '(?<=IPv4 Address.*:\s)\d+(\.\d+){3}' | head -1)

if [ -z "$IP_ADDR" ]; then
    echo "❌ Could not automatically detect IP address."
    echo "Please run this command in PowerShell:"
    echo "  ipconfig"
    echo "Look for 'IPv4 Address' under your network adapter"
    echo ""
    echo "Then manually use: http://<YOUR_IP>:5173"
    exit 1
fi

echo "✓ Found IP address: $IP_ADDR"
echo ""

# Check if app is already running
echo "Step 2: Checking if mobile app is running..."
if ! curl -s http://localhost:5173 > /dev/null; then
    echo "⚠ Mobile app is not running on localhost:5173"
    echo ""
    echo "To start the mobile app, run:"
    echo "  cd apps/mobile"
    echo "  npm run dev"
    echo ""
    exit 1
fi

echo "✓ Mobile app is running"
echo ""

echo "========================================="
echo "DEVICE CONNECTION INSTRUCTIONS"
echo "========================================="
echo ""
echo "📱 On your IQOO Z6 Pro:"
echo ""
echo "1. Make sure your phone is connected to the same WiFi as your PC"
echo ""
echo "2. Open a web browser (Chrome, Firefox, Safari, etc.)"
echo ""
echo "3. Type this URL in the address bar:"
echo "   http://$IP_ADDR:5173"
echo ""
echo "4. Press Enter and the app should load!"
echo ""

echo "========================================="
echo "TROUBLESHOOTING"
echo "========================================="
echo ""
echo "❓ App not loading?"
echo ""
echo "  • Check WiFi: Both devices must be on the same network"
echo ""
echo "  • Check firewall: Windows may block port 5173"
echo "    - Open Windows Defender Firewall"
echo "    - Allow Node.js through the firewall"
echo ""
echo "  • Check IP address: Run 'ipconfig' to verify"
echo ""
echo "  • Restart dev server:"
echo "    - Stop (Ctrl+C) and restart 'npm run dev'"
echo ""

echo "========================================="
echo "HOT RELOAD (Auto-refresh on code changes)"
echo "========================================="
echo ""
echo "Any changes you make to the code in apps/mobile/src/"
echo "will automatically refresh in your browser!"
echo ""

echo "========================================="
