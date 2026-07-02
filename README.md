# Technical Indicators & Strategy Backtesting with Alpaca

This project downloads historical daily OHLCV market data from Alpaca, calculates technical indicators, backtests multiple long-only trading strategies, compares performance metrics, generates charts, and creates a final PDF report.

## Strategies

1. **Buy & Hold** baseline
2. **Trend Following** using MACD, ADX, SMA20, and SMA50
3. **Mean Reversion** using RSI and Bollinger Bands
4. **Custom Strategy** using trend, momentum, and volume indicators: SMA, MACD, RSI, CMF, and OBV

## Technical Indicators Implemented

- SMA
- EMA
- MACD
- ADX
- RSI
- Stochastic Oscillator
- Williams %R
- Bollinger Bands
- ATR
- OBV
- Chaikin Money Flow

This satisfies the requirement of at least 6 indicators and includes indicators from trend, momentum, volatility, and volume categories.

## Assumptions

- Initial capital: `$100,000`
- Long-only
- No leverage
- No short selling
- No transaction costs or slippage
- Uses previous-day position for next-day returns to avoid look-ahead bias

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```bash
ALPACA_API_KEY=your_key_here
ALPACA_SECRET_KEY=your_secret_here
```

## Run

```bash
python run_backtest.py --ticker AAPL
```

Other examples:

```bash
python run_backtest.py --ticker MSFT
python run_backtest.py --ticker SPY
python run_backtest.py --ticker QQQ
python run_backtest.py --ticker NVDA
```

## Outputs

After running, the project creates:

- `charts/<TICKER>/price_signals_*.png`
- `charts/<TICKER>/equity_curves.png`
- `charts/<TICKER>/drawdowns.png`
- `reports/<TICKER>_performance_metrics.csv`
- `reports/<TICKER>_final_report.pdf`
- `<TICKER>_ohlcv_indicators.csv`

## Repository Contents

```text
.
├── README.md
├── requirements.txt
├── .env.example
├── run_backtest.py
├── src/
│   ├── data.py
│   ├── indicators.py
│   ├── strategies.py
│   ├── backtester.py
│   ├── metrics.py
│   ├── plots.py
│   └── report.py
├── charts/
└── reports/
```

## Final Report

The final PDF report is automatically generated after running the script. It includes:

- Strategy descriptions
- Entry and exit rules
- Performance comparison table
- Discussion of results
- Price/signal charts
- Equity curve comparison
- Drawdown comparison

## Video Submission Suggestion

A short video can show:

1. The GitHub repository structure
2. The `.env` setup without revealing the key values
3. Running `python run_backtest.py --ticker AAPL`
4. The generated charts
5. The generated final PDF report
