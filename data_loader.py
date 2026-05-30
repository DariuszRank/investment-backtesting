"""
Moduł do ładowania danych finansowych.
Obsługuje dwa źródła: Yahoo Finance (API) oraz pliki CSV.
"""

import pandas as pd
import yfinance as yf


def load_from_yahoo(ticker, start_date, end_date):
    """
    Pobiera dane historyczne z Yahoo Finance.

    Parametry:
        ticker (str): Symbol instrumentu, np. "SPY", "AAPL", "^GSPC"
        start_date (str): Data początkowa w formacie "YYYY-MM-DD"
        end_date (str): Data końcowa w formacie "YYYY-MM-DD"

    Zwraca:
        pandas.DataFrame z kolumnami: Date (indeks) i Close
    """
    data = yf.download(ticker, start=start_date, end=end_date)

    # Zostawiamy tylko kolumnę 'Close' — cena zamknięcia
    # To jest cena na koniec dnia handlowego
    # Dla naszych celów to wystarczy
    data = data[["Close"]].copy()

    # Usuwamy wiersze z brakującymi danymi (np. dni bez handlu)
    data = data.dropna()

    # Upewniamy się że kolumna Close zawiera zwykłe liczby (float)
    # yfinance czasem zwraca dane w formacie MultiIndex
    data.columns = ["Close"]

    return data


def load_from_csv(file_path, date_column="Date", close_column="Close"):
    """
    Wczytuje dane historyczne z pliku CSV.

    Parametry:
        file_path (str): Ścieżka do pliku CSV
        date_column (str): Nazwa kolumny z datami (domyślnie "Date")
        close_column (str): Nazwa kolumny z cenami zamknięcia (domyślnie "Close")

    Zwraca:
        pandas.DataFrame z kolumnami: Date (indeks) i Close
    """
    data = pd.read_csv(file_path)

    # Konwertujemy kolumnę z datami na typ datetime
    # Python musi wiedzieć że to daty, a nie zwykły tekst
    data[date_column] = pd.to_datetime(data[date_column])

    # Ustawiamy datę jako indeks (tak samo jak dane z Yahoo)
    data = data.set_index(date_column)

    # Zostawiamy tylko kolumnę z cenami zamknięcia
    data = data[[close_column]].copy()
    data.columns = ["Close"]

    # Usuwamy brakujące dane
    data = data.dropna()

    # Sortujemy po dacie (od najstarszej do najnowszej)
    data = data.sort_index()

    return data


def load_multiple_from_yahoo(tickers, start_date, end_date):
    """
    Pobiera dane dla wielu instrumentów naraz.
    Przyda się później np. dla strategii GEM, która porównuje kilka instrumentów.

    Parametry:
        tickers (list): Lista symboli, np. ["SPY", "EFA", "AGG"]
        start_date (str): Data początkowa
        end_date (str): Data końcowa

    Zwraca:
        dict: Słownik {ticker: DataFrame}
    """
    result = {}

    for ticker in tickers:
        result[ticker] = load_from_yahoo(ticker, start_date, end_date)

    return result