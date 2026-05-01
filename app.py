import streamlit as st
from rsc_engine import calculate_top20

st.set_page_config(
    page_title="Invertim – Top 20 RSC",
    layout="wide"
)

st.title("📈 Top 20 RSCValor (SP500 + NASDAQ100)")
st.caption("Universo automático desde Wikipedia · Sin Excel · Sin login")

@st.cache_data(ttl=24 * 3600)
def get_top20():
    return calculate_top20()

with st.spinner("Calculando ranking..."):
    top20 = get_top20()

st.dataframe(top20, use_container_width=True)

st.caption("Datos: Wikipedia · Yahoo Finance")
