# Concord CNC81BA-V4 Camera - Reverse Engineering Documentation

Comprehensive reverse engineering documentation for **Concord CNC81BA-V4** / **Guangzhou Juan Optical 4K POE** IP cameras, including full API documentation and Python configuration tool.

## ⚠️ Critical Issue: Broken RTSP Implementation

**These cameras have a critical firmware bug: the RTSP stream is missing SPS/PPS headers**, making the video stream incompatible with most standard video players, NVR systems, and recording software.

See [RTSP_ISSUE.md](RTSP_ISSUE.md) for detailed information about this problem and available workarounds.

## Contents

- [API_DOCUMENTATION.md](API_DOCUMENTATION.md) - Complete HTTP API reference
- [RTSP_ISSUE.md](RTSP_ISSUE.md) - Detailed analysis of RTSP problem and solutions
- [camera_config.py](camera_config.py) - Python client library and CLI tool

## Quick Start

### Prerequisites

```bash
pip install requests
```

### Using the Python Tool

```bash
# Get system information
./camera_config.py -i 192.168.1.10 info

# Get current network settings
./camera_config.py -i 192.168.1.10 network

# Set static IP address
./camera_config.py -i 192.168.1.10 set-network --ip 192.168.1.100 --dhcp 0

# Get video stream settings
./camera_config.py -i 192.168.1.10 video

# Capture snapshot
./camera_config.py -i 192.168.1.10 snapshot -o my_snapshot.jpg

# Get RTSP URL (with warning about broken implementation)
./camera_config.py -i 192.168.1.10 rtsp-url
```

### Using as a Library

```python
from camera_config import ConcordCamera

# Initialize camera client
camera = ConcordCamera("192.168.1.10", username="admin", password="")

# Get system information
info = camera.get_system_info()
print(f"Model: {info['data']['model']}")
print(f"Firmware: {info['data']['firmware_version']}")

# Configure video settings
camera.set_video_stream_settings(
    channel=0,
    codec="H265",
    resolution="3840x2160",
    fps=25,
    bitrate=8192
)

# Capture snapshot
image_data = camera.get_snapshot(channel=0, filename="snapshot.jpg")

# Get RTSP URL (note: stream has known issues)
rtsp_url = camera.get_rtsp_url(channel=1)
print(f"RTSP URL: {rtsp_url}")
```

## Camera Information

### Default Settings

- **Default IP**: 192.168.1.10
- **Default Username**: admin
- **Default Password**: (empty string)
- **HTTP Port**: 80
- **RTSP Port**: 554

### Known Models

This documentation applies to cameras manufactured by Guangzhou Juan Optical Technology Co., Ltd., sold under various brand names:

- Concord CNC81BA-V4
- Generic "4K POE Camera" listings
- Various white-label brands

### Hardware Specifications

- **Resolution**: 4K (3840x2160)
- **Sensor**: 1/2.8" CMOS
- **Video Codec**: H.264 / H.265
- **Network**: 10/100M Ethernet, POE (802.3af)
- **Audio**: Built-in microphone, AAC codec
- **Features**: WDR, Motion Detection, Day/Night mode

## API Features

The HTTP API provides access to:

### System Management
- System information and status
- Network configuration (IP, DNS, ports)
- User management
- Firmware updates
- Reboot and factory reset

### Video Configuration
- Main and sub-stream settings
- Codec selection (H.264/H.265)
- Resolution, FPS, bitrate
- Quality presets

### Image Settings
- Brightness, contrast, saturation
- Sharpness, WDR
- Flip and mirror
- Exposure modes

### Features
- Motion detection configuration
- OSD (On-Screen Display) settings
- Audio settings
- Snapshot capture
- Event notifications (WebSocket)

## RTSP Streaming Issue

### The Problem

The camera's RTSP implementation is **fundamentally broken**:
- Missing SPS (Sequence Parameter Set) headers
- Missing PPS (Picture Parameter Set) headers
- Incompatible with standard video players (VLC, FFmpeg)
- Cannot be recorded by most NVR systems
- Fails with video analysis software

### Impact

- ❌ VLC playback fails
- ❌ FFmpeg recording fails
- ❌ OpenCV capture fails
- ❌ Most NVR systems incompatible
- ❌ Home Assistant integration broken
- ❌ Frigate/Zoneminder incompatible

### Workarounds

1. **Use HTTP snapshots** for still images (works reliably)
2. **Try alternative streaming** (HTTP-FLV or MPEG-TS if available)
3. **Use manufacturer's SDK** (may have workarounds)
4. **Request firmware update** from vendor

See [RTSP_ISSUE.md](RTSP_ISSUE.md) for comprehensive details and troubleshooting.

## HTTP API Examples

### Get System Information

```bash
curl -u admin: http://192.168.1.10/api/v1/system/info
```

### Set Network Configuration

```bash
curl -u admin: -X POST http://192.168.1.10/api/v1/system/network \
  -H "Content-Type: application/json" \
  -d '{
    "dhcp": 0,
    "ip": "192.168.1.100",
    "netmask": "255.255.255.0",
    "gateway": "192.168.1.1"
  }'
```

### Capture Snapshot

```bash
curl -u admin: http://192.168.1.10/api/v1/snapshot?channel=0 -o snapshot.jpg
```

### Set Video Quality

```bash
curl -u admin: -X POST http://192.168.1.10/api/v1/video/stream \
  -H "Content-Type: application/json" \
  -d '{
    "channel": 0,
    "codec": "H265",
    "bitrate": 4096,
    "fps": 25
  }'
```

## Python Tool Reference

### Commands

| Command | Description |
|---------|-------------|
| `info` | Get system information |
| `network` | Get network settings |
| `set-network` | Configure network |
| `video` | Get video stream settings |
| `set-video` | Configure video stream |
| `image` | Get image settings |
| `set-image` | Configure image settings |
| `motion` | Get motion detection settings |
| `set-motion` | Configure motion detection |
| `osd` | Get OSD settings |
| `set-osd` | Configure OSD |
| `snapshot` | Capture snapshot |
| `rtsp-url` | Get RTSP stream URL |
| `reboot` | Reboot camera |
| `reset` | Factory reset |

### Examples

```bash
# View all available commands
./camera_config.py --help

# View command-specific help
./camera_config.py set-video --help

# Use custom credentials
./camera_config.py -i 192.168.1.10 -u admin -p mypassword info

# Set video to 1080p at 30fps
./camera_config.py -i 192.168.1.10 set-video \
  --resolution 1920x1080 \
  --fps 30 \
  --bitrate 2048

# Configure image settings
./camera_config.py -i 192.168.1.10 set-image \
  --brightness 60 \
  --contrast 55 \
  --wdr 1

# Enable motion detection
./camera_config.py -i 192.168.1.10 set-motion \
  --enabled 1 \
  --sensitivity 70
```

## Integration Examples

### Home Assistant (Snapshot Only)

Since RTSP is broken, use snapshot mode:

```yaml
camera:
  - platform: generic
    name: Concord Camera
    still_image_url: http://admin:@192.168.1.10/api/v1/snapshot?channel=0
    verify_ssl: false
```

### Python Script

```python
from camera_config import ConcordCamera
import time

camera = ConcordCamera("192.168.1.10")

# Monitor and save snapshots every 5 seconds
while True:
    filename = f"snapshot_{int(time.time())}.jpg"
    camera.get_snapshot(filename=filename)
    print(f"Saved {filename}")
    time.sleep(5)
```

### Motion Detection Monitor

```python
from camera_config import ConcordCamera

camera = ConcordCamera("192.168.1.10")

# Enable motion detection
camera.set_motion_detection(enabled=1, sensitivity=75)

print("Motion detection enabled. Configure webhook notifications via camera web interface.")
```

## Troubleshooting

### Cannot Connect to Camera

1. Verify camera IP address: `ping 192.168.1.10`
2. Check network connectivity
3. Ensure camera is on same subnet
4. Try default IP: 192.168.1.10
5. Try factory reset (button on camera)

### Authentication Failed

1. Try default credentials: admin / (empty password)
2. Check if password was changed
3. Try factory reset to restore defaults

### RTSP Stream Not Working

This is a **known issue**. The RTSP implementation is broken. See [RTSP_ISSUE.md](RTSP_ISSUE.md) for details.

**Alternative**: Use HTTP snapshot API instead of RTSP streaming.

### API Returns Errors

1. Check firmware version: `./camera_config.py -i 192.168.1.10 info`
2. Some endpoints may vary by firmware version
3. Check API response for error codes
4. Verify request format matches documentation

## Contributing

Contributions welcome! If you discover:
- Additional API endpoints
- Firmware fixes for RTSP issue
- Workarounds for streaming
- Integration examples

Please open an issue or pull request.

## Security Considerations

⚠️ **Important Security Notes**:

1. **Change default password** immediately after setup
2. **Isolate cameras on separate VLAN** - do not expose to internet
3. **Use firewall rules** to restrict access
4. **Update firmware** when security patches are available
5. **Monitor for unusual activity**

These cameras should **NEVER** be directly exposed to the internet.

## Disclaimer

This documentation is provided "as is" for educational and interoperability purposes. The authors are not affiliated with Concord or Guangzhou Juan Optical Technology Co., Ltd.

Use at your own risk. Modifying camera settings may void warranty.

## License

MIT License - See repository for details

## Community & Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Wiki**: Additional examples and integrations

## Acknowledgments

This documentation was created through reverse engineering and community contributions to enable interoperability with these cameras despite their broken RTSP implementation.
