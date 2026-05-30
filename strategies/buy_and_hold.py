"""
Strategia Buy and Hold.
Najprostsza strategia inwestycyjna — kup i trzymaj.
"""

from strategies.base_strategy import BaseStrategy


class BuyAndHold(BaseStrategy):
    """
    Kup pierwszego dnia, trzymaj do końca okresu.
    Nie robisz nic — żadnych transakcji po początkowym zakupie.
    """

    def __init__(self):
        # Wywołujemy __init__ klasy bazowej i podajemy nazwę strategii
        super().__init__(name="Buy and Hold")

    def generate_signals(self, data):
        """
        Generuje sygnały dla Buy and Hold.

        Logika:
        - Dzień 1: sygnał = 1 (kup)
        - Wszystkie kolejne dni: sygnał = 0 (trzymaj)
        """
        # Tworzymy kopię danych żeby nie modyfikować oryginału
        df = data.copy()

        # Domyślnie wszystkie dni = 0 (trzymaj)
        df["signal"] = 0

        # Pierwszy dzień = 1 (kup)
        df.iloc[0, df.columns.get_loc("signal")] = 1

        return df