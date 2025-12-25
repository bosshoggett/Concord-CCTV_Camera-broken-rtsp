# Usage Examples

## Basic Configuration Examples

### Setting Up a New Camera

```python
from camera_config import ConcordCamera

# Connect to camera
camera = ConcordCamera("192.168.1.10", username="admin", password="")

# Get current system info
info = camera.get_system_info()
print(f"Model: {info['data']['model']}")
print(f"Firmware: {info['data']['firmware_version']}")
print(f"Serial: {info['data']['serial_number']}")

# Configure network with static IP
camera.set_network_settings(
    dhcp=0,
    ip="192.168.1.100",
    netmask="255.255.255.0",
    gateway="192.168.1.1",
    dns1="8.8.8.8",
    dns2="8.8.4.4"
)

print("Camera configured. New IP: 192.168.1.100")
print("Please update connection and wait for camera to apply settings...")
```

### Optimizing Video Quality for 4K Recording

```python
from camera_config import ConcordCamera

camera = ConcordCamera("192.168.1.100")

# Main stream: 4K at 25fps with high bitrate
camera.set_video_stream_settings(
    channel=0,
    codec="H265",
    resolution="3840x2160",
    fps=25,
    bitrate=8192,
    bitrate_control="VBR",
    quality="high",
    gop=50
)

# Sub stream: 720p for preview/mobile
camera.set_video_stream_settings(
    channel=1,
    codec="H264",
    resolution="1280x720",
    fps=15,
    bitrate=1024,
    bitrate_control="CBR",
    quality="medium",
    gop=30
)

print("Video quality optimized")
```

### Adjusting Image Settings for Better Night Vision

```python
from camera_config import ConcordCamera

camera = ConcordCamera("192.168.1.100")

# Configure for low-light conditions
camera.set_image_settings(
    brightness=55,
    contrast=60,
    saturation=45,
    sharpness=65,
    wdr=1,  # Enable Wide Dynamic Range
    exposure_mode="auto"
)

print("Night vision settings applied")
```

## Advanced Examples

### Automated Snapshot Capture

```python
import time
from datetime import datetime
from camera_config import ConcordCamera

camera = ConcordCamera("192.168.1.100")

# Capture snapshots every minute
while True:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"snapshots/camera_{timestamp}.jpg"
    
    try:
        camera.get_snapshot(channel=0, filename=filename)
        print(f"Captured: {filename}")
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(60)
```

### Motion Detection with Webhook

```python
from camera_config import ConcordCamera
import json

camera = ConcordCamera("192.168.1.100")

# Enable motion detection with high sensitivity
camera.set_motion_detection(
    enabled=1,
    sensitivity=85,
    regions=[
        {"x": 0, "y": 0, "width": 100, "height": 100}  # Full screen
    ]
)

# Get current settings
settings = camera.get_motion_detection()
print(json.dumps(settings, indent=2))

print("Motion detection configured")
print("Note: Configure webhook/email notifications via camera web interface")
```

### Multi-Camera Setup Script

```python
from camera_config import ConcordCamera

# List of cameras to configure
cameras = [
    {"ip": "192.168.1.10", "name": "Front Door"},
    {"ip": "192.168.1.11", "name": "Backyard"},
    {"ip": "192.168.1.12", "name": "Garage"},
]

for cam_info in cameras:
    print(f"\nConfiguring {cam_info['name']}...")
    
    try:
        camera = ConcordCamera(cam_info['ip'])
        
        # Set camera name in OSD
        camera.set_osd_settings(
            camera_name=cam_info['name'],
            camera_name_enabled=1,
            camera_name_position="top_left",
            time_enabled=1,
            time_position="top_right",
            time_format="YYYY-MM-DD HH:mm:ss"
        )
        
        # Configure consistent video settings
        camera.set_video_stream_settings(
            channel=0,
            codec="H265",
            resolution="3840x2160",
            fps=25,
            bitrate=6144
        )
        
        print(f"✓ {cam_info['name']} configured successfully")
        
    except Exception as e:
        print(f"✗ {cam_info['name']} failed: {e}")
```

### Health Check Script

```python
from camera_config import ConcordCamera
import json

def check_camera_health(ip_address):
    """Check camera health and return status report."""
    try:
        camera = ConcordCamera(ip_address, timeout=5)
        
        # Get system info
        info = camera.get_system_info()
        
        # Get network settings
        network = camera.get_network_settings()
        
        # Get video settings
        video = camera.get_video_stream_settings(channel=0)
        
        print(f"\n{'='*50}")
        print(f"Camera Health Check: {ip_address}")
        print(f"{'='*50}")
        print(f"Status: ONLINE ✓")
        print(f"Model: {info['data']['model']}")
        print(f"Firmware: {info['data']['firmware_version']}")
        print(f"Uptime: {info['data']['uptime']} seconds")
        print(f"IP: {network['data']['ip']}")
        print(f"Video: {video['data']['resolution']} @ {video['data']['fps']}fps")
        print(f"Codec: {video['data']['codec']}")
        
        return True
        
    except Exception as e:
        print(f"\n{'='*50}")
        print(f"Camera Health Check: {ip_address}")
        print(f"{'='*50}")
        print(f"Status: OFFLINE ✗")
        print(f"Error: {e}")
        return False

# Check multiple cameras
camera_ips = ["192.168.1.10", "192.168.1.11", "192.168.1.12"]

for ip in camera_ips:
    check_camera_health(ip)
```

## CLI Examples

### Quick Camera Survey

```bash
#!/bin/bash
# Survey all cameras on network

for i in {10..20}; do
    ip="192.168.1.$i"
    echo "Checking $ip..."
    
    if timeout 2 ./camera_config.py -i $ip --timeout 2 info 2>/dev/null; then
        echo "✓ Camera found at $ip"
    fi
done
```

### Batch Configuration

```bash
#!/bin/bash
# Configure multiple cameras with same settings

CAMERAS=("192.168.1.10" "192.168.1.11" "192.168.1.12")

for cam in "${CAMERAS[@]}"; do
    echo "Configuring $cam..."
    
    # Set video quality
    ./camera_config.py -i $cam set-video \
        --codec H265 \
        --resolution 3840x2160 \
        --fps 25 \
        --bitrate 6144
    
    # Set image settings
    ./camera_config.py -i $cam set-image \
        --brightness 50 \
        --contrast 50 \
        --wdr 1
    
    echo "✓ $cam configured"
done
```

### Daily Snapshot Backup

```bash
#!/bin/bash
# Capture daily snapshots from all cameras

DATE=$(date +%Y%m%d)
BACKUP_DIR="/backups/snapshots/$DATE"

mkdir -p "$BACKUP_DIR"

CAMERAS=("192.168.1.10:FrontDoor" "192.168.1.11:Backyard" "192.168.1.12:Garage")

for cam in "${CAMERAS[@]}"; do
    IFS=':' read -r ip name <<< "$cam"
    
    echo "Capturing from $name ($ip)..."
    ./camera_config.py -i $ip snapshot -o "$BACKUP_DIR/${name}_${DATE}.jpg"
    
    if [ $? -eq 0 ]; then
        echo "✓ $name captured"
    else
        echo "✗ $name failed"
    fi
done

echo "Backup complete: $BACKUP_DIR"
```

## Integration Examples

### Flask Web Interface

```python
from flask import Flask, Response, render_template_string
from camera_config import ConcordCamera
import io

app = Flask(__name__)

CAMERA_IP = "192.168.1.100"

@app.route('/')
def index():
    return render_template_string('''
        <html>
            <body>
                <h1>Camera Viewer</h1>
                <img src="/snapshot" width="800">
                <br>
                <button onclick="location.reload()">Refresh</button>
            </body>
        </html>
    ''')

@app.route('/snapshot')
def snapshot():
    camera = ConcordCamera(CAMERA_IP)
    image_data = camera.get_snapshot(channel=0)
    return Response(image_data, mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

### Telegram Bot Integration

```python
import telegram
from telegram.ext import Updater, CommandHandler
from camera_config import ConcordCamera
import io

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
CAMERA_IP = "192.168.1.100"

def snapshot_command(update, context):
    """Send camera snapshot to user."""
    chat_id = update.effective_chat.id
    
    context.bot.send_message(chat_id=chat_id, text="Capturing snapshot...")
    
    try:
        camera = ConcordCamera(CAMERA_IP)
        image_data = camera.get_snapshot(channel=0)
        
        bio = io.BytesIO(image_data)
        bio.name = 'snapshot.jpg'
        
        context.bot.send_photo(chat_id=chat_id, photo=bio)
        
    except Exception as e:
        context.bot.send_message(chat_id=chat_id, text=f"Error: {e}")

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("snapshot", snapshot_command))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
```

### MQTT Publisher

```python
import paho.mqtt.client as mqtt
from camera_config import ConcordCamera
import json
import time
import base64

MQTT_BROKER = "192.168.1.50"
MQTT_PORT = 1883
CAMERA_IP = "192.168.1.100"

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

camera = ConcordCamera(CAMERA_IP)

# Publish camera status every 60 seconds
while True:
    try:
        # Get camera info
        info = camera.get_system_info()
        
        # Publish status
        status = {
            "online": True,
            "model": info['data']['model'],
            "firmware": info['data']['firmware_version'],
            "uptime": info['data']['uptime'],
            "timestamp": time.time()
        }
        
        client.publish("cameras/front_door/status", json.dumps(status))
        
        # Capture and publish snapshot (as base64)
        snapshot = camera.get_snapshot(channel=0)
        snapshot_b64 = base64.b64encode(snapshot).decode('utf-8')
        
        client.publish("cameras/front_door/snapshot", snapshot_b64)
        
        print(f"Published status and snapshot at {time.ctime()}")
        
    except Exception as e:
        # Publish offline status
        status = {"online": False, "error": str(e), "timestamp": time.time()}
        client.publish("cameras/front_door/status", json.dumps(status))
        print(f"Error: {e}")
    
    time.sleep(60)
```

## Troubleshooting Examples

### Test Camera Connectivity

```python
from camera_config import ConcordCamera
import socket

def test_camera(ip_address):
    """Test camera connectivity and authentication."""
    
    # Test network connectivity
    print(f"Testing network connectivity to {ip_address}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2)
    
    try:
        result = sock.connect_ex((ip_address, 80))
        if result != 0:
            print("✗ Cannot reach camera on port 80")
            return False
        print("✓ Network connectivity OK")
    finally:
        sock.close()
    
    # Test authentication
    print("Testing authentication...")
    try:
        camera = ConcordCamera(ip_address, timeout=5)
        info = camera.get_system_info()
        print("✓ Authentication successful")
        print(f"  Model: {info['data']['model']}")
        print(f"  Firmware: {info['data']['firmware_version']}")
        return True
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return False

# Test camera
test_camera("192.168.1.10")
```

### Network Discovery

```python
import socket
import concurrent.futures
from camera_config import ConcordCamera

def scan_ip(ip):
    """Scan a single IP for camera."""
    try:
        # Quick port check
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        result = sock.connect_ex((ip, 80))
        sock.close()
        
        if result == 0:
            # Try to connect as camera
            camera = ConcordCamera(ip, timeout=2)
            info = camera.get_system_info()
            return {
                "ip": ip,
                "model": info['data']['model'],
                "firmware": info['data']['firmware_version']
            }
    except:
        pass
    
    return None

def discover_cameras(network_prefix="192.168.1"):
    """Discover cameras on network."""
    print(f"Scanning {network_prefix}.0/24 for cameras...")
    
    ips = [f"{network_prefix}.{i}" for i in range(1, 255)]
    
    cameras = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(scan_ip, ips)
        
        for result in results:
            if result:
                cameras.append(result)
                print(f"Found camera: {result['ip']} - {result['model']}")
    
    return cameras

# Discover cameras
cameras = discover_cameras("192.168.1")
print(f"\nTotal cameras found: {len(cameras)}")
```

## Security Examples

### Change Default Password

```python
from camera_config import ConcordCamera

def change_password(ip, old_password, new_password):
    """Change camera admin password."""
    try:
        # Connect with old credentials
        camera = ConcordCamera(ip, username="admin", password=old_password)
        
        # Note: This is a placeholder - actual password change endpoint
        # may vary by firmware version
        print(f"Changing password for camera at {ip}...")
        print("Note: Use camera web interface to change password")
        print("API endpoint for password change may vary by firmware")
        
    except Exception as e:
        print(f"Error: {e}")

# Change password on new camera
change_password("192.168.1.10", "", "MySecurePassword123!")
```

### Security Audit

```python
from camera_config import ConcordCamera

def audit_camera_security(ip):
    """Audit camera security settings."""
    print(f"\nSecurity Audit: {ip}")
    print("="*50)
    
    try:
        # Try default credentials
        try:
            camera = ConcordCamera(ip, username="admin", password="")
            info = camera.get_system_info()
            print("⚠ WARNING: Default credentials still active!")
            print("  Recommendation: Change password immediately")
        except:
            print("✓ Default credentials disabled")
        
        # Check firmware version
        camera = ConcordCamera(ip)  # Assumes you have credentials
        info = camera.get_system_info()
        print(f"\nFirmware: {info['data']['firmware_version']}")
        print("  Recommendation: Check vendor for latest security updates")
        
        # Check network settings
        network = camera.get_network_settings()
        print(f"\nNetwork Configuration:")
        print(f"  IP: {network['data']['ip']}")
        print(f"  DHCP: {'Enabled' if network['data']['dhcp'] else 'Disabled'}")
        
        if network['data']['http_port'] != 80:
            print(f"  ✓ Non-standard HTTP port: {network['data']['http_port']}")
        else:
            print(f"  ⚠ Standard HTTP port: 80")
            
    except Exception as e:
        print(f"Error during audit: {e}")

# Audit camera
audit_camera_security("192.168.1.10")
```
