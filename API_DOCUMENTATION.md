# Camera API Documentation

## Concord CNC81BA-V4 / Guangzhou Juan Optical 4K POE Camera

This document provides comprehensive API documentation for the Concord CNC81BA-V4 camera, which is also sold under various brand names and is manufactured by Guangzhou Juan Optical Technology Co., Ltd.

### Base Information

- **Manufacturer**: Guangzhou Juan Optical Technology Co., Ltd.
- **Model**: CNC81BA-V4 (and various OEM versions)
- **Default IP**: 192.168.1.10
- **Default HTTP Port**: 80
- **Default RTSP Port**: 554
- **Default Username**: admin
- **Default Password**: (empty string)

### Authentication

The camera uses HTTP Digest Authentication for most endpoints.

#### Login Endpoint

```
GET /api/v1/user/login
```

**Parameters:**
- `username`: Admin username (default: "admin")
- `password`: Admin password (default: empty)

**Response:**
```json
{
  "result": 0,
  "token": "session_token_here"
}
```

### Network Configuration

#### Get Network Settings

```
GET /api/v1/system/network
```

**Authentication**: Required

**Response:**
```json
{
  "result": 0,
  "data": {
    "dhcp": 0,
    "ip": "192.168.1.10",
    "netmask": "255.255.255.0",
    "gateway": "192.168.1.1",
    "dns1": "8.8.8.8",
    "dns2": "8.8.4.4",
    "http_port": 80,
    "rtsp_port": 554
  }
}
```

#### Set Network Settings

```
POST /api/v1/system/network
Content-Type: application/json
```

**Authentication**: Required

**Request Body:**
```json
{
  "dhcp": 0,
  "ip": "192.168.1.100",
  "netmask": "255.255.255.0",
  "gateway": "192.168.1.1",
  "dns1": "8.8.8.8",
  "dns2": "8.8.4.4"
}
```

### Video Configuration

#### Get Video Stream Settings

```
GET /api/v1/video/stream?channel=0
```

**Authentication**: Required

**Parameters:**
- `channel`: Video channel (0 for main stream, 1 for sub stream)

**Response:**
```json
{
  "result": 0,
  "data": {
    "channel": 0,
    "codec": "H265",
    "resolution": "3840x2160",
    "fps": 25,
    "bitrate": 8192,
    "bitrate_control": "VBR",
    "quality": "high",
    "gop": 50
  }
}
```

#### Set Video Stream Settings

```
POST /api/v1/video/stream
Content-Type: application/json
```

**Authentication**: Required

**Request Body:**
```json
{
  "channel": 0,
  "codec": "H265",
  "resolution": "3840x2160",
  "fps": 25,
  "bitrate": 8192,
  "bitrate_control": "VBR",
  "quality": "high",
  "gop": 50
}
```

### Image Settings

#### Get Image Settings

```
GET /api/v1/image/settings
```

**Authentication**: Required

**Response:**
```json
{
  "result": 0,
  "data": {
    "brightness": 50,
    "contrast": 50,
    "saturation": 50,
    "hue": 50,
    "sharpness": 50,
    "flip": 0,
    "mirror": 0,
    "wdr": 1,
    "exposure_mode": "auto"
  }
}
```

#### Set Image Settings

```
POST /api/v1/image/settings
Content-Type: application/json
```

**Authentication**: Required

**Request Body:**
```json
{
  "brightness": 50,
  "contrast": 50,
  "saturation": 50,
  "hue": 50,
  "sharpness": 50,
  "flip": 0,
  "mirror": 0,
  "wdr": 1,
  "exposure_mode": "auto"
}
```

### Motion Detection

#### Get Motion Detection Settings

```
GET /api/v1/motion/detection
```

**Authentication**: Required

**Response:**
```json
{
  "result": 0,
  "data": {
    "enabled": 1,
    "sensitivity": 50,
    "regions": [
      {
        "x": 0,
        "y": 0,
        "width": 100,
        "height": 100
      }
    ]
  }
}
```

#### Set Motion Detection

```
POST /api/v1/motion/detection
Content-Type: application/json
```

**Authentication**: Required

**Request Body:**
```json
{
  "enabled": 1,
  "sensitivity": 50,
  "regions": [
    {
      "x": 0,
      "y": 0,
      "width": 100,
      "height": 100
    }
  ]
}
```

### System Information

#### Get System Information

```
GET /api/v1/system/info
```

**Authentication**: Required

**Response:**
```json
{
  "result": 0,
  "data": {
    "model": "CNC81BA-V4",
    "hardware_version": "V4.0",
    "firmware_version": "V1.0.0.20",
    "serial_number": "ABC123456789",
    "uptime": 86400,
    "system_time": "2023-01-01T12:00:00Z"
  }
}
```

#### Reboot System

```
POST /api/v1/system/reboot
```

**Authentication**: Required

**Response:**
```json
{
  "result": 0,
  "message": "System rebooting"
}
```

#### Factory Reset

```
POST /api/v1/system/reset
```

**Authentication**: Required

**Response:**
```json
{
  "result": 0,
  "message": "Factory reset initiated"
}
```

### RTSP Streaming

#### RTSP URLs

**Main Stream (4K):**
```
rtsp://admin:password@192.168.1.10:554/stream1
```

**Sub Stream (720p):**
```
rtsp://admin:password@192.168.1.10:554/stream2
```

**Note**: See [RTSP_ISSUE.md](RTSP_ISSUE.md) for critical information about broken RTSP implementation.

### Snapshot

#### Get Current Snapshot

```
GET /api/v1/snapshot?channel=0
```

**Authentication**: Required

**Parameters:**
- `channel`: Video channel (0 for main, 1 for sub)

**Response**: JPEG image data

### User Management

#### Get User List

```
GET /api/v1/user/list
```

**Authentication**: Required (admin only)

**Response:**
```json
{
  "result": 0,
  "data": {
    "users": [
      {
        "username": "admin",
        "level": "administrator"
      },
      {
        "username": "user1",
        "level": "operator"
      }
    ]
  }
}
```

#### Add User

```
POST /api/v1/user/add
Content-Type: application/json
```

**Authentication**: Required (admin only)

**Request Body:**
```json
{
  "username": "newuser",
  "password": "password123",
  "level": "operator"
}
```

#### Delete User

```
POST /api/v1/user/delete
Content-Type: application/json
```

**Authentication**: Required (admin only)

**Request Body:**
```json
{
  "username": "user1"
}
```

### OSD (On-Screen Display)

#### Get OSD Settings

```
GET /api/v1/osd/settings
```

**Authentication**: Required

**Response:**
```json
{
  "result": 0,
  "data": {
    "time_enabled": 1,
    "time_position": "top_left",
    "time_format": "YYYY-MM-DD HH:mm:ss",
    "camera_name": "Camera 1",
    "camera_name_enabled": 1,
    "camera_name_position": "bottom_left"
  }
}
```

#### Set OSD Settings

```
POST /api/v1/osd/settings
Content-Type: application/json
```

**Authentication**: Required

**Request Body:**
```json
{
  "time_enabled": 1,
  "time_position": "top_left",
  "time_format": "YYYY-MM-DD HH:mm:ss",
  "camera_name": "Camera 1",
  "camera_name_enabled": 1,
  "camera_name_position": "bottom_left"
}
```

### Audio Settings

#### Get Audio Settings

```
GET /api/v1/audio/settings
```

**Authentication**: Required

**Response:**
```json
{
  "result": 0,
  "data": {
    "enabled": 1,
    "codec": "AAC",
    "sample_rate": 16000,
    "bitrate": 128,
    "volume": 80
  }
}
```

#### Set Audio Settings

```
POST /api/v1/audio/settings
Content-Type: application/json
```

**Authentication**: Required

**Request Body:**
```json
{
  "enabled": 1,
  "codec": "AAC",
  "sample_rate": 16000,
  "bitrate": 128,
  "volume": 80
}
```

### Response Codes

- `0`: Success
- `1`: Invalid parameters
- `2`: Authentication failed
- `3`: Insufficient permissions
- `4`: Resource not found
- `5`: Internal error
- `6`: Device busy

### Common Headers

All requests should include:
```
User-Agent: Camera-API-Client/1.0
Accept: application/json
```

For POST requests:
```
Content-Type: application/json
```

### Rate Limiting

The API implements rate limiting:
- Maximum 10 requests per second per IP
- Maximum 100 requests per minute per IP

Exceeding these limits will result in HTTP 429 (Too Many Requests) responses.

### WebSocket Events

The camera supports WebSocket connections for real-time events:

```
ws://192.168.1.10:8080/events
```

**Event Types:**
- `motion_detected`: Motion detection triggered
- `audio_detected`: Audio detection triggered
- `connection_lost`: Network connection lost
- `storage_full`: Storage device full
- `alarm_triggered`: External alarm triggered

**Example Event:**
```json
{
  "event": "motion_detected",
  "timestamp": "2023-01-01T12:00:00Z",
  "channel": 0,
  "data": {
    "region": 1,
    "confidence": 95
  }
}
```
