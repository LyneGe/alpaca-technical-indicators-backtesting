import numpy as np
import pandas as pd
from .backtester import BacktestResult


def max_drawdown(equity: pd.Series) -> float:
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    return drawdown.min()


def drawdown_series(equity: pd.Series) -> pd.Series:
    return equity / equity.cummax() - 1


def performance_metrics(result: BacktestResult, risk_free_rate: float = 0.0) -> dict:
    r = result.daily_returns.dropna()
    equity = result.equity.dropna()
    years = len(equity) / 252

    total_return = equity.iloc[-1] / equity.iloc[0] - 1
    cagr = (equity.iloc[-1] / equity.iloc[0]) ** (1 / years) - 1 if years > 0 else np.nan
    volatility = r.std() * np.sqrt(252)
    excess_daily = r - risk_free_rate / 252
    sharpe = (excess_daily.mean() * 252) / volatility if volatility != 0 else np.nan

    downside = r[r < 0]
    downside_vol = downside.std() * np.sqrt(252)
    sortino = (excess_daily.mean() * 252) / downside_vol if downside_vol != 0 else np.nan

    sells = result.trades[result.trades["action"] == "SELL"] if not result.trades.empty else pd.DataFrame()
    win_rate = (sells["trade_return"] > 0).mean() if not sells.empty and "trade_return" in sells else np.nan

    return {
        "Strategy": result.name,
        "Total Return": total_return,
        "CAGR": cagr,
        "Volatility": volatility,
        "Sharpe Ratio": sharpe,
        "Sortino Ratio": sortino,
        "Max Drawdown": max_drawdown(equity),
        "Win Rate": win_rate,
        "Trades": int((result.trades["action"] == "BUY").sum()) if not result.trades.empty else 0,
    }


def metrics_table(results: list[BacktestResult]) -> pd.DataFrame:
    table = pd.DataFrame([performance_metrics(r) for r in results])
    return table
