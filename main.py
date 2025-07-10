from api import RestConfHandler
from models.interface import InterfaceConfig, InterfaceType, VrfConfig


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

    # Step 2: Create VRFs for route leaking
    print("*****Step 2: Creating VRFs...")

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

    # Step 3: Configure interfaces and assign to VRFs
    print("*****Step 3: Configuring interfaces...")

    # Interface for Customer A
    int_a = InterfaceConfig(
        name="GigabitEthernet0/0/1",
        description="Customer A Interface",
        ip_addr="11.0.0.1",
        ip_mask="255.255.255.0",
        vrf="CUSTOMER_A"
    )

    # Interface for Customer B (THIS WAS MISSING!)
    int_b = InterfaceConfig(
        name="GigabitEthernet0/0/2",
        description="Customer B Interface",
        ip_addr="12.0.0.1",
        ip_mask="255.255.255.0",
        vrf="CUSTOMER_B"
    )

    result_int_a = handler.update_interface(int_a)
    result_int_b = handler.update_interface(int_b)

    print(f"Interface GigE0/0/1 (Customer A): {result_int_a['status_code']}")
    print(f"Interface GigE0/0/2 (Customer B): {result_int_b['status_code']}")

    print("\n**Step 4: Configuring VRFS")

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

    # OSPF
    print("\n*****Step 5: Configuring OSPF")
    ospf_result = handler.create_ospfs()
    print(ospf_result['status_code'])


    # BGP
    print("\n*****Step 6: Configuring BGP address families...")
    bgp_result_a = handler.create_bgp(
        as_number=65000,
        vrf_name="CUSTOMER_A",
        rd="65000:100",
        import_rt="65000:200",
        export_rt="65000:100"
    )
    print(f"BGP Address Family: {bgp_result_a['status_code']}")




    # print("\nStep 6: Configuring BGP address families...")
    #
    # # BGP for Customer A VRF
    # bgp_result_a = handler.configure_bgp_address_family(
    #     as_number=65000,
    #     vrf_name="CUSTOMER_A",
    #     rd="65000:100",
    #     import_rt="65000:200",
    #     export_rt="65000:100"
    # )
    #
    # # BGP for Customer B VRF
    # bgp_result_b = handler.configure_bgp_address_family(
    #     as_number=65000,
    #     vrf_name="CUSTOMER_B",
    #     rd="65000:200",
    #     import_rt="65000:100",
    #     export_rt="65000:200"
    # )

    # print(f"BGP Address Family (Customer A): {bgp_result_a['status_code']}")
    # print(f"BGP Address Family (Customer B): {bgp_result_b['status_code']}")

    # Step 5: Verification and status check
    # print("\nStep 99: Verifying configuration...")
    #
    # # Check VRF status
    # vrfs = handler.get_vrfs()
    # print(vrfs)
    #
    # # Check interface status
    # interfaces = handler.get_interfaces()
    # print(interfaces)
    #
    # bgp = handler.get_bgp_config()
    # print(bgp)


def advanced_route_leaking_scenarios():
    """
    Advanced scenarios for educational purposes
    """
    print("\n=== Advanced Route Leaking Scenarios ===\n")

    handler = RestConfHandler("10.0.0.1")

    # Scenario 1: Hub-and-Spoke (Central services VRF)
    print("Scenario 1: Hub-and-Spoke Route Leaking")
    print("Use case: Shared services (DNS, DHCP) accessible from multiple customer VRFs")

    # Central services VRF
    services_vrf = VrfConfig(
        name="SHARED_SERVICES",
        rd="65000:999",
        export_rt="65000:999",
        import_rt="65000:100,65000:200"  # Imports from both customers
    )

    # Customer VRFs import from services
    customer_a_hub = VrfConfig(
        name="CUSTOMER_A_HUB",
        rd="65000:101",
        export_rt="65000:100",
        import_rt="65000:999"  # Only imports from services
    )

    # print("• SHARED_SERVICES VRF: Exports services, imports from customers")
    # print("• Customer VRFs: Export their routes, import only services")
    # print("• Result: Customers can access shared services but not each other\n")
    #
    # # Scenario 2: Selective Route Leaking
    # print("Scenario 2: Selective Route Leaking with Route Maps")
    # print("Use case: Only specific routes leaked between VRFs")
    # print("• Use route-maps to filter which routes are imported/exported")
    # print("• Example: Only leak default route or specific prefixes")
    # print("• Provides fine-grained control over route sharing\n")
    #
    # # Show how to add route-map configuration
    # print("Route-map example (would need additional RESTCONF calls):")
    # print("route-map LEAK_DEFAULT permit 10")
    # print(" match ip address prefix-list DEFAULT_ONLY")
    # print("!")
    # print("ip prefix-list DEFAULT_ONLY seq 5 permit 0.0.0.0/0")


# Complete educational demonstration
def complete_educational_demo():
    """
    Run the complete educational demonstration
    """
    try:
        # Main demo
        educational_route_leaking_demo()

        # Advanced scenarios
        # advanced_route_leaking_scenarios()


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
