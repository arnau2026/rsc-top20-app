import streamlit as st
from io import BytesIO
from datetime import datetime

from rsc_calculator import calcular_rsc

st.set_page_config(
    page_title="RSC Ranking",
    layout="wide"
)

st.title("📈 RSC Ranking")

st.write("Ranking de fuerza relativa respecto al futuro del S&P500.")


def convertir_a_excel(df):
    output = BytesIO()

    with __import__("pandas").ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Ranking")

    return output.getvalue()

with st.spinner("Calculando ranking..."):

    ranking = calcular_rsc()

    # Añadir posición
    ranking.insert(0, "Posición", range(1, len(ranking) + 1))

st.success("Ranking actualizado")

st.dataframe(
    ranking,
    use_container_width=True,
    hide_index=True
)

excel = convertir_a_excel(ranking)

st.download_button(
    label="Descargar Excel",
    data=excel,
    file_name=f"{datetime.now().strftime('%Y-%m-%d')}_ranking.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)