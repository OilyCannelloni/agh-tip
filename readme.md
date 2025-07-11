# Używanie RESTConf

RESTConf to protokół umożliwiający edycję konfiguracji urządzeń sieciowych przy pomocy żądań HTTP. Przykładowo, aby
ustawić adres i maskę na interfejsie, wysyłamy następujące dane:

```
"GigabitEthernet": [
    {
        "name": "0/0/0",
        "ip": {
            "address": {
                "primary": {
                    "address": "10.0.0.1",
                    "mask": "255.255.255.0"
              }
         }
    },
}
```

na adres

```
PATCH https://10.0.0.1/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet
```

Dzięki temu możemy edytować cały zakres interfejsów prostym skryptem w Pythonie, bez wykorzystywania żadnych bibliotek
typu `netmiko`.

## Jak włączyć RESTConf na routerze?

Wykonaj polecenia na routerze:

```
en
conf t
hostname R1
username agh priv 15 pass xd
netconf-yang
restconf
ip http secure-server
ip http authentication local
```

## Jak ustawić nagłówki requestów REST?

W skrypcie Pythonowym użyj następujących parametrów:

```
# Disable SSL warnings for lab environment  
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  
  
# Standard headers for RESTCONF  
HEADERS = {  
    "Accept": "application/yang-data+json",  
    "Content-Type": "application/yang-data+json"  
}  
  
# Default authentication (Tak jak zdefiniowane w poprzednim podpunkcie)
DEFAULT_AUTH = ("agh", "xd")
```

Aby wysłać request, użyj poniższej funkcji:

```
def make_request(method: str, url: str, data: Optional[Dict] = None) -> requests.Response:  
    """Make a HTTP request with proper error handling"""  
    print(f"{method} {url}")  
    print(data)
    try:  
        response = requests.request(
            method=method,  
            url=url,  
            json=data,
            auth=DEFAULT_AUTH,  
            headers=HEADERS,  
            verify=False,  
            timeout=30  
        )  
        return response  
    except requests.exceptions.RequestException as e:  
        print(f"Request failed: {e}")  
        raise
```

## Jak znaleźć modele REST?

#### 1. Ustaw konfigurację na konsoli routera

```
en
conf t
int gi0/0/0
ip addr 10.0.0.1 255.255.255.0
no sh
```

#### 2. Wyślij request GET

```
GET https://10.0.0.1/restconf/data/Cisco-IOS-XE-native:native/
```

#### 3. Obejrzyj zwrócony JSON

```
"Cisco-IOS-XE-native:native": {
	...
	"interface": {
		...
		"GigabitEthernet": [
			...
			{
				"name": "0/0/0",
				"ip": {
					"address": {
						"primary": {
							"address": "10.0.0.1",
							"mask": "255.255.255.0"
					  }
				 }
			}
		]
  }
}
```

Szukany URL to po kolei pola, w których znajduje się obiekt, który chcemy edytować:

```
https://10.0.0.1/restconf/data/Cisco-IOS-XE-native:native/interface/GigabitEthernet
```

Aby edytować obiekt, wysyłamy request PATCH na ten URL, z danymi począwszy od pola, na którym kończy się URL (w tym
przypadku `"GigabitEthernet"` . PATCH może tylko modyfikować i dodawać dane - nie usuwać. W związku z tym powyższe
żądanie doda nowy interfejs, nawet jeśli są aktualnie zdefiniowane inne, nie będą one usunięte.


# Przykładowy skrypt konfiguracyjny

Przykładowy skrypt konfiguracyjny bgp znajduje sie w pliku main.py. Uruchomienie go wykona po sobie nastepujace kroki:
- polaczenie z routerem
- tworzenie VRF, przypisanie interfejsu do VRF
- OSPF
- konfiguracja BGP

Aby skorzystac z domyslnych usatwien, nalezy na ruterze skorzystac z ustawien podanych wyzej, tj. user: agh pass: xd. Urzadzenie, z ktorego testowalismy skrypt wpięte bylo w interfejs GigabitEthernet0/0/0, ktory mial adres 10.0.0.1 od strony routera.

**Uwaga!**
OSPF dziala niedeterministycznie, niestety nie udalo sie tego naprawic.

# Korzystanie z CLI

Zaimplementowano rowniez prosty interfejs CLI, ktory pozwala na wykonywanie podstawowych operacji na routerze. Aby go uruchomic, wystarczy uruchomic plik `cli.py`.
Interfejs pozwala na wykonanie scenariusza uruchamianego skryptem z 'main.py', krok po kroku.

CLI posiada wbudowaną dokumentację:
- `?` - wyświetla dostępne komendy
- `<komenda> -h` - wyświetla pomoc dla danej komendy

CLI napisane zostalo przy użyciu biblioteki `cmd`, która jest standardową biblioteką Pythona do tworzenia interaktywnych powłok, polecamy eksperymenty z tym rozwiazaniem, bardzo ulatwia prace.