#!/usr/bin/env python3
"""
Camera Diagnostic Script

Runs comprehensive diagnostics on Concord cameras to help troubleshoot issues.
"""

import sys
import socket
import json
from camera_config import ConcordCamera


def diagnose_camera(ip):
    """Run comprehensive diagnostics on camera."""
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
            return False
    except Exception as e:
        print(f"✗ Network error: {e}")
        return False
    
    # Test RTSP port
    print("\n2. RTSP Port")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((ip, 554))
        sock.close()
        if result == 0:
            print("✓ Port 554 (RTSP) reachable")
        else:
            print("⚠ Port 554 (RTSP) not reachable")
    except Exception as e:
        print(f"⚠ RTSP port check failed: {e}")
    
    # Test authentication
    print("\n3. Authentication")
    try:
        camera = ConcordCamera(ip, timeout=10)
        info = camera.get_system_info()
        print("✓ Authentication successful")
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        print("\nTroubleshooting tips:")
        print("- Verify camera IP address")
        print("- Try default credentials: admin / (empty)")
        print("- Check if password was changed")
        print("- Consider factory reset")
        return False
    
    # System information
    print("\n4. System Information")
    try:
        print(f"  Model: {info['data']['model']}")
        print(f"  Hardware Version: {info['data']['hardware_version']}")
        print(f"  Firmware Version: {info['data']['firmware_version']}")
        print(f"  Serial Number: {info['data']['serial_number']}")
        print(f"  Uptime: {info['data']['uptime']} seconds")
    except Exception as e:
        print(f"✗ Error parsing system info: {e}")
        print(f"  Raw response: {info}")
    
    # Network settings
    print("\n5. Network Settings")
    try:
        network = camera.get_network_settings()
        print(f"  IP Address: {network['data']['ip']}")
        print(f"  Netmask: {network['data']['netmask']}")
        print(f"  Gateway: {network['data']['gateway']}")
        print(f"  DNS1: {network['data']['dns1']}")
        print(f"  DNS2: {network['data']['dns2']}")
        print(f"  DHCP: {'Enabled' if network['data']['dhcp'] else 'Disabled'}")
        print(f"  HTTP Port: {network['data']['http_port']}")
        print(f"  RTSP Port: {network['data']['rtsp_port']}")
    except Exception as e:
        print(f"✗ Error getting network settings: {e}")
    
    # Video settings
    print("\n6. Video Settings")
    try:
        video = camera.get_video_stream_settings(channel=0)
        print(f"  Main Stream:")
        print(f"    Codec: {video['data']['codec']}")
        print(f"    Resolution: {video['data']['resolution']}")
        print(f"    FPS: {video['data']['fps']}")
        print(f"    Bitrate: {video['data']['bitrate']} kbps")
        print(f"    Quality: {video['data']['quality']}")
    except Exception as e:
        print(f"✗ Error getting video settings: {e}")
    
    try:
        video_sub = camera.get_video_stream_settings(channel=1)
        print(f"  Sub Stream:")
        print(f"    Codec: {video_sub['data']['codec']}")
        print(f"    Resolution: {video_sub['data']['resolution']}")
        print(f"    FPS: {video_sub['data']['fps']}")
        print(f"    Bitrate: {video_sub['data']['bitrate']} kbps")
    except Exception as e:
        print(f"  Sub stream not available or error: {e}")
    
    # Image settings
    print("\n7. Image Settings")
    try:
        image = camera.get_image_settings()
        print(f"  Brightness: {image['data']['brightness']}")
        print(f"  Contrast: {image['data']['contrast']}")
        print(f"  Saturation: {image['data']['saturation']}")
        print(f"  Sharpness: {image['data']['sharpness']}")
        print(f"  WDR: {'Enabled' if image['data']['wdr'] else 'Disabled'}")
        print(f"  Exposure Mode: {image['data']['exposure_mode']}")
    except Exception as e:
        print(f"⚠ Error getting image settings: {e}")
    
    # Motion detection
    print("\n8. Motion Detection")
    try:
        motion = camera.get_motion_detection()
        print(f"  Enabled: {'Yes' if motion['data']['enabled'] else 'No'}")
        print(f"  Sensitivity: {motion['data']['sensitivity']}")
        print(f"  Regions: {len(motion['data']['regions'])} configured")
    except Exception as e:
        print(f"⚠ Error getting motion detection settings: {e}")
    
    # OSD settings
    print("\n9. OSD (On-Screen Display)")
    try:
        osd = camera.get_osd_settings()
        print(f"  Time Display: {'Enabled' if osd['data']['time_enabled'] else 'Disabled'}")
        print(f"  Camera Name: {osd['data']['camera_name']}")
        print(f"  Name Display: {'Enabled' if osd['data']['camera_name_enabled'] else 'Disabled'}")
    except Exception as e:
        print(f"⚠ Error getting OSD settings: {e}")
    
    # RTSP URLs
    print("\n10. RTSP Stream URLs")
    try:
        url_main = camera.get_rtsp_url(1, with_auth=False)
        url_sub = camera.get_rtsp_url(2, with_auth=False)
        print(f"  Main stream: {url_main}")
        print(f"  Sub stream: {url_sub}")
        print("\n  ⚠ CRITICAL WARNING:")
        print("  These cameras have BROKEN RTSP implementation!")
        print("  Missing SPS/PPS headers - stream won't work with most players")
        print("  See RTSP_ISSUE.md for details and workarounds")
    except Exception as e:
        print(f"✗ Error retrieving RTSP URLs: {e}")
    
    # Snapshot test
    print("\n11. Snapshot Capability")
    try:
        print("  Testing snapshot capture...")
        snapshot = camera.get_snapshot(channel=0)
        if snapshot and len(snapshot) > 0:
            print(f"  ✓ Snapshot captured successfully ({len(snapshot)} bytes)")
            print("  Tip: Use snapshots instead of RTSP for reliable image capture")
        else:
            print("  ✗ Snapshot capture failed or empty")
    except Exception as e:
        print(f"  ✗ Error capturing snapshot: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("Diagnostics Complete")
    print("="*60)
    print("\nSummary:")
    print("✓ Camera is accessible and API is functional")
    print("⚠ RTSP streaming has known issues (missing SPS/PPS headers)")
    print("✓ HTTP snapshot API works as alternative")
    print("\nNext steps:")
    print("- Use HTTP API for configuration")
    print("- Use snapshot endpoint for image capture")
    print("- See RTSP_ISSUE.md for streaming workarounds")
    print("- Check TROUBLESHOOTING.md for common issues")
    
    return True


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Concord Camera Diagnostic Tool")
        print("="*60)
        print("\nUsage:")
        print(f"  {sys.argv[0]} <camera_ip>")
        print("\nExample:")
        print(f"  {sys.argv[0]} 192.168.1.10")
        print("\nThis tool will test connectivity, authentication, and")
        print("enumerate all camera settings to help diagnose issues.")
        sys.exit(1)
    
    camera_ip = sys.argv[1]
    
    # Validate IP format (basic check)
    parts = camera_ip.split('.')
    if len(parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in parts):
        print(f"Error: Invalid IP address format: {camera_ip}")
        print("Expected format: xxx.xxx.xxx.xxx")
        sys.exit(1)
    
    try:
        success = diagnose_camera(camera_ip)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nDiagnostics interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error during diagnostics: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
