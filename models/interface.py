import dataclasses
import enum


class InterfaceType(enum.Enum):
    DEFAULT = "iana-if-type:ethernetCsmacd"
    LOOPBACK = "iana-if-type:softwareLoopback"


@dataclasses.dataclass
class InterfaceConfig:
    name: str
    type: InterfaceType
    ip_addr: str
    ip_mask: str
    enabled: bool = True
    description: str = ""

    def to_yang(self):
        return {
            "ietf-interfaces:interface": {
                "name": self.name,
                "description": self.description,
                "type": self.type.value,
                "enabled": self.enabled,
                "ietf-ip:ipv4": {
                    "address": [
                        {
                            "ip": self.ip_addr,
                            "netmask": self.ip_mask
                        }
                    ]
                },
                "ietf-ip:ipv6": {}
            }
        }