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
DEFAULT_AUTH = ("agh", "xd")


class RequestType(enum.Enum):
    INTERFACE = "interface"
    VRF = "vrf"
    VRF_PATCH = "vrf patch"
    BGP = "bgp"
    BGP_PATCH = "bgp patch"
    ROUTE_MAP = "route_map"
    OSPF = "ospf"


class RestConfHandler:
    """
    RESTCONF API Handler for Cisco IOS-XE devices

    This class provides programmatic access to network device configuration
    for educational purposes, specifically focusing on route leaking in MP-BGP.
    """

    def __init__(self, ip_addr: str, username: str = "agh", password: str = "xd"):
        """
        Initialize RESTCONF handler

        Args:
            ip_addr: IP address of the network device
            username: Authentication username
            password: Authentication password
        """
        self.ip_addr = ip_addr
        self.auth = (username, password)
        self.base_url = f"https://{ip_addr}:443/restconf/data"

    def _build_url(self, rq_type: RequestType, **kwargs) -> str:
        """Build appropriate URL based on request type"""
        match rq_type:
            case RequestType.INTERFACE:
                # interface = kwargs.get('interface', '')
                # interface = interface.replace("/", "%2F")
                return f"{self.base_url}/Cisco-IOS-XE-native:native/interface/GigabitEthernet"
            case RequestType.VRF:
                return f"{self.base_url}/Cisco-IOS-XE-native:native/vrf"
            case RequestType.VRF_PATCH:
                return f"{self.base_url}/Cisco-IOS-XE-native:native/vrf/definition={kwargs['vrf']}"
            case RequestType.BGP:
                return f"{self.base_url}/Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-bgp:bgp"
            case RequestType.ROUTE_MAP:
                return f"{self.base_url}/Cisco-IOS-XE-native:native/route-map"
            case RequestType.OSPF:
                return f"{self.base_url}/Cisco-IOS-XE-native:native/router/Cisco-IOS-XE-ospf:router-ospf"

    def _make_request(self, method: str, url: str, data: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with proper error handling"""
        print("url:", url)
        print(data)
        print(method)

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
        response = self._make_request("PATCH", url, interface_config.to_yang2())
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

    def get_vrf(self, vrf_name: str) -> Dict[str, Any]:
        """Get specific VRF configuration"""
        url = self._build_url(RequestType.VRF_PATCH, vrf=vrf_name)
        response = self._make_request("GET", url)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.status_code == 200 else None
        }

    def patch_vrf(self, vrf_config, name) -> Dict[str, Any]:
        """Create VRF configuration"""
        url = self._build_url(RequestType.VRF_PATCH, vrf=name)
        response = self._make_request("PATCH", url, vrf_config.to_yang())
        return {
            "status_code": response.status_code,
            "data": response.json() if response.text else None
        }

    def create_vrf_from_yang(self, vrf_config) -> Dict[str, Any]:
        """Create VRF configuration"""
        url = self._build_url(RequestType.VRF)
        response = self._make_request("POST", url, vrf_config)
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

    def create_bgp(self, as_number: int, vrf_name: str, rd: str, import_rt: str,
                   export_rt: str) -> Dict[str, Any]:
        """Create BGP configuration"""
        print(vrf_name)
        bgp_config = {
            "Cisco-IOS-XE-bgp:bgp": [
                {
                    "id": 65500,
                    "bgp": {
                        "log-neighbor-changes": False,
                        "router-id": {
                            "ip-id": "1.1.1.1"
                        }
                    },
                    "address-family": {
                        "with-vrf": {
                            "ipv4": [
                                {
                                    "af-name": "unicast",
                                    "vrf": [
                                        {
                                            "name": "CUSTOMER_A",
                                            "ipv4-unicast": {
                                                "redistribute-vrf": {
                                                    "connected": {},
                                                    "ospf": [
                                                        {
                                                            "id": 101
                                                        }
                                                    ]
                                                }
                                            }
                                        },
                                        {
                                            "name": "CUSTOMER_B",
                                            "ipv4-unicast": {
                                                "redistribute-vrf": {
                                                    "connected": {},
                                                    "ospf": [
                                                        {
                                                            "id": 102
                                                        }
                                                    ]
                                                }
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                }
            ]
        }
        url = self._build_url(RequestType.BGP)
        response = self._make_request("PATCH", url, bgp_config)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.text else None
        }


    def create_ospfs(self):
        ospf_config = {
            "Cisco-IOS-XE-ospf:router-ospf": {
                "ospf": {
                    "process-id-vrf": [
                        {
                            "id": 101,
                            "vrf": "CUSTOMER_A",
                            "network": [
                                {
                                    "ip": "11.0.0.0",
                                    "wildcard": "0.255.255.255",
                                    "area": 11
                                }
                            ],
                            "capability": {
                                "vrf-lite": True
                            }
                        },
                        {
                            "id": 102,
                            "vrf": "CUSTOMER_B",
                            "network": [
                                {
                                    "ip": "12.0.0.0",
                                    "wildcard": "0.255.255.255",
                                    "area": 12
                                }
                            ],
                            "capability": {
                                "vrf-lite": True
                            }
                        }
                    ]
                }
            }
        }

        url = self._build_url(RequestType.OSPF)
        response = self._make_request("PATCH", url, ospf_config)
        return {
            "status_code": response.status_code,
            "data": response.json() if response.text else None
        }
