import dataclasses
import enum
from typing import Optional


class InterfaceType(enum.Enum):
    ETHERNET = "iana-if-type:ethernetCsmacd"
    LOOPBACK = "iana-if-type:softwareLoopback"
    SERIAL = "iana-if-type:ppp"


@dataclasses.dataclass
class VrfConfig:
    """VRF Configuration for route leaking"""
    name: str
    rd: str  # Route Distinguisher
    import_rt: Optional[str] = None  # Import Route Target
    export_rt: Optional[str] = None  # Export Route Target

    def to_yang(self):
        config = {
            "Cisco-IOS-XE-native:definition": {
                "name" : self.name
            }
        }

        # Add route targets if specified
        # if self.import_rt or self.export_rt:
        #     route_target = {}
        #     if self.import_rt:
        #         route_target["import"] = self.import_rt
        #     if self.export_rt:
        #         route_target["export"] = self.export_rt
        #     config["Cisco-IOS-XE-native:definition"][0]["address-family"]["ipv4"]["route-target"] = route_target

        return config


@dataclasses.dataclass
class InterfaceConfig:
    """Interface Configuration"""
    name: str
    type: InterfaceType
    ip_addr: Optional[str] = None
    ip_mask: Optional[str] = None
    enabled: bool = True
    description: str = ""
    vrf: Optional[str] = None  # VRF assignment for route leaking

    def to_yang(self):
        interface_config = {
            "ietf-interfaces:interface": {
                "name": self.name,
                "description": self.description
            }
        }

        # Add IP configuration if provided
        # if self.ip_addr and self.ip_mask:
        #     interface_config["ietf-interfaces:interface"]["ietf-ip:ipv4"] = {
        #         "address": [
        #             {
        #                 "ip": self.ip_addr,
        #                 "netmask": self.ip_mask
        #             }
        #         ]
        #     }
        #
        # # Add VRF assignment if specified
        # if self.vrf:
        #     interface_config["ietf-interfaces:interface"]["Cisco-IOS-XE-native:vrf"] = {
        #         "forwarding": self.vrf
        #     }

        return interface_config