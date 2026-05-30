"""
Bazowa klasa strategii.
Każda strategia w aplikacji dziedziczy po tej klasie.
"""


class BaseStrategy:
    """
    Szablon dla wszystkich strategii.

    Każda strategia musi:
    1. Mieć nazwę (self.name)
    2. Implementować metodę generate_signals(data)

    Metoda generate_signals przyjmuje DataFrame z cenami
    i zwraca ten sam DataFrame z dodaną kolumną 'signal':
        1  = kup (wejdź w pozycję)
        0  = trzymaj (nic nie rób)
       -1  = sprzedaj (wyjdź z pozycji)
    """

    def __init__(self, name="Unnamed Strategy"):
        self.name = name

    def generate_signals(self, data):
        """
        Generuje sygnały kupna/sprzedaży na podstawie danych.

        Parametry:
            data (DataFrame): Dane z kolumną 'Close'

        Zwraca:
            DataFrame: Kopia danych z dodaną kolumną 'signal'
        """
        # Klasa bazowa nie wie jak generować sygnały.
        # Każda konkretna strategia musi napisać własną wersję tej metody.
        # Jeśli ktoś zapomni — dostanie ten komunikat.
        raise NotImplementedError(
            f"Strategia '{self.name}' nie ma zaimplementowanej metody generate_signals()"
        )