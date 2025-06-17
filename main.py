"""
SZ.5: Wykorzystanie interfejsu programistycznego do konfiguracji mechanizmu route leaking na urządzeniach w laboratorium sieciowym.
Zadaniem zespołu będzie przygotowanie aplikacji wykorzystującej programowy dostęp do urządzeń sieciowych zainstalowanych
w laboratorium w celu ułatwienia konfiguracji i sprawdzenia stanu "przeciekania tras" w MP-BGP. Preferowany interfejs
programistyczny: RESTconf. Ważne: aplikacja ma mieć aspekt edukacyjny, tzn. ma być przygotowana w formie
umożliwiającej samodzielną naukę wykorzystania takiego interfejsu.
"""
from api import RestConfHandler
from models.interface import InterfaceConfig, InterfaceType


def educational_route_leaking_demo():
    """
    Educational demonstration of route leaking configuration using RESTCONF

    This function demonstrates the key concepts and steps for configuring
    route leaking between VRFs using programmatic interfaces.
    """

    print("=== RESTCONF Route Leaking Educational Demo ===\n")

    # Step 1: Connect to device
    print("Step 1: Connecting to network device...")
    handler = RestConfHandler("10.0.0.1")  # Replace with your device IP

    if not handler.test_connection():
        print("❌ Cannot connect to device. Check IP, credentials, and RESTCONF enablement.")
        return
    print("✅ Connected successfully!\n")

    # Step 2: Create VRFs for route leaking
    print("Step 2: Creating VRFs...")

    # VRF for customer A
    vrf_a = VrfConfig(
        name="CUSTOMER_A",
        rd="65000:100",
        export_rt="65000:100",
        import_rt="65000:200"
    )

    # VRF for customer B
    vrf_b = VrfConfig(
        name="CUSTOMER_B",
        rd="65000:200",
        export_rt="65000:200",
        import_rt="65000:100"
    )

    result_a = handler.create_vrf(vrf_a)
    result_b = handler.create_vrf(vrf_b)

    print(f"VRF CUSTOMER_A: {'✅' if result_a['status_code'] in [200, 201, 204] else '❌'}")
    print(f"VRF CUSTOMER_B: {'✅' if result_b['status_code'] in [200, 201, 204] else '❌'}\n")

    # Step 3: Configure interfaces and assign to VRFs
    print("Step 3: Configuring interfaces...")

    # Interface for Customer A
    int_a = InterfaceConfig(
        name="GigabitEthernet0/0/1",
        type=InterfaceType.ETHERNET,
        ip_addr="192.168.1.1",
        ip_mask="255.255.255.0",
        description="Customer A Interface",
        vrf="CUSTOMER_A"
    )

    result_int_a = handler.update_interface(int_a)
    print(f"Interface GigE0/0/1: {'✅' if result_int_a['status_code'] in [200, 201, 204] else '❌'}")

    # Step 4: Configure BGP for route leaking
    print("\nStep 4: Configuring BGP address families...")

    bgp_result = handler.configure_bgp_address_family(
        as_number=65000,
        vrf_name="CUSTOMER_A",
        rd="65000:100",
        import_rt="65000:200",
        export_rt="65000:100"
    )

    print(f"BGP Address Family: {'✅' if bgp_result['status_code'] in [200, 201, 204] else '❌'}")

    print("\n=== Route Leaking Configuration Complete! ===")
    print("\nKey Concepts Demonstrated:")
    print("1. VRF creation with Route Distinguishers (RD)")
    print("2. Route Target import/export for selective route sharing")
    print("3. Interface assignment to VRFs")
    print("4. BGP address family configuration for MP-BGP")
    print("\nThis enables controlled route sharing between VRFs - the foundation of route leaking!")


if __name__ == "__main__":
    educational_route_leaking_demo()