import streamlit as st

from rsc_calculator import calcular_rsc

st.set_page_config(
    page_title="RSC Ranking",
    layout="wide"
)

st.title("📈 RSC Ranking")

st.write("Ranking de fuerza relativa respecto al futuro del S&P500.")

if st.button("Actualizar Ranking"):

    with st.spinner("Calculando..."):

        ranking = calcular_rsc()

    st.success("Completado")

    st.dataframe(ranking,width="stretch",hide_index=True)