# Quick Reference

## Essential Commands

### Get Camera Info
```bash
./camera_config.py -i 192.168.1.10 info
```

### Capture Snapshot
```bash
./camera_config.py -i 192.168.1.10 snapshot -o image.jpg
```

### Configure Network
```bash
./camera_config.py -i 192.168.1.10 set-network --ip 192.168.1.100 --dhcp 0
```

### Set Video Quality
```bash
./camera_config.py -i 192.168.1.10 set-video --bitrate 4096 --fps 25
```

### Run Diagnostics
```bash
./diagnose.py 192.168.1.10
```

## Default Settings

| Setting | Default Value |
|---------|---------------|
| IP Address | 192.168.1.10 |
| Username | admin |
| Password | (empty) |
| HTTP Port | 80 |
| RTSP Port | 554 |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/system/info` | GET | System information |
| `/api/v1/system/network` | GET/POST | Network settings |
| `/api/v1/video/stream` | GET/POST | Video configuration |
| `/api/v1/image/settings` | GET/POST | Image settings |
| `/api/v1/motion/detection` | GET/POST | Motion detection |
| `/api/v1/osd/settings` | GET/POST | OSD configuration |
| `/api/v1/snapshot` | GET | Capture snapshot |
| `/api/v1/system/reboot` | POST | Reboot camera |

## Python Quick Start

```python
from camera_config import ConcordCamera

# Connect
camera = ConcordCamera("192.168.1.10")

# Get info
info = camera.get_system_info()

# Capture image
camera.get_snapshot(filename="snap.jpg")

# RTSP URL (broken - missing SPS/PPS)
url = camera.get_rtsp_url(1)
```

## Common Issues

### Cannot Connect
- Check IP address: `ping 192.168.1.10`
- Verify same subnet
- Try factory reset

### Authentication Failed
- Try default: admin / (empty)
- Check password in web UI
- Factory reset if forgotten

### RTSP Doesn't Work
**This is a known bug!**
- Missing SPS/PPS headers
- Use snapshot API instead
- See RTSP_ISSUE.md

### Slow Response
- Increase timeout: `--timeout 30`
- Check network latency
- Reboot camera

## File Overview

| File | Purpose |
|------|---------|
| `README.md` | Main documentation |
| `API_DOCUMENTATION.md` | Complete API reference |
| `RTSP_ISSUE.md` | RTSP problem details |
| `EXAMPLES.md` | Code examples |
| `INSTALLATION.md` | Setup instructions |
| `TROUBLESHOOTING.md` | Problem solutions |
| `camera_config.py` | Python client tool |
| `diagnose.py` | Diagnostic script |
| `requirements.txt` | Python dependencies |

## Video Codec Settings

### 4K High Quality
```bash
./camera_config.py -i 192.168.1.10 set-video \
  --codec H265 --resolution 3840x2160 --fps 25 --bitrate 8192
```

### 1080p Balanced
```bash
./camera_config.py -i 192.168.1.10 set-video \
  --codec H264 --resolution 1920x1080 --fps 25 --bitrate 4096
```

### 720p Low Bandwidth
```bash
./camera_config.py -i 192.168.1.10 set-video \
  --codec H264 --resolution 1280x720 --fps 15 --bitrate 1024
```

## Network Configuration Examples

### Static IP
```bash
./camera_config.py -i 192.168.1.10 set-network \
  --dhcp 0 \
  --ip 192.168.1.100 \
  --netmask 255.255.255.0 \
  --gateway 192.168.1.1 \
  --dns1 8.8.8.8
```

### DHCP
```bash
./camera_config.py -i 192.168.1.10 set-network --dhcp 1
```

## Image Presets

### Daytime (Bright)
```bash
./camera_config.py -i 192.168.1.10 set-image \
  --brightness 45 --contrast 50 --saturation 55 --wdr 0
```

### Nighttime (Low Light)
```bash
./camera_config.py -i 192.168.1.10 set-image \
  --brightness 55 --contrast 60 --saturation 45 --wdr 1
```

### High Contrast Scene
```bash
./camera_config.py -i 192.168.1.10 set-image \
  --brightness 50 --contrast 55 --saturation 50 --wdr 1
```

## Motion Detection

### Enable High Sensitivity
```bash
./camera_config.py -i 192.168.1.10 set-motion \
  --enabled 1 --sensitivity 80
```

### Disable
```bash
./camera_config.py -i 192.168.1.10 set-motion --enabled 0
```

## OSD Configuration

### Show Time and Camera Name
```bash
./camera_config.py -i 192.168.1.10 set-osd \
  --show-time 1 \
  --show-name 1 \
  --camera-name "Front Door"
```

## Authentication with Password

```bash
# All commands support -p flag
./camera_config.py -i 192.168.1.10 -u admin -p "MyPassword" info
```

## Batch Operations

### Configure Multiple Cameras
```bash
for ip in 192.168.1.{10..12}; do
  echo "Configuring $ip"
  ./camera_config.py -i $ip set-video --bitrate 4096
done
```

### Health Check All Cameras
```bash
for ip in 192.168.1.{10..12}; do
  ./diagnose.py $ip > "report_${ip}.txt"
done
```

## Integration Snippets

### Home Assistant
```yaml
camera:
  - platform: generic
    still_image_url: http://admin:@192.168.1.10/api/v1/snapshot?channel=0
```

### Cron Job (Hourly Snapshot)
```bash
0 * * * * /path/to/camera_config.py -i 192.168.1.10 snapshot -o "/backups/snap_$(date +\%Y\%m\%d_\%H\%M).jpg"
```

### Python Loop
```python
import time
from camera_config import ConcordCamera

camera = ConcordCamera("192.168.1.10")
while True:
    camera.get_snapshot(filename=f"snap_{int(time.time())}.jpg")
    time.sleep(300)  # Every 5 minutes
```

## Response Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid parameters |
| 2 | Authentication failed |
| 3 | Insufficient permissions |
| 4 | Resource not found |
| 5 | Internal error |
| 6 | Device busy |

## Security Checklist

- [ ] Change default password
- [ ] Use static IP (not DHCP)
- [ ] Place on isolated VLAN
- [ ] Block internet access
- [ ] Use strong password
- [ ] Regular firmware updates
- [ ] Monitor access logs
- [ ] Disable unused features

## Getting Help

1. Check `TROUBLESHOOTING.md`
2. Run `./diagnose.py <ip>`
3. Review `README.md`
4. Check `API_DOCUMENTATION.md`
5. Open GitHub issue with diagnostics output

## Links

- [Full Documentation](README.md)
- [API Reference](API_DOCUMENTATION.md)
- [RTSP Issue Details](RTSP_ISSUE.md)
- [Examples](EXAMPLES.md)
- [Installation](INSTALLATION.md)
- [Troubleshooting](TROUBLESHOOTING.md)
