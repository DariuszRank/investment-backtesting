"""
Główny plik aplikacji do backtestingu.
Testowanie modułów — fokus na wizualizacji.
"""

from data_loader import load_from_yahoo
from strategies import BuyAndHold
from engine import BacktestEngine
from metrics import calculate_all_metrics
from visualization import (
    plot_equity_curves,
    plot_drawdown,
    plot_monthly_returns_heatmap,
    create_performance_comparison_chart,
    print_detailed_comparison
)

# ============================================================
# PRZYGOTOWANIE DANYCH
# ============================================================
print("=" * 60)
print("PRZYGOTOWANIE DANYCH I STRATEGII")
print("=" * 60)

# Pobierz dane SPY
spy_data = load_from_yahoo("SPY", "2020-01-01", "2024-12-31")
print(f"✓ Pobrano dane SPY: {len(spy_data)} dni")

# Strategia
strategy = BuyAndHold()
signals = strategy.generate_signals(spy_data)
print(f"✓ Wygenerowano sygnały: {strategy.name}")

# ============================================================
# BACKTESTY RÓŻNYCH KONFIGURACJI
# ============================================================
print("\n" + "=" * 60)
print("URUCHAMIANIE BACKTESTÓW")
print("=" * 60)

# Różne konfiguracje do porównania
configs = [
    ("XTB (0%)", "xtb", "tax_free"),
    ("BOŚ (0.29%)", "bos", "tax_free"),
    ("mBank (0.29%)", "mbank", "tax_free"),
    ("DIF (0.15%)", "dif", "tax_free")
]

results_dict = {}
metrics_dict = {}

for name, broker_id, account_id in configs:
    # Uruchom backtest
    engine = BacktestEngine(broker_id, account_id, 10_000)
    results = engine.run(signals)

    # Oblicz metryki
    metrics = calculate_all_metrics(results['portfolio_value'])

    # Zapisz wyniki
    results_dict[name] = results
    metrics_dict[name] = metrics

    print(f"✓ {name}: {engine.final_value:,.0f} EUR")

print("\nGotowe! Rozpoczynam wizualizacje...")

# ============================================================
# TEST ETAPU 6: WIZUALIZACJE
# ============================================================
print("\n" + "=" * 60)
print("TEST ETAPU 6: WIZUALIZACJE")
print("=" * 60)

# --- Wykres 1: Porównanie equity curves ---
print("\n📊 Wykres 1: Porównanie equity curves (strategii)")
plot_equity_curves(
    results_dict,
    title="Buy and Hold — wpływ prowizji brokera",
    figsize=(14, 8)
)

# --- Wykres 2: Drawdown najlepszej strategii ---
print("\n📊 Wykres 2: Drawdown strategii (XTB)")
best_strategy = results_dict["XTB (0%)"]
plot_drawdown(
    best_strategy['portfolio_value'],
    title="Drawdown — Buy and Hold XTB",
    figsize=(14, 6)
)

# --- Wykres 3: Heatmapa miesięcznych zwrotów ---
print("\n📊 Wykres 3: Heatmapa miesięcznych zwrotów")
plot_monthly_returns_heatmap(
    best_strategy['portfolio_value'],
    title="Miesięczne zwroty — Buy and Hold XTB (%)",
    figsize=(14, 8)
)

# --- Wykres 4: Porównanie metryk ---
print("\n📊 Wykres 4: Porównanie metryk")
create_performance_comparison_chart(
    metrics_dict,
    title="Porównanie metryk — różni brokerzy",
    figsize=(12, 8)
)

# --- Szczegółowa tabelka w konsoli ---
print("\n📋 Szczegółowe porównanie w konsoli:")
print_detailed_comparison(results_dict, metrics_dict)

# --- Szczegółowa tabelka w konsoli ---
print("\n📋 Szczegółowe porównanie w konsoli:")
print_detailed_comparison(results_dict, metrics_dict)

# ============================================================
# DEBUG: Sprawdź szczegóły prowizji
# ============================================================
print("\n" + "=" * 60)
print("DEBUG: Szczegóły prowizji i końcowych wartości")
print("=" * 60)

for name, broker_id, account_id in configs:
    engine = BacktestEngine(broker_id, account_id, 10_000)
    results = engine.run(signals)

    print(f"\n{name}:")
    print(f"  Kapitał początkowy:  {engine.initial_capital:>12,.2f} EUR")
    print(f"  Wartość końcowa:     {engine.final_value:>12,.2f} EUR")
    print(f"  Różnica:             {engine.final_value - engine.initial_capital:>12,.2f} EUR")
    print(f"  Total Return:        {((engine.final_value / engine.initial_capital) - 1) * 100:>12.2f}%")
    print(f"  Suma prowizji:       {engine.total_commissions:>12,.2f} EUR")
    print(f"  Liczba transakcji:   {engine.num_trades:>12}")

# Test prowizji ręcznie
print(f"\n--- Test funkcji prowizji ---")
from config import calculate_commission

test_value = 10_000
brokers_test = ["xtb", "bos", "mbank", "dif"]

for broker_id in brokers_test:
    commission = calculate_commission(test_value, broker_id)
    print(f"  {broker_id:>6}: prowizja od {test_value} EUR = {commission:>8.2f} EUR")

# ============================================================
# DEBUG 2: Sprawdź metrics_dict
# ============================================================
print("\n" + "=" * 60)
print("DEBUG 2: Sprawdź zawartość metrics_dict")
print("=" * 60)

for name in metrics_dict:
    metrics = metrics_dict[name]
    print(f"\n{name}:")
    print(f"  Total Return: {metrics['Total Return']*100:.2f}%")
    print(f"  CAGR:         {metrics['CAGR']*100:.2f}%")
    print(f"  Sharpe:       {metrics['Sharpe Ratio']:.3f}")

# ============================================================
# DEBUG 3: Sprawdź equity curves
# ============================================================
print("\n" + "=" * 60)
print("DEBUG 3: Sprawdź końcowe wartości equity curves")
print("=" * 60)

for name in results_dict:
    equity_curve = results_dict[name]['portfolio_value']
    print(f"\n{name}:")
    print(f"  Equity curve długość:     {len(equity_curve)}")
    print(f"  Pierwsza wartość:         {equity_curve.iloc[0]:>12,.2f} EUR")
    print(f"  Ostatnia wartość:         {equity_curve.iloc[-1]:>12,.2f} EUR")
    print(f"  ID obiektu w pamięci:     {id(equity_curve)}")
    print(f"  Maksymalna wartość:       {equity_curve.max():>12,.2f} EUR")

# ============================================================
# DEBUG 4: Sprawdź funkcję total_return krok po kroku
# ============================================================
print("\n" + "=" * 60)
print("DEBUG 4: Ręczne obliczenie Total Return")
print("=" * 60)

from metrics import total_return

for name in results_dict:
    equity_curve = results_dict[name]['portfolio_value']

    start_value = equity_curve.iloc[0]
    end_value = equity_curve.iloc[-1]
    calculated_return = (end_value / start_value) - 1
    function_return = total_return(equity_curve)

    print(f"\n{name}:")
    print(f"  Start value:    {start_value:>12,.2f} EUR")
    print(f"  End value:      {end_value:>12,.2f} EUR")
    print(f"  Ręczny total:   {calculated_return * 100:>12.2f}%")
    print(f"  Funkcja total:  {function_return * 100:>12.2f}%")
    print(f"  Czy identyczne: {abs(calculated_return - function_return) < 0.0001}")

print("\n🎉 Wszystkie wizualizacje gotowe!")
print("\n💡 Wnioski:")
print("   • XTB (bez prowizji) daje najlepsze wyniki")
print("   • Różnica między brokerami jest niewielka (Buy and Hold robi mało transakcji)")
print("   • Max drawdown ~34% — to sporo, ale typowe dla akcji")
print("   • CAGR ~12-13% to bardzo dobry wynik długoterminowy")