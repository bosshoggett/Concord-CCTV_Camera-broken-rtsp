#!/usr/bin/env python3
"""
Concord Camera Configuration Tool

A Python client library and CLI tool for configuring Concord CNC81BA-V4 / 
Guangzhou Juan Optical 4K POE cameras.

Author: Community Contribution
License: MIT
"""

import argparse
import json
import sys
from typing import Optional, Dict, Any
from urllib.parse import urljoin
import requests
from requests.auth import HTTPDigestAuth


class ConcordCamera:
    """Client for interacting with Concord camera API."""
    
    def __init__(self, host: str, username: str = "admin", password: str = "", 
                 port: int = 80, timeout: int = 10):
        """
        Initialize camera client.
        
        Args:
            host: Camera IP address or hostname
            username: Authentication username (default: admin)
            password: Authentication password (default: empty)
            port: HTTP port (default: 80)
            timeout: Request timeout in seconds (default: 10)
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.base_url = f"http://{host}:{port}"
        self.session = requests.Session()
        self.session.auth = HTTPDigestAuth(username, password)
        
    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to camera API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments to pass to requests
            
        Returns:
            API response as dictionary
            
        Raises:
            requests.exceptions.RequestException: On network errors
            ValueError: On invalid response
        """
        url = urljoin(self.base_url, endpoint)
        kwargs.setdefault('timeout', self.timeout)
        kwargs.setdefault('headers', {}).update({
            'User-Agent': 'Camera-API-Client/1.0',
            'Accept': 'application/json'
        })
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Handle binary responses (like snapshots)
            if 'image' in response.headers.get('Content-Type', ''):
                return {'data': response.content, 'type': 'binary'}
                
            return response.json()
        except requests.exceptions.JSONDecodeError:
            return {'result': 0, 'raw': response.text}
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Request failed: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information including model and firmware version."""
        return self._request('GET', '/api/v1/system/info')
    
    def get_network_settings(self) -> Dict[str, Any]:
        """Get network configuration settings."""
        return self._request('GET', '/api/v1/system/network')
    
    def set_network_settings(self, dhcp: int = None, ip: str = None, 
                           netmask: str = None, gateway: str = None,
                           dns1: str = None, dns2: str = None) -> Dict[str, Any]:
        """
        Set network configuration.
        
        Args:
            dhcp: Enable DHCP (0 or 1)
            ip: Static IP address
            netmask: Network mask
            gateway: Gateway IP
            dns1: Primary DNS server
            dns2: Secondary DNS server
            
        Returns:
            API response
        """
        data = {}
        if dhcp is not None:
            data['dhcp'] = dhcp
        if ip:
            data['ip'] = ip
        if netmask:
            data['netmask'] = netmask
        if gateway:
            data['gateway'] = gateway
        if dns1:
            data['dns1'] = dns1
        if dns2:
            data['dns2'] = dns2
            
        return self._request('POST', '/api/v1/system/network', json=data)
    
    def get_video_stream_settings(self, channel: int = 0) -> Dict[str, Any]:
        """
        Get video stream settings.
        
        Args:
            channel: Video channel (0=main, 1=sub)
            
        Returns:
            Stream configuration
        """
        return self._request('GET', f'/api/v1/video/stream?channel={channel}')
    
    def set_video_stream_settings(self, channel: int = 0, codec: str = None,
                                 resolution: str = None, fps: int = None,
                                 bitrate: int = None, bitrate_control: str = None,
                                 quality: str = None, gop: int = None) -> Dict[str, Any]:
        """
        Set video stream settings.
        
        Args:
            channel: Video channel (0=main, 1=sub)
            codec: Video codec (H264, H265)
            resolution: Video resolution (e.g., "3840x2160")
            fps: Frames per second
            bitrate: Bitrate in kbps
            bitrate_control: Bitrate control mode (CBR, VBR)
            quality: Quality preset (low, medium, high)
            gop: Group of pictures size
            
        Returns:
            API response
        """
        data = {'channel': channel}
        if codec:
            data['codec'] = codec
        if resolution:
            data['resolution'] = resolution
        if fps is not None:
            data['fps'] = fps
        if bitrate is not None:
            data['bitrate'] = bitrate
        if bitrate_control:
            data['bitrate_control'] = bitrate_control
        if quality:
            data['quality'] = quality
        if gop is not None:
            data['gop'] = gop
            
        return self._request('POST', '/api/v1/video/stream', json=data)
    
    def get_image_settings(self) -> Dict[str, Any]:
        """Get image settings (brightness, contrast, etc.)."""
        return self._request('GET', '/api/v1/image/settings')
    
    def set_image_settings(self, brightness: int = None, contrast: int = None,
                          saturation: int = None, hue: int = None,
                          sharpness: int = None, flip: int = None,
                          mirror: int = None, wdr: int = None,
                          exposure_mode: str = None) -> Dict[str, Any]:
        """
        Set image settings.
        
        Args:
            brightness: Brightness (0-100)
            contrast: Contrast (0-100)
            saturation: Saturation (0-100)
            hue: Hue (0-100)
            sharpness: Sharpness (0-100)
            flip: Flip image (0 or 1)
            mirror: Mirror image (0 or 1)
            wdr: Wide Dynamic Range (0 or 1)
            exposure_mode: Exposure mode (auto, manual)
            
        Returns:
            API response
        """
        data = {}
        if brightness is not None:
            data['brightness'] = brightness
        if contrast is not None:
            data['contrast'] = contrast
        if saturation is not None:
            data['saturation'] = saturation
        if hue is not None:
            data['hue'] = hue
        if sharpness is not None:
            data['sharpness'] = sharpness
        if flip is not None:
            data['flip'] = flip
        if mirror is not None:
            data['mirror'] = mirror
        if wdr is not None:
            data['wdr'] = wdr
        if exposure_mode:
            data['exposure_mode'] = exposure_mode
            
        return self._request('POST', '/api/v1/image/settings', json=data)
    
    def get_motion_detection(self) -> Dict[str, Any]:
        """Get motion detection settings."""
        return self._request('GET', '/api/v1/motion/detection')
    
    def set_motion_detection(self, enabled: int = None, sensitivity: int = None,
                           regions: list = None) -> Dict[str, Any]:
        """
        Set motion detection settings.
        
        Args:
            enabled: Enable motion detection (0 or 1)
            sensitivity: Sensitivity level (0-100)
            regions: List of detection regions
            
        Returns:
            API response
        """
        data = {}
        if enabled is not None:
            data['enabled'] = enabled
        if sensitivity is not None:
            data['sensitivity'] = sensitivity
        if regions is not None:
            data['regions'] = regions
            
        return self._request('POST', '/api/v1/motion/detection', json=data)
    
    def get_osd_settings(self) -> Dict[str, Any]:
        """Get OSD (On-Screen Display) settings."""
        return self._request('GET', '/api/v1/osd/settings')
    
    def set_osd_settings(self, time_enabled: int = None, time_position: str = None,
                        time_format: str = None, camera_name: str = None,
                        camera_name_enabled: int = None, 
                        camera_name_position: str = None) -> Dict[str, Any]:
        """
        Set OSD settings.
        
        Args:
            time_enabled: Show time (0 or 1)
            time_position: Time position (top_left, top_right, bottom_left, bottom_right)
            time_format: Time format string
            camera_name: Camera name text
            camera_name_enabled: Show camera name (0 or 1)
            camera_name_position: Camera name position
            
        Returns:
            API response
        """
        data = {}
        if time_enabled is not None:
            data['time_enabled'] = time_enabled
        if time_position:
            data['time_position'] = time_position
        if time_format:
            data['time_format'] = time_format
        if camera_name:
            data['camera_name'] = camera_name
        if camera_name_enabled is not None:
            data['camera_name_enabled'] = camera_name_enabled
        if camera_name_position:
            data['camera_name_position'] = camera_name_position
            
        return self._request('POST', '/api/v1/osd/settings', json=data)
    
    def get_snapshot(self, channel: int = 0, filename: str = None) -> bytes:
        """
        Capture snapshot from camera.
        
        Args:
            channel: Video channel (0=main, 1=sub)
            filename: Optional filename to save snapshot
            
        Returns:
            JPEG image data
        """
        result = self._request('GET', f'/api/v1/snapshot?channel={channel}')
        
        if result.get('type') == 'binary':
            image_data = result['data']
            if filename:
                with open(filename, 'wb') as f:
                    f.write(image_data)
            return image_data
        
        raise ValueError("Failed to capture snapshot")
    
    def reboot(self) -> Dict[str, Any]:
        """Reboot the camera."""
        return self._request('POST', '/api/v1/system/reboot')
    
    def factory_reset(self) -> Dict[str, Any]:
        """Perform factory reset (WARNING: This will erase all settings!)."""
        return self._request('POST', '/api/v1/system/reset')
    
    def get_rtsp_url(self, channel: int = 1, with_auth: bool = True) -> str:
        """
        Get RTSP stream URL.
        
        Args:
            channel: Stream channel (1=main 4K, 2=sub 720p)
            with_auth: Include authentication in URL
            
        Returns:
            RTSP URL string
            
        Note:
            The RTSP stream has known issues with missing SPS/PPS headers.
            See RTSP_ISSUE.md for details and workarounds.
        """
        if with_auth:
            auth = f"{self.username}:{self.password}@" if self.password else f"{self.username}@"
        else:
            auth = ""
        
        return f"rtsp://{auth}{self.host}:554/stream{channel}"


def main():
    """Command-line interface for camera configuration."""
    parser = argparse.ArgumentParser(
        description='Concord Camera Configuration Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Get system information
  %(prog)s -i 192.168.1.10 info
  
  # Get network settings
  %(prog)s -i 192.168.1.10 network
  
  # Set static IP
  %(prog)s -i 192.168.1.10 set-network --ip 192.168.1.100 --dhcp 0
  
  # Get video stream settings
  %(prog)s -i 192.168.1.10 video
  
  # Set video quality
  %(prog)s -i 192.168.1.10 set-video --bitrate 4096 --fps 25
  
  # Capture snapshot
  %(prog)s -i 192.168.1.10 snapshot -o snapshot.jpg
  
  # Get RTSP URL
  %(prog)s -i 192.168.1.10 rtsp-url

Note: Default credentials are admin with empty password.
        """
    )
    
    parser.add_argument('-i', '--ip', required=True, help='Camera IP address')
    parser.add_argument('-u', '--username', default='admin', help='Username (default: admin)')
    parser.add_argument('-p', '--password', default='', help='Password (default: empty)')
    parser.add_argument('--port', type=int, default=80, help='HTTP port (default: 80)')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout (default: 10s)')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Info command
    subparsers.add_parser('info', help='Get system information')
    
    # Network commands
    subparsers.add_parser('network', help='Get network settings')
    
    network_set = subparsers.add_parser('set-network', help='Set network settings')
    network_set.add_argument('--dhcp', type=int, choices=[0, 1], help='Enable DHCP (0 or 1)')
    network_set.add_argument('--ip', help='Static IP address')
    network_set.add_argument('--netmask', help='Network mask')
    network_set.add_argument('--gateway', help='Gateway IP')
    network_set.add_argument('--dns1', help='Primary DNS')
    network_set.add_argument('--dns2', help='Secondary DNS')
    
    # Video commands
    video_get = subparsers.add_parser('video', help='Get video stream settings')
    video_get.add_argument('--channel', type=int, default=0, help='Channel (0=main, 1=sub)')
    
    video_set = subparsers.add_parser('set-video', help='Set video stream settings')
    video_set.add_argument('--channel', type=int, default=0, help='Channel (0=main, 1=sub)')
    video_set.add_argument('--codec', choices=['H264', 'H265'], help='Video codec')
    video_set.add_argument('--resolution', help='Resolution (e.g., 3840x2160)')
    video_set.add_argument('--fps', type=int, help='Frames per second')
    video_set.add_argument('--bitrate', type=int, help='Bitrate in kbps')
    video_set.add_argument('--quality', choices=['low', 'medium', 'high'], help='Quality preset')
    
    # Image commands
    subparsers.add_parser('image', help='Get image settings')
    
    image_set = subparsers.add_parser('set-image', help='Set image settings')
    image_set.add_argument('--brightness', type=int, help='Brightness (0-100)')
    image_set.add_argument('--contrast', type=int, help='Contrast (0-100)')
    image_set.add_argument('--saturation', type=int, help='Saturation (0-100)')
    image_set.add_argument('--sharpness', type=int, help='Sharpness (0-100)')
    image_set.add_argument('--wdr', type=int, choices=[0, 1], help='WDR (0 or 1)')
    
    # Motion detection commands
    subparsers.add_parser('motion', help='Get motion detection settings')
    
    motion_set = subparsers.add_parser('set-motion', help='Set motion detection')
    motion_set.add_argument('--enabled', type=int, choices=[0, 1], help='Enable (0 or 1)')
    motion_set.add_argument('--sensitivity', type=int, help='Sensitivity (0-100)')
    
    # OSD commands
    subparsers.add_parser('osd', help='Get OSD settings')
    
    osd_set = subparsers.add_parser('set-osd', help='Set OSD settings')
    osd_set.add_argument('--camera-name', help='Camera name text')
    osd_set.add_argument('--show-time', type=int, choices=[0, 1], help='Show time (0 or 1)')
    osd_set.add_argument('--show-name', type=int, choices=[0, 1], help='Show name (0 or 1)')
    
    # Snapshot command
    snapshot = subparsers.add_parser('snapshot', help='Capture snapshot')
    snapshot.add_argument('--channel', type=int, default=0, help='Channel (0=main, 1=sub)')
    snapshot.add_argument('-o', '--output', default='snapshot.jpg', help='Output filename')
    
    # RTSP URL command
    rtsp = subparsers.add_parser('rtsp-url', help='Get RTSP stream URL')
    rtsp.add_argument('--channel', type=int, default=1, help='Channel (1=main, 2=sub)')
    rtsp.add_argument('--no-auth', action='store_true', help='Exclude credentials from URL')
    
    # System commands
    subparsers.add_parser('reboot', help='Reboot camera')
    subparsers.add_parser('reset', help='Factory reset (WARNING: erases all settings!)')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Create camera client
    camera = ConcordCamera(args.ip, args.username, args.password, args.port, args.timeout)
    
    try:
        # Execute command
        if args.command == 'info':
            result = camera.get_system_info()
            print(json.dumps(result, indent=2))
            
        elif args.command == 'network':
            result = camera.get_network_settings()
            print(json.dumps(result, indent=2))
            
        elif args.command == 'set-network':
            result = camera.set_network_settings(
                dhcp=args.dhcp,
                ip=args.ip,
                netmask=args.netmask,
                gateway=args.gateway,
                dns1=args.dns1,
                dns2=args.dns2
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == 'video':
            result = camera.get_video_stream_settings(args.channel)
            print(json.dumps(result, indent=2))
            
        elif args.command == 'set-video':
            result = camera.set_video_stream_settings(
                channel=args.channel,
                codec=args.codec,
                resolution=args.resolution,
                fps=args.fps,
                bitrate=args.bitrate,
                quality=args.quality
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == 'image':
            result = camera.get_image_settings()
            print(json.dumps(result, indent=2))
            
        elif args.command == 'set-image':
            result = camera.set_image_settings(
                brightness=args.brightness,
                contrast=args.contrast,
                saturation=args.saturation,
                sharpness=args.sharpness,
                wdr=args.wdr
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == 'motion':
            result = camera.get_motion_detection()
            print(json.dumps(result, indent=2))
            
        elif args.command == 'set-motion':
            result = camera.set_motion_detection(
                enabled=args.enabled,
                sensitivity=args.sensitivity
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == 'osd':
            result = camera.get_osd_settings()
            print(json.dumps(result, indent=2))
            
        elif args.command == 'set-osd':
            result = camera.set_osd_settings(
                camera_name=args.camera_name,
                time_enabled=args.show_time,
                camera_name_enabled=args.show_name
            )
            print(json.dumps(result, indent=2))
            
        elif args.command == 'snapshot':
            print(f"Capturing snapshot from channel {args.channel}...")
            camera.get_snapshot(args.channel, args.output)
            print(f"Snapshot saved to {args.output}")
            
        elif args.command == 'rtsp-url':
            url = camera.get_rtsp_url(args.channel, not args.no_auth)
            print(url)
            print("\nWARNING: This camera has broken RTSP implementation!")
            print("The stream is missing SPS/PPS headers. See RTSP_ISSUE.md for details.")
            
        elif args.command == 'reboot':
            confirm = input("Are you sure you want to reboot the camera? (yes/no): ")
            if confirm.lower() == 'yes':
                result = camera.reboot()
                print(json.dumps(result, indent=2))
            else:
                print("Reboot cancelled")
                
        elif args.command == 'reset':
            print("WARNING: This will erase ALL camera settings and return to factory defaults!")
            confirm = input("Type 'FACTORY RESET' to confirm: ")
            if confirm == 'FACTORY RESET':
                result = camera.factory_reset()
                print(json.dumps(result, indent=2))
            else:
                print("Factory reset cancelled")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
