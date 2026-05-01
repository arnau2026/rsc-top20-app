import pandas as pd
import yfinance as yf
from ta.trend import WMAIndicator
from datetime import datetime

# =========================================================
# UNIVERSO AUTOMÁTICO: S&P 500 + NASDAQ-100
# =========================================================

def load_universe():
    url_sp500 = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    sp500 = pd.read_html(url_sp500)[0]

    sp500_df = sp500[["Symbol", "Security", "GICS Sector", "GICS Sub-Industry"]]
    sp500_df["Symbol"] = sp500_df["Symbol"].str.replace(".", "-", regex=False)
    sp500_df.columns = ["Ticker", "Company", "Sector", "Industry"]

    url_ndx = "https://en.wikipedia.org/wiki/Nasdaq-100"
    nasdaq = pd.read_html(url_ndx)[4]

    nasdaq_df = nasdaq[["Ticker", "Company"]]
    nasdaq_df["Sector"] = "Unknown"
    nasdaq_df["Industry"] = "Unknown"

    universe = pd.concat([sp500_df, nasdaq_df], ignore_index=True)
    universe = universe.drop_duplicates(subset="Ticker")

    return universe


# =========================================================
# TOP 20 RSC
# =========================================================

def calculate_top20():
    universe = load_universe()
    tickers = universe["Ticker"].tolist()

    prices = yf.download(
        tickers,
        period="5y",
        interval="1mo",
        group_by="ticker",
        threads=True
    )

    sp500 = yf.download("ES=F", period="5y", interval="1d")["Close"]
    sp500 = sp500.resample("ME").last()

    results = []
    base_period = 10
    smooth = 8

    for ticker in tickers:
        try:
            close = prices[ticker]["Close"].dropna()
            if close.empty:
                continue

            df = pd.DataFrame({"Close": close})
            df["SP"] = sp500.reindex(df.index, method="ffill")
            df["Ratio"] = df["Close"] / df["SP"]
            df["Base"] = df["Ratio"].rolling(base_period).mean()
            df["RSC0"] = (df["Ratio"] / df["Base"] - 1) * 10
            df["RSC"] = WMAIndicator(df["RSC0"], window=smooth).wma()

            last = df.iloc[-1]
            results.append({
                "Ticker": ticker,
                "Price": round(last["Close"], 2),
                "RSC": round(last["RSC"], 4),
            })

        except Exception:
            continue

    rsc = pd.DataFrame(results)
    rsc = rsc.merge(universe, on="Ticker", how="left")
    rsc["Date"] = datetime.now().strftime("%Y-%m-%d")

    return rsc.sort_values("RSC", ascending=False).head(20)