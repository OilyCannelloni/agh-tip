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
