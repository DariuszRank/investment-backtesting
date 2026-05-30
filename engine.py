"""
Silnik backtestingu.
Symuluje przebieg portfela na podstawie sygnałów strategii.
"""

from config import calculate_commission, calculate_tax, get_broker, get_account_type


class BacktestEngine:
    """
    Silnik backtestingu — serce aplikacji.

    Przyjmuje dane z sygnałami strategii i symuluje portfel dzień po dniu,
    uwzględniając prowizje brokera i podatki.

    Zasady:
    - Kupno (sygnał 1): inwestujemy całą gotówkę (minus prowizja)
    - Trzymaj (sygnał 0): nic nie robimy
    - Sprzedaż (sygnał -1): sprzedajemy wszystko (minus prowizja i podatek)
    """

    def __init__(self, broker_id="xtb", account_id="tax_free", initial_capital=10000):
        """
        Parametry:
            broker_id (str): Identyfikator brokera (np. "xtb", "bos")
            account_id (str): Typ konta ("taxed" lub "tax_free")
            initial_capital (float): Kapitał początkowy w EUR
        """
        self.broker_id = broker_id
        self.account_id = account_id
        self.initial_capital = initial_capital

        # Pobieramy dane brokera i konta (do wyświetlania)
        self.broker = get_broker(broker_id)
        self.account = get_account_type(account_id)

    def run(self, data_with_signals):
        """
        Uruchamia symulację backtestingu.

        Parametry:
            data_with_signals (DataFrame): Dane z kolumnami 'Close' i 'signal'

        Zwraca:
            DataFrame: Kopia danych z dodaną kolumną 'portfolio_value'
        """
        df = data_with_signals.copy()

        # --- Stan portfela ---
        cash = self.initial_capital   # gotówka w EUR
        units = 0.0                   # ile jednostek instrumentu posiadamy
        buy_price = 0.0               # cena po której kupiliśmy (do obliczenia zysku)

        # --- Liczniki (do podsumowania) ---
        total_commissions = 0.0       # suma zapłaconych prowizji
        total_taxes = 0.0             # suma zapłaconych podatków
        num_trades = 0                # liczba transakcji (kupno + sprzedaż)

        # --- Lista wartości portfela (jedna wartość na każdy dzień) ---
        portfolio_values = []

        # --- Główna pętla: dzień po dniu ---
        for i in range(len(df)):
            price = df["Close"].iloc[i]
            signal = df["signal"].iloc[i]

            # === KUPNO ===
            if signal == 1 and units == 0:
                commission = calculate_commission(cash, self.broker_id)
                invest_amount = cash - commission
                units = invest_amount / price
                buy_price = price
                cash = 0.0

                total_commissions += commission
                num_trades += 1

            # === SPRZEDAŻ ===
            elif signal == -1 and units > 0:
                sell_value = units * price
                commission = calculate_commission(sell_value, self.broker_id)
                profit = (price - buy_price) * units
                tax = calculate_tax(profit, self.account_id)

                cash = sell_value - commission - tax
                units = 0.0
                buy_price = 0.0

                total_commissions += commission
                total_taxes += tax
                num_trades += 1

            # === TRZYMAJ (sygnał = 0) ===
            # Nic nie robimy — wartość portfela zmienia się z ceną

            # --- Oblicz wartość portfela na koniec dnia ---
            portfolio_value = cash + units * price
            portfolio_values.append(portfolio_value)

        # --- Dodaj wartości portfela do DataFrame ---
        df["portfolio_value"] = portfolio_values

        # --- Zapamiętaj statystyki ---
        self.total_commissions = total_commissions
        self.total_taxes = total_taxes
        self.num_trades = num_trades
        self.final_value = portfolio_values[-1]

        return df

    def print_summary(self):
        """Wyświetla podsumowanie backtestingu."""
        print(f"\n{'=' * 50}")
        print(f"PODSUMOWANIE BACKTESTINGU")
        print(f"{'=' * 50}")
        print(f"Broker:             {self.broker['name']}")
        print(f"Typ konta:          {self.account['name']}")
        print(f"Kapitał początkowy: {self.initial_capital:,.2f} EUR")
        print(f"Wartość końcowa:    {self.final_value:,.2f} EUR")
        print(f"Zwrot:              {((self.final_value / self.initial_capital) - 1) * 100:.2f}%")
        print(f"Liczba transakcji:  {self.num_trades}")
        print(f"Suma prowizji:      {self.total_commissions:,.2f} EUR")
        print(f"Suma podatków:      {self.total_taxes:,.2f} EUR")
        print(f"{'=' * 50}")