"""
SZ.5: Wykorzystanie interfejsu programistycznego do konfiguracji mechanizmu route leaking na urządzeniach w laboratorium sieciowym.
Zadaniem zespołu będzie przygotowanie aplikacji wykorzystującej programowy dostęp do urządzeń sieciowych zainstalowanych
w laboratorium w celu ułatwienia konfiguracji i sprawdzenia stanu "przeciekania tras" w MP-BGP. Preferowany interfejs
programistyczny: RESTconf. Ważne: aplikacja ma mieć aspekt edukacyjny, tzn. ma być przygotowana w formie
umożliwiającej samodzielną naukę wykorzystania takiego interfejsu.
"""
from api import RestConfHandler
from models.interface import InterfaceConfig, InterfaceType

handler = RestConfHandler("10.0.0.1")

config = InterfaceConfig(
    name="GigabitEthernet0/0/0",
    type=InterfaceType.DEFAULT
)
handler.update_interface()