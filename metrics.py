"""
Moduł do obliczania metryk strategii inwestycyjnych.
Pracuje na equity curve (krzywej wartości portfela w czasie).
"""

import pandas as pd
import numpy as np


def total_return(equity_curve):
    """
    Oblicza całkowity zwrot strategii.

    Parametry:
        equity_curve (Series): Seria wartości portfela w czasie

    Zwraca:
        float: Zwrot w ujęciu ułamkowym (0.5 = 50%)
    """
    start_value = equity_curve.iloc[0]
    end_value = equity_curve.iloc[-1]
    return (end_value / start_value) - 1


def cagr(equity_curve):
    """
    Oblicza CAGR — średnioroczny zwrot (Compound Annual Growth Rate).

    Parametry:
        equity_curve (Series): Seria wartości portfela z indeksem DatetimeIndex

    Zwraca:
        float: CAGR w ujęciu ułamkowym (0.08 = 8% rocznie)
    """
    start_value = equity_curve.iloc[0]
    end_value = equity_curve.iloc[-1]

    # Oblicz liczbę lat między pierwszą a ostatnią datą
    start_date = equity_curve.index[0]
    end_date = equity_curve.index[-1]
    years = (end_date - start_date).days / 365.25

    # Zabezpieczenie przed dzieleniem przez zero
    if years <= 0:
        return 0.0

    # Wzór na CAGR
    return (end_value / start_value) ** (1 / years) - 1


def max_drawdown(equity_curve):
    """
    Oblicza maksymalne obsunięcie (max drawdown).

    Parametry:
        equity_curve (Series): Seria wartości portfela w czasie

    Zwraca:
        float: Max drawdown w ujęciu ułamkowym (0.2 = 20% spadek)
    """
    # Obliczamy "running maximum" — najwyższą wartość do tej pory
    peak = equity_curve.expanding().max()

    # Drawdown to różnica między szczytem a aktualną wartością
    drawdown = (peak - equity_curve) / peak

    # Maksymalny drawdown to największa wartość z serii drawdown
    return drawdown.max()


def volatility(equity_curve, annualized=True):
    """
    Oblicza zmienność (odchylenie standardowe zwrotów).

    Parametry:
        equity_curve (Series): Seria wartości portfela w czasie
        annualized (bool): Czy przeliczać na wartość roczną

    Zwraca:
        float: Zmienność w ujęciu ułamkowym (0.15 = 15% rocznie)
    """
    # Obliczamy dzienne zwroty (percent change)
    daily_returns = equity_curve.pct_change().dropna()

    # Odchylenie standardowe dziennych zwrotów
    daily_vol = daily_returns.std()

    if annualized:
        # Przeliczenie na volatility roczną (zakładamy ~252 dni handlowych w roku)
        return daily_vol * np.sqrt(252)
    else:
        return daily_vol


def sharpe_ratio(equity_curve, risk_free_rate=0.0):
    """
    Oblicza współczynnik Sharpe.

    Parametry:
        equity_curve (Series): Seria wartości portfela z indeksem DatetimeIndex
        risk_free_rate (float): Stopa wolna od ryzyka (roczna, domyślnie 0%)

    Zwraca:
        float: Współczynnik Sharpe
    """
    strategy_cagr = cagr(equity_curve)
    strategy_vol = volatility(equity_curve, annualized=True)

    # Zabezpieczenie przed dzieleniem przez zero
    if strategy_vol == 0:
        return 0.0

    return (strategy_cagr - risk_free_rate) / strategy_vol


def calculate_all_metrics(equity_curve, risk_free_rate=0.0):
    """
    Oblicza wszystkie metryki jednocześnie.

    Parametry:
        equity_curve (Series): Seria wartości portfela z indeksem DatetimeIndex
        risk_free_rate (float): Stopa wolna od ryzyka (roczna)

    Zwraca:
        dict: Słownik z wszystkimi metrykami
    """
    return {
        "Total Return": total_return(equity_curve),
        "CAGR": cagr(equity_curve),
        "Volatility": volatility(equity_curve),
        "Max Drawdown": max_drawdown(equity_curve),
        "Sharpe Ratio": sharpe_ratio(equity_curve, risk_free_rate)
    }


def print_metrics(metrics, title="METRYKI STRATEGII"):
    """
    Wyświetla metryki w czytelnym formacie.

    Parametry:
        metrics (dict): Słownik z metrykami (z calculate_all_metrics)
        title (str): Tytuł sekcji
    """
    print(f"\n{'-' * 40}")
    print(f"{title}")
    print(f"{'-' * 40}")
    print(f"Total Return:     {metrics['Total Return'] * 100:>8.2f}%")
    print(f"CAGR:             {metrics['CAGR'] * 100:>8.2f}%")
    print(f"Volatility:       {metrics['Volatility'] * 100:>8.2f}%")
    print(f"Max Drawdown:     {metrics['Max Drawdown'] * 100:>8.2f}%")
    print(f"Sharpe Ratio:     {metrics['Sharpe Ratio']:>8.2f}")
    print(f"{'-' * 40}")


def compare_metrics(metrics1, metrics2, name1="Strategia A", name2="Strategia B"):
    """
    Porównuje metryki dwóch strategii w formie tabelki.

    Parametry:
        metrics1 (dict): Metryki pierwszej strategii
        metrics2 (dict): Metryki drugiej strategii
        name1 (str): Nazwa pierwszej strategii
        name2 (str): Nazwa drugiej strategii
    """
    print(f"\n{'PORÓWNANIE STRATEGII':^50}")
    print("=" * 50)
    print(f"{'Metryka':<20} {name1:>12} {name2:>12}")
    print("-" * 50)

    metrics = [
        ("Total Return", "Total Return", "%"),
        ("CAGR", "CAGR", "%"),
        ("Volatility", "Volatility", "%"),
        ("Max Drawdown", "Max Drawdown", "%"),
        ("Sharpe Ratio", "Sharpe Ratio", "")
    ]

    for display_name, key, unit in metrics:
        val1 = metrics1[key]
        val2 = metrics2[key]

        if unit == "%":
            print(f"{display_name:<20} {val1*100:>10.2f}% {val2*100:>10.2f}%")
        else:
            print(f"{display_name:<20} {val1:>12.2f} {val2:>12.2f}")

    print("=" * 50)