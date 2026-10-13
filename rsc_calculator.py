from glob import glob
from datetime import datetime
import pandas as pd
import yfinance as yf
from ta.trend import WMAIndicator

PERIOD = 10
WMA_WINDOW = 4
BENCHMARK = "SPY"


def _clean_series(series):
    series = pd.to_numeric(series, errors="coerce").dropna()
    series.index = pd.to_datetime(series.index).tz_localize(None)
    return series


def _extract_close(data, ticker):
    if data is None or data.empty:
        return pd.Series(dtype=float)
    try:
        if isinstance(data.columns, pd.MultiIndex):
            if ticker in data.columns.get_level_values(0):
                close = data[ticker]["Close"]
            elif ticker in data.columns.get_level_values(1):
                close = data.xs(ticker, axis=1, level=1)["Close"]
            else:
                return pd.Series(dtype=float)
        else:
            close = data["Close"]
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        return _clean_series(close)
    except Exception:
        return pd.Series(dtype=float)


def _download_monthly(tickers):
    return yf.download(
        tickers,
        period="1y",
        interval="1mo",
        auto_adjust=False,
        group_by="ticker",
        threads=True,
        progress=False,
    )


def _benchmark_monthly():
    data = yf.download(
        BENCHMARK,
        period="1y",
        interval="1d",
        auto_adjust=False,
        progress=False,
    )
    close = data["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    return _clean_series(close).resample("ME").last().dropna()


def _last_rsc(close, benchmark):
    if close.empty or benchmark.empty:
        return None
    df = pd.DataFrame({"Close": close})
    df["ES_Close"] = benchmark.shift(-1).reindex(df.index, method="ffill")
    ratio = df["Close"] / df["ES_Close"]
    baseprice = ratio.rolling(PERIOD).mean()
    raw_rsc = ((ratio / baseprice) - 1) * 10
    df["RSCValor"] = WMAIndicator(raw_rsc, window=WMA_WINDOW).wma()
    valid = df.dropna(subset=["Close", "RSCValor"])
    return None if valid.empty else valid.iloc[-1]


def calcular_rsc():
    sp500 = pd.read_csv(glob("sp-500-index*.csv")[0]).iloc[:-1]
    nasdaq100 = pd.read_csv(glob("nasdaq-100-index*.csv")[0]).iloc[:-1]
    universe = pd.concat([sp500, nasdaq100], ignore_index=True).rename(columns={
        "Symbol": "Ticker",
        "Name": "Company",
        "Sector": "GICS Sector",
        "Industry": "GICS Sub-Industry",
    })[["Ticker", "Company", "GICS Sector", "GICS Sub-Industry"]]
    universe["Ticker"] = universe["Ticker"].astype(str).str.replace(".", "-", regex=False)
    universe = universe.drop_duplicates("Ticker").reset_index(drop=True)

    prices = _download_monthly(universe["Ticker"].tolist())
    benchmark = _benchmark_monthly()
    rows = []
    for _, item in universe.iterrows():
        last = _last_rsc(_extract_close(prices, item["Ticker"]), benchmark)
        if last is None:
            continue
        rows.append({
            "Ticker": item["Ticker"],
            "Date": datetime.today().strftime("%Y-%m-%d"),
            "Company": item["Company"],
            "Close": round(float(last["Close"]), 2),
            "RSCValor": round(float(last["RSCValor"]), 4),
            "GICS Sector": item["GICS Sector"],
            "GICS Sub-Industry": item["GICS Sub-Industry"],
        })
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows).sort_values("RSCValor", ascending=False).reset_index(drop=True)


def calcular_rsc_etf(excel_file="ETF UCITS.xlsx"):
    etfs = pd.read_excel(excel_file, engine="openpyxl")
    etfs.columns = [str(c).strip() for c in etfs.columns]

    ticker_col = etfs.columns[0]
    etfs[ticker_col] = etfs[ticker_col].astype(str).str.strip().str.lstrip("$")
    if ticker_col != "Ticker":
        etfs = etfs.rename(columns={ticker_col: "Ticker"})

    tickers = etfs["Ticker"].dropna().drop_duplicates().tolist()
    prices = _download_monthly(tickers)
    benchmark = _benchmark_monthly()
    rows = []

    for _, item in etfs.iterrows():
        last = _last_rsc(_extract_close(prices, item["Ticker"]), benchmark)
        row = item.to_dict()
        row["Date"] = datetime.today().strftime("%Y-%m-%d")
        if last is None:
            row["Close"] = pd.NA
            row["RSCValor"] = pd.NA
        else:
            row["Close"] = round(float(last["Close"]), 2)
            row["RSCValor"] = round(float(last["RSCValor"]), 4)
        rows.append(row)

    result = pd.DataFrame(rows)
    result["RSCValor"] = pd.to_numeric(result["RSCValor"], errors="coerce")
    return result.sort_values("RSCValor", ascending=False, na_position="last").reset_index(drop=True)
