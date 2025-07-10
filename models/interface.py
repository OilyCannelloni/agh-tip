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

    @staticmethod
    def default_yang(name):
        config = {
            "Cisco-IOS-XE-native:definition": {
                "name" : name
            }
        }
        return config

    def to_yang(self):
        config = {
            "Cisco-IOS-XE-native:definition": {
                "name": self.name,
                "rd": self.rd,
                "address-family": {
                    "ipv4": {}
                }
            }
        }
        #
        if self.import_rt or self.export_rt:
            route_target = {}
            if self.export_rt:
                route_target["export"] = {
                    "asn-ip": self.export_rt
                }
            if self.import_rt:
                route_target["import"] = {
                    "asn-ip": self.import_rt
                }

            config["Cisco-IOS-XE-native:definition"]["route-target"] = route_target

        return config


@dataclasses.dataclass
class InterfaceConfig:
    """Interface Configuration"""
    name: str
    type: InterfaceType = InterfaceType.ETHERNET
    ip_addr: Optional[str] = None
    ip_mask: Optional[str] = None
    enabled: bool = True
    description: str = ""
    vrf: Optional[str] = None  # VRF assignment for route leaking

    def to_yang(self):
        interface_config = {
            "ietf-interfaces:interface": {
                "name": self.name,
                "description": self.description,
                "type": self.type.value,
                "enabled": self.enabled
            }
        }

        # Add IP configuration if provided
        if self.ip_addr and self.ip_mask:
            interface_config["ietf-interfaces:interface"]["ietf-ip:ipv4"] = {
                "address": [
                    {
                        "ip": self.ip_addr,
                        "netmask": self.ip_mask
                    }
                ]
            }

        # Add VRF assignment if specified
        if self.vrf:
            interface_config["ietf-interfaces:interface"]["Cisco-IOS-XE-native:vrf"] = {
                "forwarding": self.vrf
            }

        return interface_config