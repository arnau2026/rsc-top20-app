import streamlit as st
from rsc_engine import calculate_rsc
from datetime import datetime

# -------------------------------------------------
# CONFIGURACIÓN DE PÁGINA
# -------------------------------------------------

st.set_page_config(
    page_title="Acciones USA – RSC",
    layout="wide",
)

# -------------------------------------------------
# TÍTULO DINÁMICO
# -------------------------------------------------

now = datetime.now()
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
# LIMPIEZA VISUAL DEL DATAFRAME
# -------------------------------------------------

# Crear ranking 1..N
df = df.reset_index(drop=True)
df.insert(0, "Rank", df.index + 1)

# -------------------------------------------------
# MOSTRAR TODOS LOS RESULTADOS
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