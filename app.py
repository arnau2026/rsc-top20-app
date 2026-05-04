import streamlit as st
import pandas as pd
from rsc_engine import calculate_rsc

# --- Tiempo ---
from datetime import datetime
import pytz

# --- Datos y gráficos ---
import yfinance as yf
import matplotlib.pyplot as plt
from ta.trend import WMAIndicator
from matplotlib.dates import MonthLocator, DateFormatter

# ==================================================
# CONFIGURACIÓN GENERAL
# ==================================================

st.set_page_config(
    page_title="Acciones USA – RSC & Salud de Mercado",
    layout="wide",
)

# ==================================================
# FECHA Y HORA (ESPAÑA REAL ✅)
# ==================================================

tz = pytz.timezone("Europe/Madrid")
now = datetime.now(tz)

fecha = now.strftime("%Y-%m-%d")
hora = now.strftime("%H:%M")

st.title(f"📈 Acciones USA ordenadas a día {fecha} y hora {hora}")

# ==================================================
# CÁLCULO RSC
# ==================================================

@st.cache_data(ttl=24 * 3600)
def get_rsc():
    return calculate_rsc()

with st.spinner("Calculando ranking RSC..."):
    df = get_rsc()

# ==================================================
# LIMPIEZA Y RANKING
# ==================================================

df = df.reset_index(drop=True)
df.insert(0, "Rank", range(1, len(df) + 1))

# ==================================================
# TICKER COMO LINK A TRADINGVIEW ✅
# ==================================================

df["Ticker"] = df["Ticker"].apply(
    lambda x: f'<a href="https://www.tradingview.com/chart/?symbol={x}" '
              f'target="_blank" style="color:#1f4fff;font-weight:600;">{x}</a>'
)

# ==================================================
# ESTILO – TOP 8 EN VERDE (DARK MODE SAFE)
# ==================================================

def highlight_top8(row):
    if row["Rank"] <= 8:
        return [
            "background-color: #1f7a1f; color: #ffffff; font-weight: 600"
        ] * len(row)
    return [""] * len(row)

# ✅ AQUÍ ESTÁ LA CLAVE DEFINITIVA: .hide(axis="index")
styled_df = (
    df[
        [
            "Rank",
            "Ticker",
            "Date",
            "Company",
            "Close",
            "RSCValor",
            "GICS Sector",
            "GICS Sub-Industry",
        ]
    ]
    .style
    .apply(highlight_top8, axis=1)
    .hide(axis="index")   # 🔥 elimina para siempre la columna fantasma
)

# ==================================================
# MOSTRAR RANKING
# ==================================================

st.subheader("🏆 Ranking completo de acciones USA (RSC)")

st.write(
    styled_df.to_html(escape=False),
    unsafe_allow_html=True
)

# ==================================================
# DESCARGA CSV (SIN HTML)
# ==================================================

st.download_button(
    "⬇️ Descargar todas las acciones (CSV)",
    df.assign(Ticker=df["Ticker"].str.replace(r"<.*?>", "", regex=True))
      .to_csv(index=False)
      .encode("utf-8"),
    file_name=f"acciones_usa_rsc_{fecha}_{hora.replace(':','')}.csv",
    mime="text/csv",
)

# ==================================================
# SALUD DE MERCADO – GUÍA COPPOCK
# ==================================================

st.markdown("---")
st.subheader("🩺 Salud del mercado – Guía Coppock (S&P 500)")

@st.cache_data(ttl=24 * 3600)
def plot_coppock_market_health():
    R1, R2, med = 16, 14, 10

    data_daily = yf.download(
        "ES=F",
        period="8y",
        interval="1d",
        auto_adjust=False,
    )["Close"].squeeze()

    data_monthly = data_daily.resample("ME").last().dropna()

    roc1 = data_monthly.pct_change(R1) * 100
    roc2 = data_monthly.pct_change(R2) * 100
    roc_sum = roc1 + roc2

    coppock = WMAIndicator(roc_sum, window=med).wma()

    df_c = pd.concat([data_monthly, coppock], axis=1).dropna()
    df_c.columns = ["ES=F", "Coppock"]

    cond_mejora = (df_c["Coppock"] >= 0) | (df_c["Coppock"] > df_c["Coppock"].shift(1))

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

    ax1.plot(df_c.index, df_c["ES=F"], color="black")
    ax1.set_title("S&P 500 (ES=F) – Mensual")
    ax1.grid(True)

    ax2.plot(df_c.index, df_c["Coppock"], color="blue")
    ax2.axhline(0, color="gray", linestyle="--")

    ax2.fill_between(
        df_c.index,
        df_c["Coppock"],
        0,
        where=cond_mejora,
        color="green",
        alpha=0.3,
        label="Régimen favorable"
    )

    ax2.set_title("Guía Coppock – Salud de mercado")
    ax2.grid(True)
    ax2.legend()

    ax2.xaxis.set_major_locator(MonthLocator(interval=3))
    ax2.xaxis.set_major_formatter(DateFormatter("%Y-%m"))
    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")

    plt.tight_layout()
    return fig

st.pyplot(plot_coppock_market_health())