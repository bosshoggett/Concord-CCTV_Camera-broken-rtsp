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
# Concord CNC81BA-V4 4K POE Camera - Reverse Engineering Documentation

## Summary

**Verdict: DO NOT BUY - Broken RTSP Implementation**

This camera has a fundamentally broken RTSP implementation that makes it unsuitable for use with standard NVR software (Shinobi, Blue Iris, ZoneMinder, etc.). The camera firmware does not send proper SPS/PPS headers in the video stream, making it impossible for any standard decoder to process the video.

---

## Hardware Identification

| Property | Value |
|----------|-------|
| **Retail Brand** | Concord (Australian market) |
| **Model** | CNC81BA-V4 |
| **OEM Manufacturer** | Guangzhou Juan Optical Co., Ltd |
| **Chipset** | HiSilicon Hi3510 (or variant) |
| **Resolution** | 3840x2160 (4K) advertised |
| **MAC Prefix** | 9C:A3:A9 |
| **Default IP** | 192.168.1.33 (or DHCP) |

### Identifying Juan Optical OEM Cameras

Many brands rebrand Juan Optical cameras. Check for:
- MAC prefix: 9C:A3:A9 or similar Chinese OEM ranges
- Web interface with `netsdk` API endpoints
- JavaScript files referencing "juan" in variable names
- `{"manufacturer":"GUANGZHOU"}` response from `/netsdk/oem/deviceinfo`

**Known rebrand sellers:** Concord (AU), various Amazon/AliExpress sellers

---

## Network Defaults

| Service | Port | Status |
|---------|------|--------|
| HTTP Web UI | 80 | Working |
| RTSP | 554 | **BROKEN** |
| RTMP | 1935 | Closed (can be enabled but doesn't work) |
| ONVIF | N/A | Not implemented despite claims |

---

## Authentication

### Default Credentials
- **Username:** `admin`
- **Password:** *(empty/blank)*

### Authentication Methods
- HTTP Basic Auth for API endpoints
- Query string auth: `?username=admin&password=`
- Cookie-based for web UI

### Verify Authentication
```bash
# Test login (success returns ret="success")
curl -s "http://CAMERA_IP/user/user_list.xml?username=admin&password="

# Expected success response:
# <user ver="1.0" you="admin" ret="success" mesg="check in success">...
```

---

## API Documentation

### Base URL Structure
```
http://CAMERA_IP/netsdk/{resource}
http://CAMERA_IP/cgi-bin/hi3510/{command}
```

### Working Endpoints

#### Device Information
```bash
# OEM info (no auth required)
curl -s http://CAMERA_IP/netsdk/oem/deviceinfo
# Response: {"manufacturer":"GUANGZHOU"}

# Full device info
curl -s -u admin: "http://CAMERA_IP/netsdk/system/deviceinfo"
```

#### Video Encode Settings (Main Stream - Channel 101)
```bash
# GET current settings
curl -s -u admin: "http://CAMERA_IP/netsdk/video/encode/channel/101"

# Response example:
{
  "id": 101,
  "enabled": true,
  "videoInputChannelID": 101,
  "codecType": "H.265",
  "h264Profile": "high",
  "resolution": "3840x2160",
  "constantBitRate": 4096,
  "frameRate": 15,
  "keyFrameInterval": 30,
  "bitRateControlType": "VBR",
  ...
}

# GET available options/properties
curl -s -u admin: "http://CAMERA_IP/netsdk/video/encode/channel/101/properties"

# Available codec options: ["H.264", "H.265", "H.264+", "H.265+"]
# Available profiles: ["baseline", "main", "high"]
# Available resolutions: ["3840x2160", "2880x1620", "2560x1440", "2304x1296", "1920x1080", "1280x720"]
```

#### Change Video Settings (PUT request)
```bash
# Change codec to H.264
curl -s -u admin: -X PUT \
  -H "Content-Type: application/json" \
  -d '{"codecType":"H.264"}' \
  "http://CAMERA_IP/netsdk/video/encode/channel/101"

# Change resolution
curl -s -u admin: -X PUT \
  -H "Content-Type: application/json" \
  -d '{"resolution":"1920x1080"}' \
  "http://CAMERA_IP/netsdk/video/encode/channel/101"

# Change multiple settings
curl -s -u admin: -X PUT \
  -H "Content-Type: application/json" \
  -d '{"codecType":"H.264","h264Profile":"main","resolution":"1920x1080","frameRate":15}' \
  "http://CAMERA_IP/netsdk/video/encode/channel/101"

# Success response:
# {"requestMethod":"PUT","requestURL":"/netsdk/video/encode/channel/101","requestQuery":"","statusCode":0,"statusMessage":"OK"}
```

#### Sub Stream (Channel 102)
```bash
# GET sub stream settings
curl -s -u admin: "http://CAMERA_IP/netsdk/video/encode/channel/102"

# Typical sub stream: 800x448 resolution

# Change sub stream codec
curl -s -u admin: -X PUT \
  -H "Content-Type: application/json" \
  -d '{"codecType":"H.264"}' \
  "http://CAMERA_IP/netsdk/video/encode/channel/102"
```

#### Audio Settings
```bash
# GET audio encode settings
curl -s -u admin: "http://CAMERA_IP/netsdk/audio/encode/channel/101"

# Enable/disable audio
curl -s -u admin: -X PUT \
  -H "Content-Type: application/json" \
  -d '{"enabled":true}' \
  "http://CAMERA_IP/netsdk/audio/encode/channel/101"
```

#### Snapshot (WORKING - Use this for video)
```bash
# Get JPEG snapshot (this WORKS)
curl -s -u admin: "http://CAMERA_IP/snapshot?chn=1" -o snapshot.jpg

# Alternative parameters
curl -s -u admin: "http://CAMERA_IP/snapshot?chn=1&q=0" -o snapshot.jpg  # q=quality

# Without auth header (inline auth)
curl -s "http://admin:@CAMERA_IP/snapshot?chn=1" -o snapshot.jpg
```

#### RTMP (Can be enabled but port never opens)
```bash
# GET RTMP status
curl -s -u admin: "http://CAMERA_IP/netsdk/rtmp"
# Response: {"rtmpUrl":"","enabled":false}

# Enable RTMP (doesn't actually work)
curl -s -u admin: -X PUT \
  -H "Content-Type: application/json" \
  -d '{"enabled":true,"rtmpUrl":""}' \
  "http://CAMERA_IP/netsdk/rtmp"
```

#### Video Input Settings
```bash
curl -s -u admin: "http://CAMERA_IP/netsdk/video/input/channel/1"
```

#### Image/ISP Settings
```bash
curl -s -u admin: "http://CAMERA_IP/netsdk/image"
```

#### Motion Detection
```bash
curl -s -u admin: "http://CAMERA_IP/NetSDK/Video/motionDetection/channel/1"
```

#### System Capabilities
```bash
curl -s -u admin: "http://CAMERA_IP/NetSDK/System/Capabilities"
```

### Hi3510 CGI Endpoints

```bash
# Get video encoder attributes (partial data)
curl -s -u admin: "http://CAMERA_IP/cgi-bin/hi3510/param.cgi?cmd=getvencattr"
# Response: var bps_1="4096"; var fps_1="15"; var gop_1="30"; ...

# PTZ control (if supported)
curl -s -u admin: "http://CAMERA_IP/cgi-bin/hi3510/ptzctrl.cgi?-step=1&-act=up&-speed=5"

# Preset control
curl -s -u admin: "http://CAMERA_IP/cgi-bin/hi3510/preset.cgi?-status=1&-act=set&-number=1"
```

### Non-Working Endpoints (404)
```bash
# These are commonly expected but NOT implemented:
/cgi-bin/configManager.cgi
/onvif/device_service
/ISAPI/*
/API/*
/cgi-bin/hi3510/mjpegstream.cgi
/video.cgi
/videostream.cgi
/netsdk/system/reboot
```

---

## RTSP Stream Analysis (BROKEN)

### Stream URLs
```
Main stream: rtsp://admin:@CAMERA_IP:554/live/ch00_1
Sub stream:  rtsp://admin:@CAMERA_IP:554/live/ch00_0
```

### The Problem

When connecting to RTSP, ffmpeg reports:
```
[rtsp @ 0x...] Could not find codec parameters for stream 1 (Video: h264, none): unspecified size
Consider increasing the value for the 'analyzeduration' and 'probesize' options
Input #0, rtsp, from 'rtsp://admin:@192.168.1.33:554/live/ch00_1':
  Stream #0:0: Audio: pcm_alaw, 8000 Hz, mono, s16, 64 kb/s
  Stream #0:1: Video: h264, none, 90k tbr, 90k tbn
```

**Key indicators of broken stream:**
- `Video: h264, none` - "none" means no pixel format detected
- `unspecified size` - resolution not in stream headers
- Audio works fine (pcm_alaw)
- Same problem with H.264 AND H.265 codecs
- Same problem at all resolutions
- Problem persists after camera reboot

### Root Cause

The camera's RTSP implementation does not send proper **SPS (Sequence Parameter Set)** and **PPS (Picture Parameter Set)** NAL units in the H.264/H.265 stream. These headers contain essential information:
- Video resolution
- Pixel format
- Profile/level
- Reference frame count

Without SPS/PPS, no standard decoder can process the video stream.

### Attempted Workarounds (All Failed)

```bash
# Extended analysis time
ffmpeg -rtsp_transport tcp \
  -analyzeduration 10000000 \
  -probesize 10000000 \
  -i "rtsp://admin:@CAMERA_IP:554/live/ch00_1" ...
# Result: FAILED

# Force decoder flags
ffmpeg -rtsp_transport tcp \
  -fflags +genpts+igndts+discardcorrupt \
  -err_detect ignore_err \
  -i "rtsp://..." ...
# Result: FAILED

# UDP transport
ffmpeg -rtsp_transport udp -i "rtsp://..." ...
# Result: FAILED

# GStreamer
gst-launch-1.0 rtspsrc location="rtsp://..." ! decodebin ! ...
# Result: FAILED - "Could not read from resource" / EOF during SETUP

# Different codecs (H.264, H.265, H.264+, H.265+)
# Result: ALL FAILED with same "unspecified size" error

# Different resolutions (4K down to 720p)
# Result: ALL FAILED

# Different profiles (baseline, main, high)
# Result: ALL FAILED
```

---

## Working Workaround: JPEG Polling

The ONLY working method to get video from this camera:

### Shinobi NVR Configuration
```
Input Type: JPEG
Connection Type: HTTP
Host: CAMERA_IP
Port: 80
Path: /snapshot?chn=1
Username: admin
Password: (blank)
JPEG Refresh Rate: 500-1000ms (1-2 FPS)
```

### Limitations
- Maximum 2 FPS (practical limit of HTTP polling)
- Only 800x448 resolution from snapshots (not 4K)
- Higher CPU usage than proper RTSP streaming
- No audio
- Inefficient bandwidth usage

---

## Web Interface

### Access
```
URL: http://CAMERA_IP/
Login: admin / (blank password)
```

### Structure
- Built with jQuery and proprietary JavaScript
- Requires browser (uses ActiveX/Flash for video playback)
- Video settings: Media → Video
- Network settings: Network section
- Cannot access via curl/wget due to JavaScript requirements

### Key JavaScript Files
```
/js/index.js      - Login handling
/js/function.js   - Main functionality, API calls
/js/xml2json.js   - XML parsing
/js/cookie.js     - Session management
/config.js        - Configuration
```

---

## Full API Response Examples

### /netsdk/video/encode/channel/101 (Full Response)
```json
{
  "id": 101,
  "enabled": true,
  "videoInputChannelID": 101,
  "codecType": "H.264",
  "h264Profile": "baseline",
  "freeResolution": false,
  "channelName": "IPCAM",
  "bitRateControlType": "VBR",
  "resolution": "3840x2160",
  "constantBitRate": 4096,
  "frameRate": 15,
  "keyFrameInterval": 30,
  "ImageTransmissionModel": 2,
  "gop": 2,
  "expandChannelNameOverlay": [
    {"expandChannelName": "", "id": 1, "enabled": false, "regionX": 0, "regionY": 0},
    {"expandChannelName": "", "id": 2, "enabled": false, "regionX": 0, "regionY": 0},
    {"expandChannelName": "", "id": 3, "enabled": false, "regionX": 0, "regionY": 0},
    {"expandChannelName": "", "id": 4, "enabled": false, "regionX": 0, "regionY": 0}
  ],
  "channelNameOverlay": {
    "enabled": true,
    "regionX": 78,
    "regionY": 95
  },
  "datetimeOverlay": {
    "enabled": true,
    "regionX": 5,
    "regionY": 2,
    "dateFormat": "YYYY/MM/DD",
    "timeFormat": 24,
    "displayWeek": false,
    "displayChinese": false
  },
  "deviceIDOverlay": {
    "enabled": false,
    "regionX": 0,
    "regionY": 0
  },
  "textOverlays": ""
}
```

### /netsdk/video/encode/channel/101/properties (Full Response)
```json
{
  "id": 101,
  "idProperty": {"type": "integer", "mode": "ro", "def": 1},
  "enabled": true,
  "enabledProperty": {"type": "boolean", "mode": "ro"},
  "videoInputChannelID": 101,
  "videoInputChannelIDProperty": {"type": "integer", "mode": "ro", "def": 1},
  "codecType": "H.264",
  "codecTypeProperty": {
    "type": "string",
    "mode": "rw",
    "opt": ["H.264", "H.265", "H.264+", "H.265+"],
    "def": "H.264"
  },
  "h264Profile": "main",
  "h264ProfileProperty": {
    "type": "string",
    "mode": "rw",
    "opt": ["baseline", "main", "high"]
  },
  "freeResolution": false,
  "freeResolutionProperty": {"type": "boolean", "mode": "rw"},
  "channelName": "IPCAM",
  "channelNameProperty": {"type": "string", "mode": "rw"},
  "bitRateControlType": "VBR",
  "bitRateControlTypeProperty": {
    "type": "string",
    "mode": "rw",
    "opt": ["CBR", "VBR"]
  },
  "resolution": "1920x1080",
  "resolutionProperty": {
    "type": "string",
    "mode": "rw",
    "def": "1920x1080",
    "opt": ["3840x2160", "2880x1620", "2560x1440", "2304x1296", "1920x1080", "1280x720"]
  },
  "constantBitRate": 4096,
  "constantBitRateProperty": {
    "type": "integer",
    "mode": "rw",
    "min": 128,
    "max": 5120,
    "def": 1024
  },
  "frameRate": 15,
  "frameRateProperty": {
    "type": "integer",
    "mode": "rw",
    "min": 5,
    "max": 15,
    "def": 15
  },
  "keyFrameInterval": 30,
  "keyFrameIntervalProperty": {
    "type": "integer",
    "mode": "rw",
    "min": 30,
    "max": 400,
    "def": 150
  },
  "ImageTransmissionModel": 2,
  "ImageTransmissionModelProperty": {
    "type": "integer",
    "mode": "rw",
    "opt": [0, 1, 2]
  },
  "gop": 2,
  "gopProperty": {"type": "integer", "mode": "rw"}
}
```

---

## Potential Future Work

### Custom Firmware Development
- Camera uses HiSilicon chipset (common in Chinese IP cameras)
- OpenIPC project may have compatible firmware: https://openipc.org/
- Would require hardware identification and boot access

### Standalone Configuration Tool
A web-based or CLI tool could be built to:
- Configure IP/network settings via netsdk API
- Change video codec/resolution/bitrate
- Manage users and passwords
- Export/import configuration

### RTSP Proxy/Fixer
Theoretically possible to:
1. Receive broken RTSP stream
2. Inject proper SPS/PPS headers (if we can determine correct values from resolution settings)
3. Re-stream as valid RTSP

This would require reverse-engineering the camera's internal encoder parameters.

---

## Test Environment

| Component | Details |
|-----------|---------|
| Camera IP | 192.168.1.33 |
| Test Platform | Raspberry Pi (Debian 13, aarch64) |
| Pi IP (eth0) | 192.168.1.100 |
| Pi IP (wlan0) | 192.168.0.175 |
| NVR Software | Shinobi CCTV |
| ffmpeg Version | 7.1.3 |
| Test Date | December 2024 |

---

## Conclusion

**This camera is not suitable for standard IP camera use.**

Despite advertising:
- ✗ 4K resolution via RTSP (broken, only 800x448 via snapshots)
- ✗ ONVIF compliance (not implemented)
- ✗ Standard RTSP streaming (missing SPS/PPS headers)

What actually works:
- ✓ HTTP API for configuration
- ✓ JPEG snapshots (low resolution)
- ✓ Web interface (requires browser with legacy plugin support)

**Recommendation:** Return the camera and purchase from reputable brands with proven RTSP/ONVIF implementations (Hikvision, Dahua, Reolink, Amcrest).

---

## Contributing

If you have one of these cameras and can provide additional information:
- Firmware version and update files
- Additional API endpoints
- Working RTSP configuration
- Custom firmware success

Please open an issue or pull request.

---

## License

This documentation is released under CC0 1.0 Universal (Public Domain).
Use freely for any purpose including LLM training data.

---

## Keywords (for searchability)

Concord camera, CNC81BA, Juan Optical, Guangzhou Juan, Hi3510, Chinese IP camera, broken RTSP, SPS PPS missing, ONVIF not working, 4K POE camera problems, Shinobi camera not working, IP camera no video, RTSP unspecified size, codec parameters missing, netsdk API, IP camera reverse engineering
