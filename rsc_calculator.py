from glob import glob
from datetime import datetime

import pandas as pd
import yfinance as yf
from ta.trend import WMAIndicator


def calcular_rsc(callback=None):

    if callback:
        callback(5, "Leyendo índices...")

    sp500_files = glob("sp-500-index*.csv")
    nasdaq_files = glob("nasdaq-100-index*.csv")

    if not sp500_files:
        raise FileNotFoundError(
            "No se encontró sp-500-index*.csv"
        )

    if not nasdaq_files:
        raise FileNotFoundError(
            "No se encontró nasdaq-100-index*.csv"
        )

    sp500_file = sp500_files[0]
    nasdaq100_file = nasdaq_files[0]

    sp500 = pd.read_csv(sp500_file).iloc[:-1]
    nasdaq100 = pd.read_csv(nasdaq100_file).iloc[:-1]

    combined = pd.concat([sp500, nasdaq100])

    combined = combined.rename(columns={
        "Symbol": "Ticker",
        "Name": "Company",
        "Sector": "GICS Sector",
        "Industry": "GICS Sub-Industry"
    })

    combined = combined[
        [
            "Ticker",
            "Company",
            "GICS Sector",
            "GICS Sub-Industry"
        ]
    ]

    combined["Ticker"] = (
        combined["Ticker"]
        .str.replace(".", "-", regex=False)
    )

    combined = (
        combined
        .drop_duplicates("Ticker")
        .sort_values("Ticker")
        .reset_index(drop=True)
    )

    tickers = combined["Ticker"].tolist()

    if callback:
        callback(
            10,
            f"Descargando datos ({len(tickers)} tickers)..."
        )

    data_stocks = yf.download(
        tickers,
        period="5y",
        interval="1mo",
        auto_adjust=False,
        group_by="ticker",
        progress=False
    )

    if callback:
        callback(
            40,
            "Descargando futuro S&P500..."
        )

    data_fut_daily = yf.download(
        "ES=F",
        period="5y",
        interval="1d",
        progress=False
    )["Close"]

    data_fut = (
        data_fut_daily
        .resample("ME")
        .last()
        .dropna()
    )

    period = 10
    m = 8

    resultados = []

    total = len(tickers)

    info_tickers = (
        combined
        .set_index("Ticker")
        .to_dict("index")
    )

    if callback:
        callback(
            50,
            "Procesando RSC..."
        )

    for i, ticker in enumerate(tickers):

        try:

            if ticker not in info_tickers:
                continue

            close = (
                data_stocks[ticker]["Close"]
                .dropna()
            )

            if close.empty:
                continue

            df = pd.DataFrame({
                "Close": close
            })

            df["ES_Close"] = (
                data_fut
                .shift(-1)
                .reindex(
                    df.index,
                    method="ffill"
                )
            )

            df["Cociente"] = (
                df["Close"] /
                df["ES_Close"]
            )

            df["CountR"] = (
                df["Cociente"]
                .rolling(period)
                .sum()
            )

            df["Baseprice"] = (
                df["CountR"] /
                period
         