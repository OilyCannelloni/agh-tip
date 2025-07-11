from api import RestConfHandler
from models.interface import InterfaceConfig, InterfaceType, VrfConfig
from time import sleep


def educational_route_leaking_demo():
    """
    Educational demonstration of route leaking configuration using RESTCONF

    This function demonstrates the key concepts and steps for configuring
    route leaking between VRFs using programmatic interfaces.
    """

    # Step 1: Connect to device
    print("*****Step 1: Connecting to network device...")
    handler = RestConfHandler("10.0.0.1")  # Replace with your device IP
    if not handler.test_connection():
        print("Cannot connect to device. Check IP, credentials, and RESTCONF enablement.")
        return
    print("✅ Connected successfully!\n")
    sleep(2)

######################################################################
    # Step 2: Create VRFs for route leaking
    print("\n\n*****Step 2: Creating VRFs...")
    # VRF for customer A
    vrf_a = VrfConfig.default_yang(
        name="CUSTOMER_A"
    )
    # VRF for customer B
    vrf_b = VrfConfig.default_yang(
        name="CUSTOMER_B"
    )
    result_a = handler.create_vrf_from_yang(vrf_a)
    result_b = handler.create_vrf_from_yang(vrf_b)
    print(f"VRF CUSTOMER_A: {result_a['status_code']}")
    print(f"VRF CUSTOMER_B: {result_b['status_code']}\n")

    print("\n**Step 2.1: Configuring VRFS")
    vrf_a = VrfConfig(
        name="CUSTOMER_A",
        rd="65000:100",
        export_rt="65000:100",
        import_rt="65000:200"
    )
    vrf_a_result = handler.patch_vrf(vrf_a, vrf_a.name)
    print(f"VRF CUSTOMER_A: {vrf_a_result['status_code']}")

    vrf_b = VrfConfig(
        name="CUSTOMER_B",
        rd="65000:200",
        export_rt="65000:200",
        import_rt="65000:100"
    )
    vrf_b_result = handler.patch_vrf(vrf_b, vrf_b.name)
    print(f"VRF CUSTOMER_B: {vrf_b_result['status_code']}")
    sleep(4)

######################################################################
    # Step 3: Configure interfaces and assign to VRFs
    print("\n\n*****Step 3: Configuring interfaces...")

    # Interface for Customer A
    int_a = InterfaceConfig(
        name="GigabitEthernet0/0/1",
        description="Customer A Interface",
        ip_addr="11.0.0.1",
        ip_mask="255.255.255.0",
        vrf="CUSTOMER_A"
    )

    # Interface for Customer B
    int_b = InterfaceConfig(
        name="GigabitEthernet0/0/2",
        description="Customer B Interface",
        ip_addr="12.0.0.1",
        ip_mask="255.255.255.0",
        vrf="CUSTOMER_B"
    )
    result_int_a = handler.update_interface(int_a)
    print(f"Interface GigE0/0/1 (Customer A): {result_int_a['status_code']}")

    sleep(2)
    result_int_b = handler.update_interface(int_b)
    print(f"Interface GigE0/0/2 (Customer B): {result_int_b['status_code']}")
    sleep(3)

######################################################################
    # OSPF
    print("\n\n*****Step 4: Configuring OSPF")
    ospf_result = handler.create_ospfs()
    print(ospf_result['status_code'])
    sleep(2)

######################################################################
    # BGP
    print("\n\n*****Step 5: Configuring BGP address families...")
    bgp_result_a = handler.create_bgp(
        as_number=65000,
        vrf_name="CUSTOMER_A",
        rd="65000:100",
        import_rt="65000:200",
        export_rt="65000:100"
    )
    print(f"BGP Address Family: {bgp_result_a['status_code']}")

# Complete educational demonstration
def complete_educational_demo():
    """
    Run the complete educational demonstration
    """
    try:
        educational_route_leaking_demo()

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        print("Common issues:")
        print("- Device not reachable")
        print("- RESTCONF not enabled")
        print("- Incorrect credentials")
        print("- YANG model not supported")
        raise e


if __name__ == "__main__":
    complete_educational_demo()
