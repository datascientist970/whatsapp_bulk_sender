# 📱 WhatsApp Business Suite - Enterprise Bulk Messaging Platform

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![Django](https://img.shields.io/badge/django-5.0.2-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

**Professional WhatsApp Bulk Messaging Solution with AI-Powered Content Generation**

[Features](#✨-features) • [Installation](#🚀-installation) • [Usage](#💻-usage) • [Troubleshooting](#🔧-troubleshooting) • [FAQ](#❓-faq)

</div>

---

## 🎯 What is This?

WhatsApp Business Suite is a professional web application that allows you to:
- Send bulk WhatsApp messages to multiple recipients
- Generate AI-powered marketing messages using Groq API
- Send multiple messages per recipient (1-50 times)
- Check if phone numbers have WhatsApp
- Track delivery status in real-time

**Perfect for:** Marketing campaigns, customer notifications, event reminders, business announcements

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI Message Generator** | Create professional messages with 6 different tones |
| 📨 **Bulk Sending** | Send to hundreds of numbers simultaneously |
| 🔢 **Multi-Send** | Send up to 50 messages per recipient |
| ✅ **Number Validation** | Check which numbers have WhatsApp |
| 📊 **Real-time Analytics** | Track success rates and delivery status |
| 🔐 **Secure Session** | Login once, stay connected |
| 🐛 **Debug Console** | Built-in troubleshooting tools |
| 📱 **Responsive Design** | Works on desktop, tablet, and mobile |

---

## 🚀 Installation Guide for Beginners

### Step 1: Prerequisites

Before starting, make sure you have:

1. **Python 3.9 or higher** 
   - Download from: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH" during installation

2. **Google Chrome Browser**
   - Download from: https://www.google.com/chrome/
   - Any version works

3. **Groq API Key** (Free)
   - Sign up at: https://console.groq.com
   - Go to "API Keys" → "Create API Key"
   - Copy your key (starts with `gsk_`)

### Step 2: Download the Project

**Option A: Download ZIP**
1. Click "Code" button → "Download ZIP"
2. Extract to a folder (e.g., `C:\WhatsApp-Sender`)

**Option B: Clone with Git**

git clone https://github.com/datascience970/whatsapp-bulk-sender.git
cd whatsapp-bulk-sender


Step 3: One-Click Installation
Windows Users:
Double-click install.bat (create this file using the code below)

Wait for installation to complete

Follow the on-screen instructions

Mac/Linux Users:
chmod +x install.sh
./install.sh

Launch the Application
Open your web browser
Go to: http://localhost:8000
You should see the WhatsApp Business Suite interface

💻 How to Use
First Time Setup - Connect WhatsApp
Open the application at http://localhost:8000

Check the status - It will show "Disconnected"

Scan QR Code:

Open WhatsApp on your phone

Go to Settings → Linked Devices → Link a Device

Scan the QR code shown on your computer screen

Wait for connection - Status will change to "Connected"

https://via.placeholder.com/600x200?text=QR+Code+Scanning+Guide

Sending Your First Campaign
Step 1: Generate AI Message (Optional)
Enter what your campaign is about:

text
Example: "Promote our summer sale with 30% discount on all products"
Choose a tone: Professional, Casual, Friendly, Urgent, Promotional, or Humorous

Click "Generate AI Message"

Click "Apply to Campaign" to use it

Step 2: Write or Edit Your Message
Type your message in the "Message Content" box

Emojis work great! 😊

Keep messages under 1500 characters for best results

Use line breaks for readability

Step 3: Add Phone Numbers
Enter numbers one per line or comma-separated:

text
+1234567890
+9876543210
+1122334455
Important: Always include country code (e.g., +1 for USA, +44 for UK)

Step 4: Set Delivery Options
Choose how many messages to send per number (1-50)

The app will show total messages to be sent

Step 5: Validate Numbers (Recommended)
Click "Validate Numbers" to check which numbers have WhatsApp

Step 6: Send Campaign
Click "Execute Campaign"

Confirm the total messages

Watch real-time delivery results

Check success rate in analytics

📊 Understanding the Interface
Main Dashboard
Connection Status: Shows if WhatsApp is connected

AI Message Generator: Create professional content

Message Content: Your campaign message

Send Settings: Configure delivery options

Recipient List: Phone numbers

Campaign Analytics: Results and statistics

Debug Console (Right Panel)
Shows real-time system logs

Helps troubleshoot issues

Displays error messages

Useful for advanced users

