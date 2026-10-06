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

    with __import__("pandas").ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:
        df.to_excel(
            writer,
            index=False,
            sheet_name="Ranking"
        )

    return output.getvalue()


progress_bar = st.progress(0)
status_text = st.empty()

ranking = calcular_rsc(
    callback=lambda p, txt: (
        progress_bar.progress(p),
        status_text.text(txt)
    )
)

ranking.insert(
    0,
    "Posición",
    range(1, len(ranking) + 1)
)

progress_bar.progress(100)
status_text.text("✅ Ranking actualizado")

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