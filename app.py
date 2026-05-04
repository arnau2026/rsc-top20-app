import streamlit as st
from rsc_engine import calculate_rsc
from datetime import datetime
import pytz

# -------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -------------------------------------------------

st.set_page_config(
    page_title="Acciones USA – RSC",
    layout="wide",
)

# -------------------------------------------------
# FECHA Y HORA (HORARIO ESPAÑA REAL ✅)
# -------------------------------------------------

tz = pytz.timezone("Europe/Madrid")
now = datetime.now(tz)

fecha = now.strftime("%Y-%m-%d")
hora = now.strftime("%H:%M")

st.title(f"📈 Acciones USA ordenadas a día {fecha} y hora {hora}")

# -------------------------------------------------
# CÁLCULO (CACHE)
# -------------------------------------------------

@st.cache_data(ttl=24 * 3600)
def get_rsc():
    return calculate_rsc()

with st.spinner("Calculando RSC..."):
    df = get_rsc()

# -------------------------------------------------
# LIMPIEZA Y RANKING (ELIMINA ÍNDICE FANTASMA ✅)
# -------------------------------------------------

df = df.reset_index(drop=True)
df.insert(0, "Rank", range(1, len(df) + 1))

# -------------------------------------------------
# VISUALIZACIÓN LIMPIA
# -------------------------------------------------

st.dataframe(
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
    ],
    width="stretch",
    hide_index=True,   # ahora sí funciona
)

# -------------------------------------------------
# DESCARGA
# -------------------------------------------------

st.download_button(
    "⬇️ Descargar todas las acciones (CSV)",
    df.to_csv(index=False).encode("utf-8"),
    file_name=f"acciones_usa_rsc_{fecha}_{hora.replace(':','')}.csv",
    mime="text/csv",
)