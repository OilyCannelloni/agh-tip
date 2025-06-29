#!/usr/bin/env python3

import cmd
import argparse
import shlex

intro = """Route leaking CLI"""

class RouteLeakingCli(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = '(route leaking cli> '
        self.intro = intro

    def default(self, line: str) -> None:
        print(f"Nieznana komenda: '{line}'. Napisz 'help' lub '?' aby uzyskać dostępne polecenia.")
        return

    def emptyline(self):
        return False

    def do_quit(self, line: str) -> bool:
        """Wyjście z programu: quit"""
        return True

    def do_initial_config(self, arg):
        """
        Krok 1: Wstępna konfiguracja urządzenia.
        """
        parser = argparse.ArgumentParser(
            prog="initial_config",
            description="Wykonuje wstępną konfigurację przełącznika (hostname, routing, vtp, console)."
        )
        parser.add_argument('--hostname', required=False, help="Nazwa hosta do ustawienia (np. R3, R4, R5).")

        try:
            args = parser.parse_args(shlex.split(arg))
            print("--- PARAMS: initial_config ---")
            print(f"   Argumenty: {args}")
            print("   (W tym miejscu nastąpiłaby właściwa implementacja konfiguracji)\n")
        except SystemExit:
            pass

    def do_create_vrf(self, arg):
        """
        Krok 2: Tworzenie instancji VRF.
        """
        parser = argparse.ArgumentParser(
            prog="create_vrf",
            description="Tworzy nową instancję VRF z podanym Route Distinguisher."
        )
        parser.add_argument('--name', required=True, help="Nazwa dla VRF (np. AGH, Common).")
        parser.add_argument('--rd', required=True, help="Route Distinguisher w formacie ASN:NN (np. 65500:1).")

        try:
            args = parser.parse_args(shlex.split(arg))
            print(f"--- PARAMS: create_vrf {args.name} ---")
            print(f"   Nazwa VRF: {args.name}")
            print(f"   Route Distinguisher: {args.rd}")
            print("   (W tym miejscu nastąpiłaby właściwa implementacja konfiguracji)\n")
        except SystemExit:
            pass

    def do_assign_interface(self, arg):
        """
        Krok 3: Przypisanie interfejsów do VRF.
        """
        parser = argparse.ArgumentParser(
            prog="assign_interface",
            description="Przypisuje i konfiguruje interfejs w ramach określonego VRF."
        )
        subparsers = parser.add_subparsers(dest='interface_type', required=True, help='Typ interfejsu')

        # interfejs fizyczny
        parser_phys = subparsers.add_parser('physical', help='Konfiguracja interfejsu fizycznego')
        parser_phys.add_argument('--name', required=True, help='Nazwa interfejsu (np. gi1/0/1)')
        parser_phys.add_argument('--vrf', required=True, help='Nazwa VRF do przypisania')
        parser_phys.add_argument('--ip', required=True, help='Adres IP')
        parser_phys.add_argument('--mask', required=True, help='Maska podsieci')
        parser_phys.add_argument('--desc', help='Opis interfejsu')

        # loopback
        parser_loop = subparsers.add_parser('loopback', help='Konfiguracja interfejsu loopback')
        parser_loop.add_argument('--id', required=True, type=int, help='Numer interfejsu loopback (np. 1)')
        parser_loop.add_argument('--vrf', required=True, help='Nazwa VRF do przypisania')
        parser_loop.add_argument('--ip', required=True, help='Adres IP')
        parser_loop.add_argument('--mask', default='255.255.255.255', help='Maska podsieci (domyślnie /32)')
        parser_loop.add_argument('--desc', help='Opis interfejsu')

        try:
            args = parser.parse_args(shlex.split(arg))
            print(f"--- PARAMS: assign_interface typu {args.interface_type} ---")
            print(f"   Argumenty: {args}")
            print("   (W tym miejscu nastąpiłaby właściwa implementacja konfiguracji)\n")
        except SystemExit:
            pass

    def do_configure_ospf(self, arg):
        """
        Krok 5: Konfiguracja OSPF w kontekście VRF.
        """
        parser = argparse.ArgumentParser(
            prog="configure_ospf",
            description="Konfiguruje i uruchamia proces OSPF dla wskazanego VRF."
        )
        parser.add_argument('--pid', required=True, type=int, help="ID procesu OSPF (np. 1, 2, 3).")
        parser.add_argument('--vrf', required=True, help="Nazwa VRF, w którym działa OSPF.")
        parser.add_argument('--network', required=True, help="Adres sieci do rozgłaszania (np. 10.0.0.0).")
        parser.add_argument('--wildcard', required=True, help="Maska wildcard (np. 0.255.255.255).")
        parser.add_argument('--area', required=True, type=int, help="Numer obszaru OSPF.")

        try:
            args = parser.parse_args(shlex.split(arg))
            print(f"--- PARAMS: configure_ospf dla VRF {args.vrf} ---")
            print(f"   Argumenty: {args}")
            print("   (W tym miejscu nastąpiłaby właściwa implementacja konfiguracji)\n")
        except SystemExit:
            pass

    def do_configure_bgp(self, arg):
        """
        Krok 6: Konfiguracja MP-BGP.
        """
        parser = argparse.ArgumentParser(
            prog="configure_bgp",
            description="Konfiguruje proces BGP i redystrybucję dla VRF."
        )
        parser.add_argument('--asn', required=True, type=int, help="Numer systemu autonomicznego BGP (np. 65500).")
        parser.add_argument('--router-id', required=True, help="Router ID dla procesu BGP (np. 1.1.1.1).")
        parser.add_argument('--vrf', required=True, help="VRF do skonfigurowania w BGP.")
        parser.add_argument(
            '--redistribute',
            required=True,
            action='append',
            choices=['connected', 'ospf'],
            help="Źródło tras do redystrybucji. Można podać wielokrotnie."
        )
        parser.add_argument('--ospf-pid', type=int, help="ID procesu OSPF, jeśli wybrano redystrybucję z OSPF.")

        try:
            args = parser.parse_args(shlex.split(arg))
            if 'ospf' in args.redistribute and not args.ospf_pid:
                parser.error("--ospf-pid jest wymagany przy redystrybucji z OSPF.")

            print(f"--- PARAMS: configure_bgp dla ASN {args.asn} i VRF {args.vrf} ---")
            print(f"   Argumenty: {args}")
            print("   (W tym miejscu nastąpiłaby właściwa implementacja konfiguracji)\n")
        except SystemExit:
            pass

    def do_configure_route_leaking(self, arg):
        """
        Krok 7: Konfiguracja Route Leaking.
        [cite_start]Ustawia atrybuty route-target import/export dla VRF. [cite: 29]
        """
        parser = argparse.ArgumentParser(
            prog="configure_route_leaking",
            description="Konfiguruje 'przeciekanie' tras poprzez atrybuty route-target."
        )
        parser.add_argument('--vrf', required=True, help="Nazwa VRF, dla którego ustawiane są targety.")
        parser.add_argument(
            '--import-rt',
            action='append',
            required=True,
            help="Route Target do importowania (np. 65500:0). Można użyć wielokrotnie."
        )
        parser.add_argument(
            '--export-rt',
            action='append',
            required=True,
            help="Route Target do eksportowania (np. 65500:1). Można użyć wielokrotnie."
        )
        parser.add_argument('--redistribute-bgp-in-ospf', type=int, metavar='OSPF_PID',
                            help='Opcjonalnie włącz redystrybucję BGP do OSPF o podanym PID.')

        try:
            args = parser.parse_args(shlex.split(arg))
            print(f"--- PARAMS: configure_route_leaking dla VRF {args.vrf} ---")
            print(f"   Import RT: {args.import_rt}")
            print(f"   Export RT: {args.export_rt}")
            if args.redistribute_bgp_in_ospf:
                print(f"   Włączono redystrybucję BGP do OSPF PID {args.redistribute_bgp_in_ospf}")
            print("   (W tym miejscu nastąpiłaby właściwa implementacja konfiguracji)\n")
        except SystemExit:
            pass

    def do_full_configuration(self, arg):
        """
        Uruchamia pełną sekwencję konfiguracji dla wybranego przełącznika.
        """
        pass

if __name__ == '__main__':
    route_leaking_cli = RouteLeakingCli()
    route_leaking_cli.cmdloop()
