import pandas as pd
import urllib.request
import ssl
import certifi
import yfinance as yf
from ta.trend import WMAIndicator
from datetime import datetime
import io

# =========================================================
# CONFIGURACIÓN GLOBAL
# =========================================================

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9",
}

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


# =========================================================
# UTILIDADES
# =========================================================

def fetch_tables(url: str) -> list[pd.DataFrame]:
    req = urllib.request.Request(url, headers=HEADERS)
    html_bytes = urllib.request.urlopen(req, context=SSL_CONTEXT).read()

    # ✅ Convertir bytes → texto → buffer (evita FileNotFoundError en Cloud)
    html_str = html_bytes.decode("utf-8", errors="ignore")
    return pd.read_html(io.StringIO(html_str), flavor="lxml")


# =========================================================
# UNIVERSO DE TICKERS
# =========================================================

def load_universe() -> pd.DataFrame:
    # ---------- S&P 500 ----------
    sp500 = fetch_tables(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    )[0][["Symbol", "Security", "GICS Sector", "GICS Sub-Industry"]].copy()

    sp500.columns = [
        "Ticker",
        "Company",
        "GICS Sector",
        "GICS Sub-Industry",
    ]

    # ---------- NASDAQ-100 (detección dinámica) ----------
    nasdaq_tables = fetch_tables(
        "https://en.wikipedia.org/wiki/NASDAQ-100"
    )

    nasdaq = next(
        t for t in nasdaq_tables
        if (
            {"Ticker", "Company"} <= set(t.columns)
            or {"Symbol", "Security"} <= set(t.columns)
        )
    ).iloc[:, :2].copy()

    nasdaq.columns = ["Ticker", "Company"]
    nasdaq.loc[:, "GICS Sector"] = "Unknown"
    nasdaq.loc[:, "GICS Sub-Industry"] = "Unknown"

    # ---------- COMBINAR ----------
    universe = pd.concat([sp500, nasdaq], ignore_index=True)

    universe["Ticker"] = universe["Ticker"].str.replace(".", "-", regex=False)

    return (
        universe
        .drop_duplicates(subset="Ticker")
        .sort_values("Ticker")
        .reset_index(drop=True)
    )


# =========================================================
# CÁLCULO RSC
# =========================================================

def calculate_rsc() -> pd.DataFrame:
    universe = load_universe()
    tickers = universe["Ticker"].tolist()

    # --- PRECIOS ACCIONES (mensual) ---
    prices = yf.download(
        tickers,
        period="5y",
        interval="1mo",
        group_by="ticker",
        threads=True,
        auto_adjust=False,
    )

    # --- SP500 FUTURE ---
    sp = (
        yf.download(
            "ES=F",
            period="5y",
            interval="1d",
            auto_adjust=False,
        )["Close"]
        .resample("ME")
        .last()
    )

    results = []

    for t in tickers:
        try:
            close = prices[t]["Close"].dropna()
            if close.empty:
                continue

            df = pd.DataFrame({"Close": close})
            df["ES"] = sp.shift(-1).reindex(df.index, method="ffill")

            df["R"] = df["Close"] / df["ES"]
            df["Base"] = df["R"].rolling(10).mean()
            df["RSC0"] = (df["R"] / df["Base"] - 1) * 10
            df["RSCValor"] = WMAIndicator(df["RSC0"], window=8).wma()

            results.append({
                "Ticker": t,
                "Close": round(df["Close"].iloc[-1], 2),
                "RSCValor": round(df["RSCValor"].iloc[-1], 4),
            })

        except Exception:
            pass

    rsc = pd.DataFrame(results).merge(universe, on="Ticker", how="left")
    rsc["Date"] = datetime.now().strftime("%Y-%m-%d")

    return rsc.sort_values("RSCValor", ascending=False)
