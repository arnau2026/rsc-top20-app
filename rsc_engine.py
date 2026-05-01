# rsc_engine.py
import pandas as pd
import yfinance as yf
from ta.trend import WMAIndicator
from datetime import datetime

def calculate_top20(input_file="Inputfile.xlsx"):

    combined = pd.read_excel(input_file, engine="openpyxl")
    combined.columns = ["Ticker", "Company", "GICS Sector", "GICS Sub-Industry"]
    combined["Ticker"] = combined["Ticker"].str.replace(".", "-", regex=False)
    combined = combined.drop_duplicates("Ticker").sort_values("Ticker")

    tickers = combined["Ticker"].tolist()

    data_stocks = yf.download(
        tickers, period="5y", interval="1mo", group_by="ticker"
    )
    data_fut = (
        yf.download("ES=F", period="5y", interval="1d")["Close"]
        .resample("ME").last()
    )

    rsc_results = []
    for ticker in tickers:
        try:
            close = data_stocks[ticker]["Close"].dropna()
            df = pd.DataFrame({"Close": close})
            df["ES_Close"] = data_fut.shift(-1).reindex(df.index, method="ffill")

            df["Cociente"] = df["Close"] / df["ES_Close"]
            df["Baseprice"] = df["Cociente"].rolling(10).mean()
            df["RSC0"] = ((df["Cociente"] / df["Baseprice"]) - 1) * 10
            df["RSC"] = WMAIndicator(df["RSC0"], window=8).wma()

            last = df.iloc[-1]
            rsc_results.append({
                "Ticker": ticker,
                "Close": round(last["Close"], 2),
                "RSCValor": round(last["RSC"], 4)
            })
        except:
            pass

    rsc_df = pd.DataFrame(rsc_results).merge(combined, on="Ticker")
    rsc_df["Date"] = datetime.now().strftime("%Y-%m-%d")

    return rsc_df.sort_values("RSCValor", ascending=False).head(20)