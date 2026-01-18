# Installation & Setup Guide

## Quick Start (5 Minutes)

### 1. Clone Repository

```bash
git clone https://github.com/bosshoggett/Concord-CCTV_Camera-broken-rtsp.git
cd Concord-CCTV_Camera-broken-rtsp
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install directly:
```bash
pip install requests
```

### 3. Test Connection

```bash
./diagnose.py 192.168.1.10
```

Replace `192.168.1.10` with your camera's IP address.

### 4. Start Using

```bash
# Get camera information
./camera_config.py -i 192.168.1.10 info

# Capture a snapshot
./camera_config.py -i 192.168.1.10 snapshot -o test.jpg

# View the snapshot
xdg-open test.jpg  # Linux
open test.jpg      # macOS
```

## Detailed Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Network access to camera

Check Python version:
```bash
python3 --version
```

### Install on Linux

#### Ubuntu/Debian
```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip

# Clone repository
git clone https://github.com/bosshoggett/Concord-CCTV_Camera-broken-rtsp.git
cd Concord-CCTV_Camera-broken-rtsp

# Install dependencies
pip3 install -r requirements.txt

# Make scripts executable
chmod +x camera_config.py diagnose.py

# Test
./camera_config.py --help
```

#### CentOS/RHEL/Fedora
```bash
# Install Python and pip
sudo dnf install python3 python3-pip

# Clone and setup (same as Ubuntu)
git clone https://github.com/bosshoggett/Concord-CCTV_Camera-broken-rtsp.git
cd Concord-CCTV_Camera-broken-rtsp
pip3 install -r requirements.txt
chmod +x camera_config.py diagnose.py
```

### Install on macOS

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python3

# Clone repository
git clone https://github.com/bosshoggett/Concord-CCTV_Camera-broken-rtsp.git
cd Concord-CCTV_Camera-broken-rtsp

# Install dependencies
pip3 install -r requirements.txt

# Make scripts executable
chmod +x camera_config.py diagnose.py

# Test
./camera_config.py --help
```

### Install on Windows

#### Using Python from python.org

1. **Download Python**: https://www.python.org/downloads/
   - Select "Add Python to PATH" during installation

2. **Open Command Prompt or PowerShell**

3. **Clone repository**:
   ```powershell
   git clone https://github.com/bosshoggett/Concord-CCTV_Camera-broken-rtsp.git
   cd Concord-CCTV_Camera-broken-rtsp
   ```

4. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

5. **Test**:
   ```powershell
   python camera_config.py --help
   ```

#### Using WSL (Windows Subsystem for Linux)

Follow the Linux installation instructions within WSL.

### Virtual Environment (Recommended)

Using a virtual environment keeps dependencies isolated:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Use the tools
./camera_config.py -i 192.168.1.10 info

# Deactivate when done
deactivate
```

## Camera Setup

### Initial Connection

1. **Power on camera** (use POE or power adapter)
2. **Connect to network** (ethernet cable)
3. **Find camera IP address**:

   Option A - Check DHCP server (router) for new device
   
   Option B - Use network scanner:
   ```bash
   nmap -p 80 192.168.1.0/24
   ```
   
   Option C - Try default IP:
   ```bash
   ping 192.168.1.10
   ```

4. **Test connection**:
   ```bash
   ./diagnose.py 192.168.1.10
   ```

### Configure Static IP

```bash
# View current network settings
./camera_config.py -i 192.168.1.10 network

# Set static IP
./camera_config.py -i 192.168.1.10 set-network \
  --dhcp 0 \
  --ip 192.168.1.100 \
  --netmask 255.255.255.0 \
  --gateway 192.168.1.1 \
  --dns1 8.8.8.8

# Wait for camera to apply settings (10-30 seconds)
sleep 20

# Verify new IP
./camera_config.py -i 192.168.1.100 network
```

### Change Default Password

**IMPORTANT**: Change the default empty password!

Currently must be done via web interface:
1. Open browser to `http://192.168.1.10`
2. Login: admin / (empty password)
3. Go to Settings → User Management
4. Change admin password
5. Update your scripts with new password:
   ```bash
   ./camera_config.py -i 192.168.1.10 -p "NewPassword" info
   ```

### Configure Video Quality

```bash
# High quality 4K (main stream)
./camera_config.py -i 192.168.1.100 set-video \
  --channel 0 \
  --codec H265 \
  --resolution 3840x2160 \
  --fps 25 \
  --bitrate 8192

# Lower quality for preview (sub stream)
./camera_config.py -i 192.168.1.100 set-video \
  --channel 1 \
  --codec H264 \
  --resolution 1280x720 \
  --fps 15 \
  --bitrate 1024
```

### Optimize Image Settings

```bash
# Adjust for your lighting conditions
./camera_config.py -i 192.168.1.100 set-image \
  --brightness 50 \
  --contrast 50 \
  --saturation 50 \
  --sharpness 55 \
  --wdr 1
```

## Using as Python Library

### Basic Usage

```python
from camera_config import ConcordCamera

# Initialize
camera = ConcordCamera("192.168.1.100", username="admin", password="yourpass")

# Get information
info = camera.get_system_info()
print(f"Camera: {info['data']['model']}")

# Capture snapshot
camera.get_snapshot(channel=0, filename="snapshot.jpg")
```

### In Your Project

Add to your `requirements.txt`:
```
requests>=2.25.0
```

Import the camera module:
```python
import sys
sys.path.insert(0, '/path/to/Concord-CCTV_Camera-broken-rtsp')
from camera_config import ConcordCamera
```

Or copy `camera_config.py` to your project directory.

## Integration Examples

### Home Assistant

Add to `configuration.yaml`:

```yaml
# Use snapshot mode (RTSP is broken)
camera:
  - platform: generic
    name: Front Door Camera
    still_image_url: http://admin:password@192.168.1.100/api/v1/snapshot?channel=0
    verify_ssl: false
```

### Shell Script

```bash
#!/bin/bash
# Capture daily snapshot

DATE=$(date +%Y%m%d_%H%M%S)
./camera_config.py -i 192.168.1.100 snapshot -o "capture_${DATE}.jpg"
```

Save as `capture.sh`, make executable, add to cron:
```bash
chmod +x capture.sh
crontab -e
# Add: 0 * * * * /path/to/capture.sh
```

### Python Monitoring Script

```python
#!/usr/bin/env python3
import time
from camera_config import ConcordCamera

camera = ConcordCamera("192.168.1.100")

while True:
    try:
        # Check if camera is online
        info = camera.get_system_info()
        print(f"Camera online - Uptime: {info['data']['uptime']}s")
        
        # Capture snapshot every hour
        timestamp = int(time.time())
        if timestamp % 3600 == 0:
            camera.get_snapshot(filename=f"snapshot_{timestamp}.jpg")
            print("Snapshot captured")
            
    except Exception as e:
        print(f"Camera offline or error: {e}")
    
    time.sleep(60)
```

## Troubleshooting Installation

### "Command not found"

Ensure scripts are executable:
```bash
chmod +x camera_config.py diagnose.py
```

Or call with Python explicitly:
```bash
python3 camera_config.py -i 192.168.1.10 info
```

### "No module named 'requests'"

Install the dependency:
```bash
pip install requests
# or
pip3 install requests
```

### Permission Denied

Linux/macOS:
```bash
chmod +x camera_config.py
```

Windows: Use `python` prefix:
```powershell
python camera_config.py -i 192.168.1.10 info
```

### Python Version Issues

Ensure Python 3.7+:
```bash
python3 --version
```

If too old, install newer version:
```bash
# Ubuntu
sudo apt install python3.9

# macOS
brew install python@3.9
```

## Network Configuration

### Same Subnet Requirement

Camera and computer must be on same subnet initially.

**Example**:
- Camera: 192.168.1.10 (default)
- Computer: must be 192.168.1.x (x = 2-254, not 10)

### Direct Connection

For isolated testing, connect computer directly to camera:

1. Connect ethernet cable between camera and computer
2. Set computer to static IP: 192.168.1.5
3. Netmask: 255.255.255.0
4. Access camera at: 192.168.1.10

Linux:
```bash
sudo ip addr add 192.168.1.5/24 dev eth0
```

### VLAN Isolation (Recommended)

For security, place cameras on isolated VLAN:

1. Configure switch with camera VLAN (e.g., VLAN 50)
2. Allow routing from management VLAN to camera VLAN
3. Block camera VLAN from internet access
4. Use firewall rules to restrict access

## Next Steps

After installation:

1. ✅ Test connection: `./diagnose.py 192.168.1.10`
2. ✅ Read documentation: `README.md`, `API_DOCUMENTATION.md`
3. ✅ Try examples: `EXAMPLES.md`
4. ⚠️ Read about RTSP issue: `RTSP_ISSUE.md`
5. 🔧 Configure camera settings as needed
6. 🔐 **Change default password!**

## Support

- Documentation: See `*.md` files in repository
- Issues: Open GitHub issue
- Examples: See `EXAMPLES.md`
- Troubleshooting: See `TROUBLESHOOTING.md`

## Updating

```bash
cd Concord-CCTV_Camera-broken-rtsp
git pull
pip install -r requirements.txt --upgrade
```

## Uninstalling

```bash
# Remove repository
cd ..
rm -rf Concord-CCTV_Camera-broken-rtsp

# Remove Python packages (if not needed by other projects)
pip uninstall requests
```
