#!/usr/bin/env python3
"""
Juan Optical / Concord Camera Configuration Utility

This script provides CLI access to configure cameras using the
Guangzhou Juan Optical netsdk API (found in Concord, and various
AliExpress/Amazon rebranded cameras).

WARNING: These cameras have broken RTSP implementations.
This tool can configure settings but cannot fix the broken video stream.

Usage:
    python3 juan_camera_tool.py --ip 192.168.1.33 --info
    python3 juan_camera_tool.py --ip 192.168.1.33 --set-codec H.264
    python3 juan_camera_tool.py --ip 192.168.1.33 --snapshot output.jpg

Author: Community Reverse Engineering Project
License: CC0 1.0 Universal (Public Domain)
"""

import argparse
import requests
import json
import sys
from requests.auth import HTTPBasicAuth


class JuanCamera:
    """Interface for Juan Optical / Concord cameras with netsdk API."""
    
    def __init__(self, ip: str, username: str = "admin", password: str = ""):
        self.ip = ip
        self.base_url = f"http://{ip}"
        self.auth = HTTPBasicAuth(username, password)
        self.username = username
        self.password = password
    
    def _get(self, endpoint: str) -> dict | str | None:
        """GET request to camera API."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            
            #-- Try to parse as JSON, fall back to text
            try:
                return response.json()
            except json.JSONDecodeError:
                return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}", file=sys.stderr)
            return None
    
    def _put(self, endpoint: str, data: dict) -> dict | None:
        """PUT request to camera API."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.put(
                url,
                auth=self.auth,
                headers={"Content-Type": "application/json"},
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}", file=sys.stderr)
            return None
    
    def test_connection(self) -> bool:
        """Test if camera is reachable and credentials work."""
        url = f"{self.base_url}/user/user_list.xml?username={self.username}&password={self.password}"
        try:
            response = requests.get(url, timeout=10)
            return 'ret="success"' in response.text
        except requests.exceptions.RequestException:
            return False
    
    def get_oem_info(self) -> dict | None:
        """Get OEM manufacturer info (no auth required)."""
        return self._get("/netsdk/oem/deviceinfo")
    
    def get_device_info(self) -> dict | None:
        """Get full device information."""
        return self._get("/netsdk/system/deviceinfo")
    
    def get_video_encode(self, channel: int = 101) -> dict | None:
        """Get video encode settings for a channel."""
        return self._get(f"/netsdk/video/encode/channel/{channel}")
    
    def get_video_encode_properties(self, channel: int = 101) -> dict | None:
        """Get available video encode options for a channel."""
        return self._get(f"/netsdk/video/encode/channel/{channel}/properties")
    
    def set_video_encode(self, channel: int, **kwargs) -> dict | None:
        """
        Set video encode settings.
        
        Available kwargs:
            codecType: "H.264", "H.265", "H.264+", "H.265+"
            h264Profile: "baseline", "main", "high"
            resolution: "3840x2160", "1920x1080", "1280x720", etc.
            frameRate: 5-15 (depends on camera)
            constantBitRate: 128-5120
            bitRateControlType: "CBR", "VBR"
        """
        return self._put(f"/netsdk/video/encode/channel/{channel}", kwargs)
    
    def get_audio_encode(self, channel: int = 101) -> dict | None:
        """Get audio encode settings."""
        return self._get(f"/netsdk/audio/encode/channel/{channel}")
    
    def set_audio_enabled(self, channel: int, enabled: bool) -> dict | None:
        """Enable or disable audio."""
        return self._put(f"/netsdk/audio/encode/channel/{channel}", {"enabled": enabled})
    
    def get_rtmp_status(self) -> dict | None:
        """Get RTMP configuration (usually broken)."""
        return self._get("/netsdk/rtmp")
    
    def get_snapshot(self, output_path: str, channel: int = 1) -> bool:
        """
        Download a JPEG snapshot from the camera.
        This is the ONLY reliable way to get video from these cameras.
        """
        url = f"{self.base_url}/snapshot?chn={channel}"
        try:
            response = requests.get(url, auth=self.auth, timeout=10)
            response.raise_for_status()
            
            if response.headers.get("Content-Type", "").startswith("image/"):
                with open(output_path, "wb") as f:
                    f.write(response.content)
                return True
            else:
                print("Error: Response is not an image", file=sys.stderr)
                return False
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}", file=sys.stderr)
            return False
    
    def get_hi3510_venc(self) -> str | None:
        """Get video encoder attributes via hi3510 CGI."""
        return self._get("/cgi-bin/hi3510/param.cgi?cmd=getvencattr")


def print_json(data, indent: int = 2):
    """Pretty print JSON data."""
    if isinstance(data, dict):
        print(json.dumps(data, indent=indent))
    else:
        print(data)


def main():
    parser = argparse.ArgumentParser(
        description="Configure Juan Optical / Concord cameras via netsdk API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ip 192.168.1.33 --info
  %(prog)s --ip 192.168.1.33 --video-settings
  %(prog)s --ip 192.168.1.33 --video-options
  %(prog)s --ip 192.168.1.33 --set-codec H.264
  %(prog)s --ip 192.168.1.33 --set-resolution 1920x1080
  %(prog)s --ip 192.168.1.33 --snapshot /tmp/camera.jpg

WARNING: These cameras have broken RTSP. Use --snapshot for video.
        """
    )
    
    #-- Connection options
    parser.add_argument("--ip", required=True, help="Camera IP address")
    parser.add_argument("--user", default="admin", help="Username (default: admin)")
    parser.add_argument("--password", default="", help="Password (default: blank)")
    
    #-- Information commands
    parser.add_argument("--test", action="store_true", help="Test connection")
    parser.add_argument("--info", action="store_true", help="Get device info")
    parser.add_argument("--oem", action="store_true", help="Get OEM info")
    parser.add_argument("--video-settings", action="store_true", help="Get video encode settings")
    parser.add_argument("--video-options", action="store_true", help="Get available video options")
    parser.add_argument("--audio-settings", action="store_true", help="Get audio settings")
    parser.add_argument("--channel", type=int, default=101, help="Channel (101=main, 102=sub)")
    
    #-- Configuration commands
    parser.add_argument("--set-codec", choices=["H.264", "H.265", "H.264+", "H.265+"],
                        help="Set video codec")
    parser.add_argument("--set-profile", choices=["baseline", "main", "high"],
                        help="Set H.264 profile")
    parser.add_argument("--set-resolution", help="Set resolution (e.g., 1920x1080)")
    parser.add_argument("--set-framerate", type=int, help="Set frame rate (5-15)")
    parser.add_argument("--set-bitrate", type=int, help="Set bitrate (128-5120 kbps)")
    
    #-- Snapshot
    parser.add_argument("--snapshot", metavar="FILE", help="Save snapshot to file")
    
    args = parser.parse_args()
    
    #-- Create camera instance
    camera = JuanCamera(args.ip, args.user, args.password)
    
    #-- Test connection
    if args.test:
        if camera.test_connection():
            print(f"✓ Connected to {args.ip} successfully")
            sys.exit(0)
        else:
            print(f"✗ Failed to connect to {args.ip}")
            sys.exit(1)
    
    #-- OEM info (no auth required)
    if args.oem:
        data = camera.get_oem_info()
        if data:
            print_json(data)
        sys.exit(0 if data else 1)
    
    #-- Device info
    if args.info:
        data = camera.get_device_info()
        if data:
            print_json(data)
        sys.exit(0 if data else 1)
    
    #-- Video settings
    if args.video_settings:
        data = camera.get_video_encode(args.channel)
        if data:
            print_json(data)
        sys.exit(0 if data else 1)
    
    #-- Video options
    if args.video_options:
        data = camera.get_video_encode_properties(args.channel)
        if data:
            print_json(data)
        sys.exit(0 if data else 1)
    
    #-- Audio settings
    if args.audio_settings:
        data = camera.get_audio_encode(args.channel)
        if data:
            print_json(data)
        sys.exit(0 if data else 1)
    
    #-- Configuration changes
    settings_to_apply = {}
    
    if args.set_codec:
        settings_to_apply["codecType"] = args.set_codec
    
    if args.set_profile:
        settings_to_apply["h264Profile"] = args.set_profile
    
    if args.set_resolution:
        settings_to_apply["resolution"] = args.set_resolution
    
    if args.set_framerate:
        settings_to_apply["frameRate"] = args.set_framerate
    
    if args.set_bitrate:
        settings_to_apply["constantBitRate"] = args.set_bitrate
    
    if settings_to_apply:
        print(f"Applying settings to channel {args.channel}:")
        print_json(settings_to_apply)
        result = camera.set_video_encode(args.channel, **settings_to_apply)
        if result and result.get("statusCode") == 0:
            print("✓ Settings applied successfully")
            print("\nNOTE: RTSP is broken on these cameras. Settings change")
            print("will not fix video streaming. Use --snapshot for video.")
        else:
            print("✗ Failed to apply settings")
            if result:
                print_json(result)
            sys.exit(1)
    
    #-- Snapshot
    if args.snapshot:
        print(f"Downloading snapshot to {args.snapshot}...")
        if camera.get_snapshot(args.snapshot):
            print(f"✓ Snapshot saved to {args.snapshot}")
        else:
            print("✗ Failed to get snapshot")
            sys.exit(1)
    
    #-- No command specified
    if not any([args.test, args.oem, args.info, args.video_settings, 
                args.video_options, args.audio_settings, settings_to_apply, 
                args.snapshot]):
        parser.print_help()


if __name__ == "__main__":
    main()
