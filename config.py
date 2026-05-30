"""
Moduł konfiguracyjny.
Zawiera dane brokerów, ustawienia podatkowe i funkcje pomocnicze.

WAŻNE: Wszystkie kwoty w aplikacji są w EUR.
"""

# --- WALUTA ---
CURRENCY = "EUR"


# --- BROKERZY ---
# commission     = prowizja od transakcji (ułamek, np. 0.0029 = 0.29%)
# min_commission = minimalna prowizja w EUR (0 jeśli nie ma)

BROKERS = {
    "xtb": {
        "name": "XTB",
        "commission": 0.0,
        "min_commission": 0.0,
        "description": "XTB — bez prowizji dla akcji i ETF (do limitu obrotu)"
    },
    "bos": {
        "name": "DM BOŚ",
        "commission": 0.0029,
        "min_commission": 4.0,
        "description": "DM BOŚ — 0.29%, minimum 4 EUR"
    },
    "mbank": {
        "name": "mBank eMakler",
        "commission": 0.0029,
        "min_commission": 6.0,
        "description": "mBank eMakler — 0.29%, minimum 6 EUR"
    },
    "dif": {
        "name": "DIF Broker",
        "commission": 0.0015,
        "min_commission": 4.0,
        "description": "DIF Broker — 0.15%, minimum 4 EUR"
    }
}


# --- TYPY KONT PODATKOWYCH ---
# tax_rate = stawka podatku od zysków kapitałowych (ułamek)

ACCOUNT_TYPES = {
    "taxed": {
        "name": "Konto opodatkowane",
        "tax_rate": 0.19,
        "description": "Standardowe konto maklerskie — 19% podatku od zysków"
    },
    "tax_free": {
        "name": "IKE / IKZE",
        "tax_rate": 0.0,
        "description": "Konto zwolnione z podatku od zysków kapitałowych"
    }
}


# --- FUNKCJE POMOCNICZE ---

def get_broker(broker_id):
    """
    Zwraca dane brokera na podstawie jego identyfikatora.

    Parametry:
        broker_id (str): Klucz brokera, np. "xtb", "mbank", "bos"

    Zwraca:
        dict z danymi brokera
    """
    if broker_id not in BROKERS:
        print(f"Nieznany broker: '{broker_id}'")
        print(f"Dostępni brokerzy: {list(BROKERS.keys())}")
        return None

    return BROKERS[broker_id]


def get_account_type(account_id):
    """
    Zwraca dane typu konta na podstawie identyfikatora.

    Parametry:
        account_id (str): Klucz konta, np. "taxed", "tax_free"

    Zwraca:
        dict z danymi konta
    """
    if account_id not in ACCOUNT_TYPES:
        print(f"Nieznany typ konta: '{account_id}'")
        print(f"Dostępne typy: {list(ACCOUNT_TYPES.keys())}")
        return None

    return ACCOUNT_TYPES[account_id]


def calculate_commission(transaction_value, broker_id):
    """
    Oblicza prowizję za pojedynczą transakcję (kupno lub sprzedaż).

    Parametry:
        transaction_value (float): Wartość transakcji w EUR
        broker_id (str): Identyfikator brokera

    Zwraca:
        float: Kwota prowizji w EUR
    """
    broker = get_broker(broker_id)
    if broker is None:
        return 0.0

    # Prowizja procentowa
    commission = transaction_value * broker["commission"]

    # Sprawdź czy nie jest poniżej minimum
    if commission < broker["min_commission"]:
        commission = broker["min_commission"]

    return commission


def calculate_tax(profit, account_id):
    """
    Oblicza podatek od zysku ze sprzedaży.

    Parametry:
        profit (float): Zysk ze sprzedaży w EUR (ujemny = strata)
        account_id (str): Typ konta

    Zwraca:
        float: Kwota podatku w EUR (0 jeśli strata lub konto zwolnione)
    """
    if profit <= 0:
        return 0.0

    account = get_account_type(account_id)
    if account is None:
        return 0.0

    return profit * account["tax_rate"]


def list_brokers():
    """Wyświetla listę dostępnych brokerów."""
    print(f"\nDostępni brokerzy (prowizje w {CURRENCY}):")
    print("-" * 60)
    for broker_id, broker in BROKERS.items():
        print(f"  {broker_id:10s} → {broker['description']}")


def list_account_types():
    """Wyświetla listę dostępnych typów kont."""
    print("\nDostępne typy kont:")
    print("-" * 60)
    for account_id, account in ACCOUNT_TYPES.items():
        print(f"  {account_id:10s} → {account['description']}")