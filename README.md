🚁 Drone Lab AIC - Inventory Management System
A comprehensive QR-based inventory management system designed specifically for drone laboratories. Track equipment, manage storage units, and access inventory instantly via QR codes.

📱 Live Application
Access the app here: Drone Lab Inventory

🎯 Features
📊 Core Inventory Management
Multi-Storage Support: Create cabinets, shelves, drawers, and custom storage units

Item Tracking: Monitor drones, batteries, controllers, tools, and accessories

Real-time Status: Available, In Use, Maintenance, Broken, Reserved

Categories: Drones, Batteries, Controllers, Propellers, Cameras, Sensors, Tools, Electronics

Quantity Management: Track units, pairs, sets, and custom quantities

🔄 Smart QR Code System
Central QR Code: Full dashboard access with complete management capabilities

Storage-Specific QR: Limited access to view only specific storage contents

Instant Download: Generate and download QR codes for printing

Mobile Optimized: Easy scanning from any smartphone

⚡ Advanced Features
Real-time Sync: Changes appear instantly across all devices

Auto-save: Every modification automatically persists data

Cross-device Access: Use on laptops, tablets, and phones simultaneously

Data Persistence: Inventory data survives reloads and browser sessions

Backup System: Automatic data backups prevent loss

🚀 Quick Start
Access Methods:
Full Access (Management)

Scan the Central QR Code

Or visit: https://drone-lab-inventory-l8phzdn3dqn38cppfacdtr.streamlit.app

Complete dashboard with add/edit/delete capabilities

Limited Access (View Only)

Scan any Storage QR Code

View-only access to specific storage contents

Perfect for lab technicians and quick checks

Basic Operations:
Adding Storage:

Click "➕ Add Storage"

Enter name, location, type, and description

QR code generates automatically

Managing Items:

Expand any storage unit

Use "➕ Add Item" to add new equipment

Click "✏️" to edit or "🗑️" to delete items

QR Code Usage:

Download QR codes from the dashboard

Print and place on storage units

Scan with any smartphone camera

🏗️ System Architecture
Data Flow:
text
Mobile Device ←QR Scan→ Streamlit App ←JSON File→ All Devices
Key Components:
Frontend: Streamlit web application

Data Storage: JSON file with automatic backups

QR Generation: High-quality, scannable codes

Session Management: State preservation across devices

🔧 Technical Details
Dependencies
txt
streamlit==1.28.0
qrcode[pil]==7.4.2
File Structure
text
drone-lab-inventory/
├── app.py                 # Main application
├── requirements.txt       # Python dependencies
├── inventory_data.json    # Inventory database
└── inventory_data.json.backup  # Automatic backups
Data Schema
python
{
  "storages": {
    "storage_id": {
      "name": "Storage Name",
      "type": "cabinet|shelf|drawer|rack",
      "location": "Drone Lab AIC",
      "items": [
        {
          "name": "Item Name",
          "quantity": "X units",
          "status": "Available|In Use|Maintenance",
          "category": "Drones|Batteries|Tools|..."
        }
      ]
    }
  }
}
📈 Usage Statistics
The system automatically tracks:

✅ Total storage units

✅ Item counts per category

✅ Available vs. in-use items

✅ Last update timestamps

✅ Cross-device sync status

🛡️ Data Safety
Automatic Backups: Every save creates a backup

Error Recovery: Graceful handling of file corruption

Data Validation: Structure verification on load

Atomic Operations: Safe concurrent access

🔍 Troubleshooting
Common Issues:
QR Codes Not Scanning:

Ensure good lighting

Use high-contrast printing

Test with multiple phone cameras

Changes Not Appearing:

Wait 20 seconds for auto-refresh

Click "🔄 Force Refresh"

Check internet connection

Data Not Persisting:

Verify browser allows local storage

Check console for error messages

Use "🔄 Force Refresh" to reload

Performance Tips:
Keep item names concise for better QR scannability

Use consistent quantity formats (e.g., "2 units", "5 packs")

Regular maintenance: archive old items, update statuses

🎨 Customization
Adding New Categories:
Edit the categories list in the data structure:

python
'categories': ['Drones', 'Batteries', 'Controllers', 'Your_New_Category']
Modifying Status Options:
Update status options as needed:

python
'status_options': ['Available', 'In Use', 'Maintenance', 'Your_New_Status']
🤝 Contributing
This system is designed for Drone Lab AIC but can be adapted for:

University laboratories

Research facilities

Equipment rental services

Maker spaces and workshops

📞 Support
For technical issues or feature requests, contact Anvesh Sharma.

Built with ❤️ for Drone Lab AIC - Making inventory management effortless through technology! 🚁✨
