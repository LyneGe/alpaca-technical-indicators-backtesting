from dataclasses import dataclass
import pandas as pd


@dataclass
class BacktestResult:
    name: str
    equity: pd.Series
    daily_returns: pd.Series
    position: pd.Series
    trades: pd.DataFrame


class Backtester:
    def __init__(self, data: pd.DataFrame, initial_capital: float = 100000):
        self.data = data.copy()
        self.initial_capital = initial_capital

    def run(self, name: str, position: pd.Series) -> BacktestResult:
        close = self.data["close"]
        position = position.reindex(close.index).fillna(0).astype(int)

        # Use yesterday's position for today's return to avoid look-ahead bias.
        asset_returns = close.pct_change().fillna(0)
        strategy_returns = position.shift(1).fillna(0) * asset_returns
        equity = self.initial_capital * (1 + strategy_returns).cumprod()
        equity.name = name

        trades = self._extract_trades(name, close, position)
        return BacktestResult(name, equity, strategy_returns, position, trades)

    def _extract_trades(self, name: str, close: pd.Series, position: pd.Series) -> pd.DataFrame:
        changes = position.diff().fillna(position.iloc[0])
        rows = []
        entry_date = None
        entry_price = None

        for date, change in changes.items():
            if change == 1:
                entry_date = date
                entry_price = close.loc[date]
                rows.append({"strategy": name, "date": date, "action": "BUY", "price": entry_price})
            elif change == -1 and entry_date is not None:
                exit_price = close.loc[date]
                rows.append({"strategy": name, "date": date, "action": "SELL", "price": exit_price,
                             "entry_date": entry_date, "entry_price": entry_price,
                             "trade_return": exit_price / entry_price - 1})
                entry_date = None
                entry_price = None

        return pd.DataFrame(rows)
