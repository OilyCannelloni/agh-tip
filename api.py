import enum
import json
import requests

from models.interface import InterfaceConfig

requests.packages.urllib3.disable_warnings()

HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-type":"application/yang-data+json"
}

AUTH = ("cisco", "cisco123!")


class RqType(enum.Enum):
    INTERFACE = 0


class RestConfHandler:
    def __init__(self, ip_addr):
        self.ip_addr = ip_addr

    def get_url(self, rq_type: RqType, **kwargs):
        match rq_type:
            case RqType.INTERFACE:
                return f"https://{self.ip_addr}/restconf/data/ietf-interfaces:interfaces/interface={kwargs['interface']}"

    """
    Interfaces
    """
    def update_interface(self, if_config: InterfaceConfig):
        url = self.get_url(RqType.INTERFACE)
        response = requests.put(url, json.dumps(if_config.to_yang()), auth=AUTH, headers=HEADERS, verify=False)
        print(response.status_code, response.json())

    def get_interface(self, interface: str):
        url = self.get_url(RqType.INTERFACE)
        response = requests.get(url, auth=AUTH, headers=HEADERS, verify=False)
        print(response.status_code, response.json())

    def delete_interface(self, interface: str):
        url = self.get_url(RqType.INTERFACE)
        response = requests.delete(url, auth=AUTH, headers=HEADERS, verify=False)
        print(response.status_code, response.json())
