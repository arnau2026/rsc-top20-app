from glob import glob
from datetime import datetime

import pandas as pd
import yfinance as yf
from ta.trend import WMAIndicator


def calcular_rsc():

    sp500_file = glob("sp-500-index*.csv")[0]
    nasdaq100_file = glob("nasdaq-100-index*.csv")[0]

    sp500 = pd.read_csv(sp500_file).iloc[:-1]
    nasdaq100 = pd.read_csv(nasdaq100_file).iloc[:-1]

    combined = pd.concat([sp500, nasdaq100])

    combined = combined.rename(columns={
        "Symbol": "Ticker",
        "Name": "Company",
        "Sector": "GICS Sector",
        "Industry": "GICS Sub-Industry"
    })

    combined = combined[[
        "Ticker",
        "Company",
        "GICS Sector",
        "GICS Sub-Industry"
    ]]

    combined["Ticker"] = combined["Ticker"].str.replace(".", "-", regex=False)

    combined = (
        combined
        .drop_duplicates("Ticker")
        .sort_values("Ticker")
        .reset_index(drop=True)
    )

    tickers = combined["Ticker"].tolist()

    data_stocks = yf.download(
        tickers,
        period="5y",
        interval="1mo",
        auto_adjust=False,
        group_by="ticker",
        progress=False
    )

    data_fut_daily = yf.download(
        "ES=F",
        period="5y",
        interval="1d",
        progress=False
    )["Close"]

    data_fut = data_fut_daily.resample("ME").last().dropna()

    period = 10
    m = 8

    resultados = []

    for ticker in tickers:

        try:

            close = data_stocks[ticker]["Close"].dropna()

            if close.empty:
                continue

            df = pd.DataFrame({"Close": close})

            df["ES_Close"] = data_fut.shift(-1).reindex(df.index, method="ffill")

            df["Cociente"] = df["Close"] / df["ES_Close"]
            df["CountR"] = df["Cociente"].rolling(period).sum()
            df["Baseprice"] = df["CountR"] / period
            df["RSCValor0"] = ((df["Cociente"] / df["Baseprice"]) - 1) * 10
            df["RSCValor"] = WMAIndicator(df["RSCValor0"], window=m).wma()

            last = df.iloc[-1]

            resultados.append({
                "Ticker": ticker,
                "Date": datetime.today().strftime("%Y-%m-%d"),
                "Company": combined.loc[
                    combined.Ticker == ticker,
                    "Company"
                ].values[0],
                "Close": round(last["Close"],2),
                "RSCValor": round(last["RSCValor"],4),
                "GICS Sector": combined.loc[
                    combined.Ticker == ticker,
                    "GICS Sector"
                ].values[0],
                "GICS Sub-Industry": combined.loc[
                    combined.Ticker == ticker,
                    "GICS Sub-Industry"
                ].values[0],
            })

        except:
            pass

    ranking = pd.DataFrame(resultados)

    ranking = ranking.sort_values(
        "RSCValor",
        ascending=False
    )

    return ranking