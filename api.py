import enum
import json
import requests
from typing import Optional, Dict, Any
import urllib3

# Disable SSL warnings for lab environment
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Standard headers for RESTCONF
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

# Default authentication (change for your lab)
DEFAULT_AUTH = ("cisco", "cisco123!")


class RequestType(enum.Enum):
    INTERFACE = "interface"
    VRF = "vrf"
    BGP = "bgp"
    ROUTE_MAP = "route_map"


class RestConfHandler:
    """
    RESTCONF API Handler for Cisco IOS-XE devices

    This class provides programmatic access to network device configuration
    for educational purposes, specifically focusing on route leaking in MP-BGP.
    """

    def __init__(self, ip_addr: str, username: str = "cisco", password: str = "cisco123!"):
        """
        Initialize RESTCONF handler

        Args:
            ip_addr: IP address of the network device
            username: Authentication username
            password: Authentication password
        """
        self.ip_addr = ip_addr
        self.auth = (username, password)
        self.base_url = f"https://{ip_addr}/restconf/data"

    def _build_url(self, rq_type: RequestType, **kwargs) -> str:
        """Build appropriate URL based on request type"""
        match rq_type:
            case RequestType.INTERFACE:
                interface = kwargs.get('interface', '')
                return f"{self.base_url}/ietf-interfaces:interfaces/interface={interface}"
            case RequestType.VRF:
                return f"{self.base_url}/Cisco-IOS-XE-native:native/vrf/definition"
            case RequestType.BGP:
                return f"{self.base_url}/Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp"
            case RequestType.ROUTE_MAP:
                return f"{self.base_url}/Cisco-IOS-XE-native:native/route-map"

    def _make_request(self, method: str, url: str, data: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with proper error handling"""
        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                auth=self.auth,
                headers=HEADERS,
                verify=False,
                timeout=30
            )
            return response
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            raise

    def test_connection(self) -> bool:
        """Test if device is reachable and RESTCONF is enabled"""
        try:
            url = f"{self.base_url}/ietf-interfaces:interfaces"
            response = self._make_request("GET", url)
            return response.status_code == 200
        except:
            return False

    # Interface Management
    def get_interfaces(self) -> Dict[str, Any]:
        """Get all interfaces configuration"""
        url = self._build_url(RequestType.INTERFACE).rstrip("=")
        response = self._make_request("GET", url)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None
        }

    def get_interface(self, interface: str) -> Dict[str, Any]:
        """Get specific interface configuration"""
        url = self._build_url(RequestType.INTERFACE, interface=interface)
        response = self._make_request("GET", url)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None
        }

    def update_interface(self, interface_config) -> Dict[str, Any]:
        """Update interface configuration"""
        url = self._build_url(RequestType.INTERFACE, interface=interface_config.name)
        response = self._make_request("PUT", url, interface_config.to_yang())
        return {
            "status_code": response.status_code,
            "data": response.json() if response.text else None
        }

    # VRF Management
    def get_vrfs(self) -> Dict[str, Any]:
        """Get all VRF configurations"""
        url = self._build_url(RequestType.VRF)
        response = self._make_request("GET", url)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None
        }

    def create_vrf(self, vrf_config) -> Dict[str, Any]:
        """Create VRF configuration"""
        url = self._build_url(RequestType.VRF)
        response = self._make_request("PUT", url, vrf_config.to_yang())
        return {
            "status_code": response.status_code,
            "data": response.json() if response.text else None
        }

    def assign_vrf_to_interface(self, interface: str, vrf_name: str) -> Dict[str, Any]:
        """Assign VRF to interface for route leaking"""
        # This modifies the interface to include VRF assignment
        interface_data = {
            "ietf-interfaces:interface": {
                "name": interface,
                "Cisco-IOS-XE-native:vrf": {
                    "forwarding": vrf_name
                }
            }
        }
        url = self._build_url(RequestType.INTERFACE, interface=interface)
        response = self._make_request("PATCH", url, interface_data)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.text else None
        }

    # BGP Configuration for Route Leaking
    def get_bgp_config(self) -> Dict[str, Any]:
        """Get BGP configuration"""
        url = self._build_url(RequestType.BGP)
        response = self._make_request("GET", url)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None
        }

    def configure_bgp_address_family(self, as_number: int, vrf_name: str,
                                     rd: str, import_rt: str, export_rt: str) -> Dict[str, Any]:
        """Configure BGP address family for VRF (essential for route leaking)"""
        bgp_config = {
            "Cisco-IOS-XE-bgp:bgp": {
                "id": as_number,
                "address-family": {
                    "with-vrf": {
                        "ipv4": {
                            "af-name": "unicast",
                            "vrf": [
                                {
                                    "name": vrf_name,
                                    "ipv4-unicast": {
                                        "rd": rd,
                                        "route-target": {
                                            "export": export_rt,
                                            "import": import_rt
                                        }
                                    }
                                }
                            ]
                        }
                    }
                }
            }
        }
        url = self._build_url(RequestType.BGP)
        response = self._make_request("PUT", url, bgp_config)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.text else None
        }
