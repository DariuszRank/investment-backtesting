"""
Moduł do wizualizacji wyników backtestingu.
Wykresy equity curve, drawdown i tabelki porównawcze.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np


def plot_equity_curves(results_dict, title="Porównanie strategii", figsize=(12, 8)):
    """
    Rysuje wykres porównujący equity curves kilku strategii.

    Parametry:
        results_dict (dict): Słownik {nazwa: DataFrame_z_portfolio_value}
        title (str): Tytuł wykresu
        figsize (tuple): Rozmiar wykresu (szerokość, wysokość)
    """
    plt.figure(figsize=figsize)

    # Dla każdej strategii rysuj linię
    for name, data in results_dict.items():
        plt.plot(data.index, data['portfolio_value'], label=name, linewidth=2)

    # Formatowanie wykresu
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel('Data', fontsize=12)
    plt.ylabel('Wartość portfela (EUR)', fontsize=12)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)

    # Formatowanie osi X (daty)
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(rotation=45)

    # Formatowanie osi Y (wartości w tysiącach)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x / 1000:.0f}k'))

    plt.tight_layout()
    plt.show()


def plot_drawdown(equity_curve, title="Drawdown strategii", figsize=(12, 6)):
    """
    Rysuje wykres drawdown (obsunięć) strategii.

    Parametry:
        equity_curve (Series): Seria wartości portfela z indeksem DatetimeIndex
        title (str): Tytuł wykresu
        figsize (tuple): Rozmiar wykresu
    """
    # Oblicz drawdown
    peak = equity_curve.expanding().max()
    drawdown = (peak - equity_curve) / peak * 100  # w procentach

    plt.figure(figsize=figsize)

    # Rysuj drawdown jako obszar pod zerem
    plt.fill_between(drawdown.index, drawdown, 0,
                     color='red', alpha=0.3, label='Drawdown')
    plt.plot(drawdown.index, drawdown, color='red', linewidth=1)

    # Formatowanie
    plt.title(title, fontsize=16, fontweight='bold')
    plt.xlabel('Data', fontsize=12)
    plt.ylabel('Drawdown (%)', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)

    # Formatowanie osi X
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    ax.xaxis.set_major_locator(mdates.YearLocator())
    plt.xticks(rotation=45)

    # Oś Y pokazuje wartości ujemne (spadki)
    plt.ylim(top=5)  # trochę miejsca nad zerem

    # Pokaż maksymalny drawdown
    max_dd = drawdown.max()
    plt.axhline(y=max_dd, color='darkred', linestyle='--', alpha=0.7)
    plt.text(0.02, 0.95, f'Max Drawdown: {max_dd:.1f}%',
             transform=ax.transAxes, fontsize=12,
             bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))

    plt.tight_layout()
    plt.show()


def plot_monthly_returns_heatmap(equity_curve, title="Miesięczne zwroty (%)", figsize=(12, 8)):
    """
    Rysuje heatmapę miesięcznych zwrotów (zaawansowana wizualizacja).

    Parametry:
        equity_curve (Series): Seria wartości portfela z indeksem DatetimeIndex
        title (str): Tytuł wykresu
        figsize (tuple): Rozmiar wykresu
    """
    # Przekształć equity curve na miesięczne zwroty
    monthly_eq = equity_curve.resample('ME').last()
    monthly_returns = monthly_eq.pct_change().dropna() * 100  # w procentach

    # Utwórz DataFrame z rokiem i miesiącem
    df = monthly_returns.to_frame('return')
    df['year'] = df.index.year
    df['month'] = df.index.month

    # Pivot table: rok = wiersze, miesiąc = kolumny
    heatmap_data = df.pivot_table(values='return', index='year', columns='month')

    # Nazwy miesięcy
    month_names = ['Sty', 'Lut', 'Mar', 'Kwi', 'Maj', 'Cze',
                   'Lip', 'Sie', 'Wrz', 'Paź', 'Lis', 'Gru']
    heatmap_data.columns = month_names[:len(heatmap_data.columns)]

    plt.figure(figsize=figsize)

    # Kolorowa mapa: zielony = zysk, czerwony = strata
    im = plt.imshow(heatmap_data.values, cmap='RdYlGn', aspect='auto')

    # Ustaw etykiety osi
    plt.xticks(range(len(heatmap_data.columns)), heatmap_data.columns)
    plt.yticks(range(len(heatmap_data.index)), heatmap_data.index)
    plt.xlabel('Miesiąc', fontsize=12)
    plt.ylabel('Rok', fontsize=12)
    plt.title(title, fontsize=16, fontweight='bold')

    # Dodaj wartości liczbowe w komórkach
    for i in range(len(heatmap_data.index)):
        for j in range(len(heatmap_data.columns)):
            value = heatmap_data.iloc[i, j]
            if not np.isnan(value):
                plt.text(j, i, f'{value:.1f}%', ha='center', va='center',
                         color='black' if abs(value) < 5 else 'white', fontsize=10)

    # Colorbar
    cbar = plt.colorbar(im, shrink=0.8)
    cbar.set_label('Miesięczny zwrot (%)', fontsize=11)

    plt.tight_layout()
    plt.show()


def create_performance_comparison_chart(metrics_dict, title="Porównanie metryk", figsize=(10, 6)):
    """
    Tworzy wykres słupkowy porównujący metryki różnych strategii.

    Parametry:
        metrics_dict (dict): Słownik {nazwa_strategii: dict_z_metrykami}
        title (str): Tytuł wykresu
        figsize (tuple): Rozmiar wykresu
    """
    strategies = list(metrics_dict.keys())
    metrics_to_plot = ['Total Return', 'CAGR', 'Max Drawdown', 'Sharpe Ratio']

    # Przygotuj dane
    data = {metric: [] for metric in metrics_to_plot}

    for strategy in strategies:
        for metric in metrics_to_plot:
            value = metrics_dict[strategy][metric]
            # Przelicz na procenty gdzie sensowne
            if metric in ['Total Return', 'CAGR', 'Max Drawdown']:
                value *= 100
            data[metric].append(value)

    # Utwórz subplot dla każdej metryki
    fig, axes = plt.subplots(2, 2, figsize=figsize)
    axes = axes.flatten()

    for i, metric in enumerate(metrics_to_plot):
        ax = axes[i]
        bars = ax.bar(strategies, data[metric])

        # Kolorowanie: zielony = dobrze, czerwony = źle
        if metric in ['Total Return', 'CAGR', 'Sharpe Ratio']:
            colors = ['green' if x > 0 else 'red' for x in data[metric]]
        else:  # Max Drawdown (mniejsze = lepsze)
            colors = ['red' if x > 20 else 'orange' if x > 10 else 'green' for x in data[metric]]

        for bar, color in zip(bars, colors):
            bar.set_color(color)
            bar.set_alpha(0.7)

        # Formatowanie
        ax.set_title(metric)
        if metric in ['Total Return', 'CAGR', 'Max Drawdown']:
            ax.set_ylabel('%')
        else:
            ax.set_ylabel('Współczynnik')

        # Obróć etykiety X jeśli za długie
        if any(len(s) > 8 for s in strategies):
            ax.tick_params(axis='x', rotation=45)

        ax.grid(True, alpha=0.3)

    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.show()


def print_detailed_comparison(results_dict, metrics_dict):
    """
    Wyświetla szczegółową tabelę porównawczą w konsoli.

    Parametry:
        results_dict (dict): Słownik z wynikami backtestingu
        metrics_dict (dict): Słownik z metrykami
    """
    print(f"\n{'=' * 80}")
    print(f"{'SZCZEGÓŁOWE PORÓWNANIE STRATEGII':^80}")
    print(f"{'=' * 80}")

    strategies = list(results_dict.keys())

    # Nagłówek tabeli
    print(f"{'Strategia':<20}", end='')
    for strategy in strategies:
        print(f"{strategy:>15}", end='')
    print()
    print('-' * 80)

    # Podstawowe informacje
    print(f"{'Okres analizy':<20}", end='')
    for strategy in strategies:
        data = results_dict[strategy]
        start = data.index[0].strftime('%Y-%m-%d')
        end = data.index[-1].strftime('%Y-%m-%d')
        print(f"{start} — {end}"[:15].rjust(15), end='')
    print()

    print(f"{'Liczba dni':<20}", end='')
    for strategy in strategies:
        days = len(results_dict[strategy])
        print(f"{days:>15}", end='')
    print()

    print('-' * 80)

    # Metryki
    metrics_display = [
        ('Total Return (%)', 'Total Return', 100),
        ('CAGR (%)', 'CAGR', 100),
        ('Volatility (%)', 'Volatility', 100),
        ('Max Drawdown (%)', 'Max Drawdown', 100),
        ('Sharpe Ratio', 'Sharpe Ratio', 1)
    ]

    for display_name, key, multiplier in metrics_display:
        print(f"{display_name:<20}", end='')
        for strategy in strategies:
            value = metrics_dict[strategy][key] * multiplier
            if multiplier == 1:  # Sharpe Ratio
                print(f"{value:>15.2f}", end='')
            else:  # Procenty
                print(f"{value:>14.1f}%", end='')
        print()

    print('=' * 80)