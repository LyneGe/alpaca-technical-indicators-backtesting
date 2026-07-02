import argparse
from pathlib import Path
from dotenv import load_dotenv

from src.data import download_ohlcv
from src.indicators import add_indicators
from src.strategies import buy_and_hold, trend_following, mean_reversion, custom_strategy
from src.backtester import Backtester
from src.metrics import metrics_table
from src.plots import plot_price_signals, plot_equity_curves, plot_drawdowns
from src.report import build_report


def main():
    parser = argparse.ArgumentParser(description="Alpaca technical indicator strategy backtester")
    parser.add_argument("--ticker", type=str, default="AAPL", help="Ticker symbol, e.g. AAPL, MSFT, SPY, QQQ, NVDA")
    parser.add_argument("--years", type=int, default=5, help="Number of years of daily data")
    parser.add_argument("--initial_capital", type=float, default=100000, help="Initial capital")
    args = parser.parse_args()

    load_dotenv()
    ticker = args.ticker.upper()
    output_dir = Path("charts") / ticker
    report_dir = Path("reports")
    report_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {args.years}+ years of daily data for {ticker} from Alpaca...")
    raw = download_ohlcv(ticker, years=args.years)
    data = add_indicators(raw)
    data.to_csv(f"{ticker}_ohlcv_indicators.csv")

    bt = Backtester(data, initial_capital=args.initial_capital)
    results = [
        bt.run("Buy & Hold", buy_and_hold(data)),
        bt.run("Trend Following", trend_following(data)),
        bt.run("Mean Reversion", mean_reversion(data)),
        bt.run("Custom Strategy", custom_strategy(data)),
    ]

    metrics = metrics_table(results)
    metrics.to_csv(report_dir / f"{ticker}_performance_metrics.csv", index=False)

    chart_paths = []
    # Requirement asks price chart with indicators and buy/sell signals. Use all active strategies.
    for result in results[1:]:
        chart_paths.append(plot_price_signals(data, result, output_dir))
    chart_paths.append(plot_equity_curves(results, output_dir))
    chart_paths.append(plot_drawdowns(results, output_dir))

    for result in results:
        if not result.trades.empty:
            result.trades.to_csv(report_dir / f"{ticker}_{result.name.replace(' ', '_').replace('&', 'and')}_trades.csv", index=False)

    report_path = build_report(ticker, metrics, chart_paths, report_dir / f"{ticker}_final_report.pdf")

    print("\nPerformance Table:")
    print(metrics.to_string(index=False))
    print(f"\nSaved charts to: {output_dir}")
    print(f"Saved PDF report to: {report_path}")


if __name__ == "__main__":
    main()
