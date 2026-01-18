# Troubleshooting Guide

## Common Issues and Solutions

### 1. Cannot Connect to Camera

#### Symptoms
- Connection timeout
- "Connection refused" errors
- No response from camera

#### Solutions

**Check Network Connectivity:**
```bash
# Ping camera
ping 192.168.1.10

# Check if port 80 is open
nc -zv 192.168.1.10 80

# Or use telnet
telnet 192.168.1.10 80
```

**Verify Camera IP Address:**
1. Check camera label for default IP (usually 192.168.1.10)
2. Use network scanner to find camera:
   ```bash
   nmap -p 80 192.168.1.0/24
   ```
3. Check DHCP server for assigned IP
4. Use manufacturer's discovery tool if available

**Network Configuration Issues:**
- Ensure computer and camera are on same subnet
- Check firewall rules
- Verify switch/router configuration
- Try direct connection (computer ↔ camera)

**Factory Reset:**
1. Locate reset button on camera (usually small pinhole)
2. Press and hold for 10-15 seconds while powered
3. Camera will reset to default IP: 192.168.1.10
4. Default credentials: admin / (empty password)

### 2. Authentication Failed

#### Symptoms
- 401 Unauthorized errors
- "Authentication failed" messages
- Rejected credentials

#### Solutions

**Try Default Credentials:**
```bash
# Default username and empty password
./camera_config.py -i 192.168.1.10 -u admin -p "" info
```

**Test with curl:**
```bash
# Test basic auth
curl -v -u admin: http://192.168.1.10/api/v1/system/info

# Check authentication method (should be Digest)
curl -v http://192.168.1.10/api/v1/system/info 2>&1 | grep -i auth
```

**Password Reset:**
- If password is forgotten, factory reset is required
- No backdoor or default master password exists
- Contact vendor for recovery options

**Check Python Requests Version:**
```bash
# Ensure requests library supports Digest auth
pip install --upgrade requests
python3 -c "import requests; print(requests.__version__)"
```

### 3. RTSP Stream Not Working

#### Symptoms
- VLC shows black screen or "connection failed"
- FFmpeg errors about missing headers
- NVR cannot decode stream
- Errors like "non-existing PPS referenced"

#### This is a Known Issue!

See [RTSP_ISSUE.md](RTSP_ISSUE.md) for complete details.

**Quick Diagnosis:**
```bash
# Check if SDP contains sprop-parameter-sets
curl -u admin: -X DESCRIBE \
     -H "Accept: application/sdp" \
     rtsp://192.168.1.10:554/stream1 2>&1 | grep sprop

# If nothing returned, camera has the bug
```

**Workarounds:**
1. Use HTTP snapshot API instead:
   ```bash
   ./camera_config.py -i 192.168.1.10 snapshot -o image.jpg
   ```

2. Try FFmpeg with error concealment:
   ```bash
   ffmpeg -rtsp_transport tcp -analyzeduration 10000000 \
          -probesize 10000000 -err_detect ignore_err \
          -i rtsp://admin:@192.168.1.10:554/stream1 \
          -c copy output.mp4
   ```

3. Use HTTP-FLV if available:
   ```bash
   ffplay http://192.168.1.10/stream1.flv
   ```

### 4. Slow Response / Timeout

#### Symptoms
- Commands take long time to execute
- Timeout errors
- Intermittent failures

#### Solutions

**Increase Timeout:**
```bash
# CLI
./camera_config.py -i 192.168.1.10 --timeout 30 info

# Python
from camera_config import ConcordCamera
camera = ConcordCamera("192.168.1.10", timeout=30)
```

**Check Network Latency:**
```bash
# Ping with timing
ping -c 10 192.168.1.10

# Traceroute
traceroute 192.168.1.10
```

**Camera Performance:**
- Camera may be overloaded (too many connections)
- High resolution streams can impact API responsiveness
- Reboot camera to clear stuck processes
- Check camera CPU/temperature (if exposed in API)

### 5. Python Import Errors

#### Symptoms
- `ModuleNotFoundError: No module named 'requests'`
- Import failures

#### Solutions

**Install Dependencies:**
```bash
# Using pip
pip install -r requirements.txt

# Or specifically
pip install requests

# For Python 3 specifically
pip3 install requests
```

**Check Python Version:**
```bash
python3 --version  # Should be 3.7+
```

**Virtual Environment:**
```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### 6. API Returns Unexpected Results

#### Symptoms
- Empty responses
- Different JSON structure than documented
- Unknown fields

#### Solutions

**Check Firmware Version:**
```bash
./camera_config.py -i 192.168.1.10 info | grep firmware
```

Different firmware versions may have:
- Different API endpoints
- Different response structures
- Additional or missing fields

**Debug Mode:**
```python
import logging
import requests

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Make request
camera = ConcordCamera("192.168.1.10")
response = camera.get_system_info()
```

**Capture Raw Response:**
```python
from camera_config import ConcordCamera

camera = ConcordCamera("192.168.1.10")
try:
    response = camera._request('GET', '/api/v1/system/info')
    print("Raw response:")
    print(response)
except Exception as e:
    print(f"Error: {e}")
```

### 7. Snapshot Capture Fails

#### Symptoms
- Empty or corrupted images
- Timeout on snapshot request
- "Failed to capture snapshot" error

#### Solutions

**Check Endpoint:**
```bash
# Test with curl
curl -u admin: http://192.168.1.10/api/v1/snapshot?channel=0 -o test.jpg

# Verify file
file test.jpg
```

**Try Different Channel:**
```bash
# Main stream (channel 0)
./camera_config.py -i 192.168.1.10 snapshot --channel 0 -o snap0.jpg

# Sub stream (channel 1)
./camera_config.py -i 192.168.1.10 snapshot --channel 1 -o snap1.jpg
```

**Check Camera Load:**
- Too many simultaneous snapshot requests may fail
- Wait between requests
- Reduce video stream bitrate

### 8. Network Configuration Changes Don't Apply

#### Symptoms
- Settings appear to save but don't take effect
- Camera stays on old IP
- Network settings revert after reboot

#### Solutions

**Verify Settings Were Applied:**
```bash
# Set network config
./camera_config.py -i 192.168.1.10 set-network --ip 192.168.1.100 --dhcp 0

# Wait a moment
sleep 5

# Check on OLD IP if it still responds
./camera_config.py -i 192.168.1.10 network

# Check on NEW IP
./camera_config.py -i 192.168.1.100 network
```

**Reboot Required:**
Some settings may require reboot:
```bash
./camera_config.py -i 192.168.1.10 reboot
```

**DHCP Conflict:**
- If DHCP is enabled, static IP is ignored
- Disable DHCP first: `--dhcp 0`
- Then set static IP

### 9. Motion Detection Not Triggering

#### Symptoms
- No events generated
- No recordings despite motion
- Settings appear saved but don't work

#### Solutions

**Verify Settings:**
```bash
# Check current settings
./camera_config.py -i 192.168.1.10 motion

# Enable with high sensitivity
./camera_config.py -i 192.168.1.10 set-motion --enabled 1 --sensitivity 80
```

**Check Event Configuration:**
- Motion detection may be enabled but events disabled
- Check notification settings via web interface
- Verify webhook/email configuration

**Test Motion:**
- Wave hand in front of camera
- Check detection regions in web interface
- Adjust sensitivity level

### 10. Cannot Access Web Interface

#### Symptoms
- HTTP API works but web interface doesn't load
- Blank page or errors

#### Solutions

**Check Port:**
```bash
# Default is port 80
curl -I http://192.168.1.10/

# Check if non-standard port
./camera_config.py -i 192.168.1.10 network | grep http_port
```

**Browser Compatibility:**
- Try different browser
- Disable browser extensions
- Clear cache and cookies
- Some cameras require Internet Explorer or specific ActiveX controls

**Direct File Access:**
```bash
# Try to access login page directly
curl -v http://192.168.1.10/index.html
curl -v http://192.168.1.10/login.html
```

## Advanced Troubleshooting

### Packet Capture Analysis

```bash
# Capture all traffic to/from camera
tcpdump -i any -s 0 -w camera_traffic.pcap host 192.168.1.10

# Analyze with Wireshark
wireshark camera_traffic.pcap

# Filter for HTTP traffic
http

# Look for:
# - Request/response pairs
# - Authentication headers
# - API endpoints
# - Error responses
```

### Testing API Endpoints Directly

```bash
# List all potential endpoints
for path in system/info system/network video/stream image/settings motion/detection osd/settings; do
    echo "Testing /api/v1/$path"
    curl -s -u admin: http://192.168.1.10/api/v1/$path | head -1
done
```

### Network Port Scan

```bash
# Scan common ports
nmap -p 21,22,23,25,80,443,554,8000,8080,8081 192.168.1.10

# Service detection
nmap -sV 192.168.1.10

# Common camera ports:
# 21   - FTP
# 80   - HTTP API/Web
# 554  - RTSP
# 8000 - Alternative HTTP
# 8080 - Alternative HTTP
```

### Firmware Analysis

```bash
# Check firmware version
./camera_config.py -i 192.168.1.10 info | jq '.data.firmware_version'

# Look for firmware update endpoint
curl -u admin: http://192.168.1.10/api/v1/system/firmware

# Check manufacturer website for updates
```

## Getting Help

If you're still having issues:

1. **Gather Information:**
   - Camera model and firmware version
   - Network configuration
   - Error messages (full text)
   - Steps to reproduce
   - What you've already tried

2. **Create Minimal Test Case:**
   ```python
   from camera_config import ConcordCamera
   camera = ConcordCamera("192.168.1.10")
   print(camera.get_system_info())
   ```

3. **Check Documentation:**
   - [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
   - [RTSP_ISSUE.md](RTSP_ISSUE.md)
   - [EXAMPLES.md](EXAMPLES.md)

4. **Open Issue:**
   - Include all gathered information
   - Attach packet captures if relevant
   - Note any firmware-specific behavior

## Diagnostic Script

Save this as `diagnose.py` and run to collect debug information:

```python
#!/usr/bin/env python3
"""Camera diagnostic script."""

from camera_config import ConcordCamera
import socket
import json

def diagnose_camera(ip):
    """Run comprehensive diagnostics."""
    print(f"Diagnosing camera at {ip}")
    print("="*60)
    
    # Test network connectivity
    print("\n1. Network Connectivity")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, 80))
        sock.close()
        if result == 0:
            print("✓ Port 80 reachable")
        else:
            print("✗ Cannot connect to port 80")
            return
    except Exception as e:
        print(f"✗ Network error: {e}")
        return
    
    # Test authentication
    print("\n2. Authentication")
    try:
        camera = ConcordCamera(ip, timeout=10)
        info = camera.get_system_info()
        print("✓ Authentication successful")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return
    
    # System information
    print("\n3. System Information")
    try:
        print(json.dumps(info, indent=2))
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Network settings
    print("\n4. Network Settings")
    try:
        network = camera.get_network_settings()
        print(json.dumps(network, indent=2))
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Video settings
    print("\n5. Video Settings")
    try:
        video = camera.get_video_stream_settings(channel=0)
        print(json.dumps(video, indent=2))
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # RTSP URL
    print("\n6. RTSP URL")
    try:
        url = camera.get_rtsp_url(1)
        print(f"Main stream: {url}")
        url = camera.get_rtsp_url(2)
        print(f"Sub stream: {url}")
        print("\n⚠ WARNING: RTSP has known issues (missing SPS/PPS headers)")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*60)
    print("Diagnostics complete")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 diagnose.py <camera_ip>")
        sys.exit(1)
    
    diagnose_camera(sys.argv[1])
```

Run with:
```bash
python3 diagnose.py 192.168.1.10
```
