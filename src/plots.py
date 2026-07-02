from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from .metrics import drawdown_series


def plot_price_signals(df: pd.DataFrame, result, output_dir: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    buys = result.trades[result.trades["action"] == "BUY"] if not result.trades.empty else pd.DataFrame()
    sells = result.trades[result.trades["action"] == "SELL"] if not result.trades.empty else pd.DataFrame()

    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["close"], label="Close")
    plt.plot(df.index, df["sma_20"], label="SMA 20")
    plt.plot(df.index, df["sma_50"], label="SMA 50")
    if not buys.empty:
        plt.scatter(buys["date"], buys["price"], marker="^", label="Buy")
    if not sells.empty:
        plt.scatter(sells["date"], sells["price"], marker="v", label="Sell")
    plt.title(f"Price Chart with Signals - {result.name}")
    plt.xlabel("Date")
    plt.ylabel("Price")
    plt.legend()
    plt.tight_layout()
    path = Path(output_dir) / f"price_signals_{safe_name(result.name)}.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_equity_curves(results, output_dir: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 6))
    for r in results:
        plt.plot(r.equity.index, r.equity, label=r.name)
    plt.title("Equity Curve Comparison")
    plt.xlabel("Date")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.tight_layout()
    path = Path(output_dir) / "equity_curves.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def plot_drawdowns(results, output_dir: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(12, 6))
    for r in results:
        dd = drawdown_series(r.equity)
        plt.plot(dd.index, dd, label=r.name)
    plt.title("Drawdown Comparison")
    plt.xlabel("Date")
    plt.ylabel("Drawdown")
    plt.legend()
    plt.tight_layout()
    path = Path(output_dir) / "drawdowns.png"
    plt.savefig(path, dpi=150)
    plt.close()
    return path


def safe_name(name: str) -> str:
    return name.lower().replace(" & ", "_").replace(" ", "_")
