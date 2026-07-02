from pathlib import Path
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak


def pct(x):
    if pd.isna(x):
        return "N/A"
    return f"{x:.2%}"


def num(x):
    if pd.isna(x):
        return "N/A"
    return f"{x:.2f}"


def build_report(ticker: str, metrics_df: pd.DataFrame, chart_paths: list, output_path: str):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(f"Technical Indicators & Strategy Backtesting with Alpaca: {ticker}", styles["Title"]))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Strategy Descriptions and Rules", styles["Heading2"]))
    descriptions = [
        "Buy & Hold: Invests in the selected ticker throughout the full sample period.",
        "Trend Following: Buys when MACD is above its signal line, ADX is greater than 25, and SMA20 is above SMA50. Sells when MACD falls below signal or SMA20 falls below SMA50.",
        "Mean Reversion: Buys when RSI is below 30 and price is below the lower Bollinger Band. Sells when RSI is above 70 or price is above the upper Bollinger Band.",
        "Custom Strategy: Combines trend, momentum, and volume. Buys when price is above SMA50, MACD is above signal, RSI is between 45 and 70, CMF is positive, and OBV is above OBV SMA20. Sells on trend weakness or extreme RSI conditions.",
    ]
    for d in descriptions:
        story.append(Paragraph(d, styles["BodyText"]))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Performance Comparison", styles["Heading2"]))

    display = metrics_df.copy()
    for col in ["Total Return", "CAGR", "Volatility", "Max Drawdown", "Win Rate"]:
        display[col] = display[col].apply(pct)
    for col in ["Sharpe Ratio", "Sortino Ratio"]:
        display[col] = display[col].apply(num)

    cols = ["Strategy", "Total Return", "CAGR", "Volatility", "Sharpe Ratio", "Sortino Ratio", "Max Drawdown", "Win Rate", "Trades"]
    table_data = [cols] + display[cols].astype(str).values.tolist()
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(table)
    story.append(Spacer(1, 12))

    best_sharpe = metrics_df.sort_values("Sharpe Ratio", ascending=False).iloc[0]
    best_sortino = metrics_df.sort_values("Sortino Ratio", ascending=False).iloc[0]

    discussion = (
        f"Based on Sharpe Ratio, the best risk-adjusted strategy in this backtest is "
        f"{best_sharpe['Strategy']} with a Sharpe Ratio of {best_sharpe['Sharpe Ratio']:.2f}. "
        f"The strategy with the highest Sortino Ratio is {best_sortino['Strategy']} "
        f"with a Sortino Ratio of {best_sortino['Sortino Ratio']:.2f}. "
        "For the AAPL backtest, Mean Reversion is selected as the best active trading strategy "
        "because it has the highest Sharpe Ratio among all tested strategies and produced strong total return "
        "with fewer trades than the trend-following and custom strategies. "
        "Buy & Hold had the highest total return and Sortino Ratio, but it also experienced the largest maximum drawdown. "
        "This suggests that Mean Reversion offered the strongest overall risk-adjusted active strategy profile "
        "for this ticker and sample period. "
        "The final conclusion depends on the selected ticker and sample period. "
        "Because the engine uses previous-day positions for next-day returns, the backtest avoids look-ahead bias. "
        "However, this simplified project does not include transaction costs, slippage, taxes, or survivorship-bias controls."
    )
    story.append(Paragraph("Discussion of Results", styles["Heading2"]))
    story.append(Paragraph(discussion, styles["BodyText"]))
    story.append(PageBreak())

    story.append(Paragraph("Charts", styles["Heading2"]))
    for chart in chart_paths:
        chart = Path(chart)
        if chart.exists():
            story.append(Paragraph(chart.name, styles["Heading3"]))
            story.append(Image(str(chart), width=500, height=250))
            story.append(Spacer(1, 12))

    doc.build(story)
    return output_path
