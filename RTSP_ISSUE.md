# RTSP Implementation Issue: Missing SPS/PPS Headers

## Problem Overview

The Concord CNC81BA-V4 / Guangzhou Juan Optical 4K POE cameras have a **critical flaw** in their RTSP implementation: they do not include SPS (Sequence Parameter Set) and PPS (Picture Parameter Set) headers in the H.264/H.265 video stream.

### What are SPS/PPS Headers?

SPS and PPS are crucial NAL (Network Abstraction Layer) units in H.264/H.265 video streams that contain essential information about the video encoding:

- **SPS (Sequence Parameter Set)**: Contains global encoding parameters
  - Profile and level
  - Picture dimensions (width/height)
  - Frame rate
  - Reference frame information
  - Color space and chroma format

- **PPS (Picture Parameter Set)**: Contains per-picture encoding parameters
  - Entropy coding mode
  - Slice group information
  - Quantization parameters
  - Deblocking filter control

### Impact of Missing Headers

Without SPS/PPS headers, video decoders cannot properly initialize and decode the video stream. This results in:

1. **Playback Failures**: Most video players (VLC, FFmpeg, etc.) cannot play the stream
2. **Recording Issues**: NVR systems fail to record or produce corrupted files
3. **Transcoding Problems**: Cannot transcode or re-encode the stream
4. **Thumbnail Generation Failures**: Cannot extract keyframes for thumbnails

### Technical Details

#### Standard RTSP Implementation

In a properly implemented RTSP server, SPS/PPS are transmitted in multiple ways:

1. **In SDP (Session Description Protocol)**: During RTSP DESCRIBE
   ```
   a=fmtp:96 packetization-mode=1;profile-level-id=640028;sprop-parameter-sets=Z2QAKKzZQHgCJ+WEAAADAAIAAAMAZjxYtlg=,aO48gA==
   ```

2. **In RTP packets**: As part of the video stream (typically before IDR frames)

3. **Out-of-band**: Via dedicated RTSP methods

#### Broken Implementation in Concord Cameras

The Concord cameras:
- Do **NOT** include `sprop-parameter-sets` in the SDP
- Do **NOT** send SPS/PPS NAL units in the RTP stream
- Do **NOT** provide any mechanism to retrieve these headers

#### Example of Broken SDP

```
v=0
o=- 1234567890 1234567890 IN IP4 192.168.1.10
s=RTSP/RTP stream
t=0 0
a=tool:LIVE555 Streaming Media v2018.08.28
a=type:broadcast
a=control:*
a=range:npt=0-
m=video 0 RTP/AVP 96
c=IN IP4 0.0.0.0
b=AS:8192
a=rtpmap:96 H265/90000
a=control:track1
```

Note the **missing** `a=fmtp:96 ... sprop-parameter-sets=...` line!

#### Comparison with Correct SDP

```
v=0
o=- 1234567890 1234567890 IN IP4 192.168.1.10
s=RTSP/RTP stream
t=0 0
a=tool:LIVE555 Streaming Media v2018.08.28
a=type:broadcast
a=control:*
a=range:npt=0-
m=video 0 RTP/AVP 96
c=IN IP4 0.0.0.0
b=AS:8192
a=rtpmap:96 H265/90000
a=fmtp:96 sprop-vps=QAEMAf//AWAAAAMAkAAAAwAAAwB4FwJA;sprop-sps=QgEBAWAAAAMAkAAAAwAAAwB4oAKAgC0WNrkky/AIAAADAAgAAAMBlg==;sprop-pps=RAHA8vA8kA==
a=control:track1
```

## Workarounds and Solutions

### Solution 1: Extract Headers from HTTP Snapshot

The camera's HTTP snapshot endpoint (`/api/v1/snapshot`) generates JPEG images that are created from decoded H.265 frames. We can use this to infer the video parameters, but we still cannot extract the actual SPS/PPS headers.

**Limitations**: This doesn't give us the actual encoded headers needed for decoding.

### Solution 2: Use HTTP-FLV or HTTP-TS Instead

Some firmware versions may support alternative streaming protocols:

```bash
# Try HTTP-FLV
http://192.168.1.10/stream1.flv

# Try HTTP-TS (MPEG-TS over HTTP)
http://192.168.1.10/stream1.ts
```

**Note**: Not all firmware versions support these protocols.

### Solution 3: Capture and Extract from First I-Frame

If you can capture the raw RTP packets, you might be able to extract SPS/PPS from the first complete I-frame. This is complex and unreliable.

**Steps:**
1. Use Wireshark or tcpdump to capture RTSP/RTP traffic
2. Filter for RTP packets containing H.265 NAL units
3. Parse NAL units to find SPS (type 33) and PPS (type 34)
4. Extract and save these headers

**Example using tcpdump:**
```bash
tcpdump -i eth0 -s 65535 -w capture.pcap host 192.168.1.10 and port 554
```

### Solution 4: FFmpeg Workaround (Partial)

FFmpeg can sometimes work around missing headers by analyzing the stream:

```bash
# Try to play with error concealment
ffplay -rtsp_transport tcp -analyzeduration 10000000 -probesize 10000000 rtsp://admin:@192.168.1.10:554/stream1

# Try to record with errors ignored
ffmpeg -rtsp_transport tcp -i rtsp://admin:@192.168.1.10:554/stream1 \
       -c copy -bsf:v dump_extra -err_detect ignore_err \
       -fflags +genpts output.mp4
```

**Success Rate**: Low to moderate, depends on firmware version

### Solution 5: Use Manufacturer's SDK/Player

The manufacturer may provide:
- Windows/Linux SDK with proper decoder
- ActiveX control for Internet Explorer
- Proprietary player application

These tools have the SPS/PPS hardcoded or retrieve them through undocumented methods.

### Solution 6: Firmware Update (If Available)

Check with the manufacturer or vendor for firmware updates that fix this issue:

```bash
# Check current firmware version via API
curl -u admin: http://192.168.1.10/api/v1/system/info
```

**Known Working Firmware**: None confirmed yet

### Solution 7: Custom RTSP Proxy

Create a proxy that:
1. Connects to the camera's RTSP stream
2. Captures and analyzes the stream to extract/generate SPS/PPS
3. Injects proper headers into the SDP and RTP stream
4. Presents a fixed RTSP stream to clients

**Implementation complexity**: High

## Testing the Issue

### Using FFmpeg

```bash
# This will likely fail or show errors
ffmpeg -rtsp_transport tcp -i rtsp://admin:@192.168.1.10:554/stream1 -t 10 test.mp4

# Expected errors:
# [h265 @ 0x...] non-existing PPS 0 referenced
# [h265 @ 0x...] decode_slice_header error
# [h265 @ 0x...] no frame!
```

### Using VLC

```bash
vlc rtsp://admin:@192.168.1.10:554/stream1

# VLC will show:
# - Buffering forever, or
# - Green screen with errors in console, or
# - Crash
```

### Using GStreamer

```bash
gst-launch-1.0 rtspsrc location=rtsp://admin:@192.168.1.10:554/stream1 ! rtph265depay ! h265parse ! avdec_h265 ! autovideosink

# Expected errors:
# WARNING: caps negotiation failed
# ERROR: failed to go to PLAYING
```

### Using Python with OpenCV

```python
import cv2

cap = cv2.VideoCapture("rtsp://admin:@192.168.1.10:554/stream1")
ret, frame = cap.read()

if not ret:
    print("Failed to read frame - SPS/PPS headers missing!")
else:
    print("Success (unlikely with this camera)")
```

## Diagnostic Commands

### Check SDP for sprop-parameter-sets

```bash
# Send DESCRIBE request to check SDP
curl -v -X DESCRIBE \
     -H "Accept: application/sdp" \
     -u admin: \
     rtsp://192.168.1.10:554/stream1 2>&1 | grep -A 20 "application/sdp"
```

### Capture RTSP Traffic

```bash
# Capture all RTSP/RTP traffic
tcpdump -i any -s 0 -w rtsp_capture.pcap 'host 192.168.1.10 and (port 554 or portrange 16384-65535)'

# Analyze with Wireshark
wireshark rtsp_capture.pcap
# Filter: rtsp || rtp
# Look for DESCRIBE response and check SDP
# Examine RTP packets for NAL unit types
```

### Parse NAL Units

```bash
# Extract RTP payload and look for NAL unit types
# H.265 NAL unit types:
# 32 (VPS) - Video Parameter Set
# 33 (SPS) - Sequence Parameter Set  
# 34 (PPS) - Picture Parameter Set
# 19-20 (IDR) - Instantaneous Decoder Refresh frames

# Use h265_parser or similar tools to analyze
```

## Hardware Solutions

### Use Compatible Hardware

Some NVR systems and video management software have workarounds for broken cameras:

1. **Blue Iris** (Windows): Has compatibility modes
2. **Synology Surveillance Station**: May have device-specific profiles
3. **Hikvision NVRs**: Sometimes can handle non-standard streams
4. **Dahua NVRs**: May have compatibility modes

### ONVIF Compatibility

The camera may support ONVIF Profile S, which might provide alternative streaming:

```bash
# Test ONVIF device discovery
onvif-discovery

# Get ONVIF stream URIs
onvif-util -i 192.168.1.10 -u admin -p "" get-stream-uri
```

## Impact on Different Use Cases

### Home Assistant / HASS.io
```yaml
# This will likely NOT work
camera:
  - platform: generic
    stream_source: rtsp://admin:@192.168.1.10:554/stream1
```

### Zoneminder
May work with specific monitor settings and "Modect" mode disabled, but recording will likely be problematic.

### Frigate (with Google Coral)
Will fail to decode stream without SPS/PPS headers.

### MotionEye
May partially work with snapshot mode, but streaming will fail.

## Recommended Actions

1. **Contact Vendor**: Report this as a bug and request firmware fix
2. **Use HTTP Snapshots**: For static image capture, use the HTTP API
3. **Consider Replacement**: If real-time streaming is critical, consider different cameras
4. **SDK Integration**: If available, use manufacturer's SDK which may handle this internally
5. **Community Firmware**: Check for community-developed firmware (if available)

## Additional Resources

- [RFC 6184](https://tools.ietf.org/html/rfc6184) - RTP Payload Format for H.264
- [RFC 7798](https://tools.ietf.org/html/rfc7798) - RTP Payload Format for H.265
- [H.265/HEVC Specification](https://www.itu.int/rec/T-REC-H.265)
- [RTSP RFC 2326](https://tools.ietf.org/html/rfc2326)
- [RTSP 2.0 RFC 7826](https://tools.ietf.org/html/rfc7826)

## Contributing

If you find a working solution or workaround, please contribute to this documentation!
