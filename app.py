import streamlit as st
from rsc_engine import calculate_rsc

st.set_page_config(page_title="Invertim – RSC", layout="wide")

st.title("📈 Top 20 RSCValor")

@st.cache_data(ttl=24 * 3600)
def get_rsc():
    return calculate_rsc()

with st.spinner("Calculando RSC…"):
    df = get_rsc()

st.dataframe(
    df.head(20)[
        [
            "Ticker",
            "Date",
            "Company",
            "Close",
            "RSCValor",
            "GICS Sector",
            "GICS Sub-Industry",
        ]
    ],
    width='stretch',
)