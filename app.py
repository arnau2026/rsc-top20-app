import streamlit as st
import pandas as pd

from io import BytesIO
from datetime import datetime

from rsc_calculator import (
    calcular_rsc,
    calcular_rsc_etf,
)


st.set_page_config(
    page_title="RSC Ranking",
    page_icon="📈",
    layout="wide"
)


# ---------------------------------------------------------
# CONFIGURACIÓN DEL RANKING
# ---------------------------------------------------------

if "media_rsc" not in st.session_state:
    st.session_state.media_rsc = 8

PERIOD = 10
MEDIA = st.session_state.media_rsc


# ---------------------------------------------------------
# TÍTULO
# ---------------------------------------------------------

st.title("📈 RSC Ranking")

st.caption(
    "Fuerza relativa respecto al SPY."
)


# ---------------------------------------------------------
# FUNCIÓN EXCEL
# ---------------------------------------------------------

def to_excel(df, sheet_name):

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        df.to_excel(
            writer,
            index=False,
            sheet_name=sheet_name
        )

    return output.getvalue()


# ---------------------------------------------------------
# RANKING ACCIONES
# ---------------------------------------------------------

with st.spinner(
    "Calculando ranking de acciones..."
):

    acciones = calcular_rsc(
        period=PERIOD,
        media=MEDIA
    )


if not acciones.empty:

    acciones.insert(
        0,
        "Posición",
        range(1, len(acciones) + 1)
    )


st.subheader("Ranking de acciones")


st.dataframe(
    acciones,
    width="stretch",
    hide_index=True,
    height=620
)


st.download_button(
    label="⬇️ Descargar Excel acciones",
    data=to_excel(
        acciones,
        "Ranking Acciones"
    ),
    file_name=(
        f"{datetime.now():%Y-%m-%d}"
        "_ranking_acciones.xlsx"
    ),
    mime=(
        "application/vnd.openxmlformats-"
        "officedocument.spreadsheetml.sheet"
    ),
    width="stretch",
)


# ---------------------------------------------------------
# ETF UCITS
# ---------------------------------------------------------

st.divider()

st.subheader(
    "Ranking de ETF UCITS"
)


with st.spinner(
    "Calculando ranking de ETF UCITS..."
):

    ucits = calcular_rsc_etf(
        "ETF UCITS.xlsx",
        period=PERIOD,
        media=MEDIA
    )


if not ucits.empty:

    ucits = ucits.drop(
        columns=[
            "Fecha de inicio",
            "Patrimonio millones de euros",
            "Domicilio del fondo",
        ],
        errors="ignore",
    )

    first_columns = [
        "Ticker",
        "Date",
        "Nombre del fondo",
        "Close",
        "RSCValor",
        "Divisa fondo"
    ]

    remaining_columns = [
        c
        for c in ucits.columns
        if c not in first_columns
    ]

    ucits = ucits[
        first_columns
        + remaining_columns
    ]

    ucits.insert(
        0,
        "Posición",
        range(1, len(ucits) + 1)
    )

    st.dataframe(
        ucits,
        width="stretch",
        hide_index=True,
        height=620
    )

    st.download_button(
        label="⬇️ Descargar Excel ETF UCITS",
        data=to_excel(
            ucits,
            "Ranking ETF UCITS"
        ),
        file_name=(
            f"{datetime.now():%Y-%m-%d}"
            "_ranking_etf_ucits.xlsx"
        ),
        mime=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        width="stretch",
    )

else:

    st.warning(
        "No se han podido cargar los ETF UCITS."
    )


# ---------------------------------------------------------
# BOTÓN RANKING MÁS DIVERSIFICADO
# ---------------------------------------------------------

st.write("")

col_boton, _ = st.columns([1, 5])

with col_boton:

    if st.button(
        "Ranking más diversificado",
        type="secondary",
        width="content"
    ):

        st.session_state.media_rsc = 4

        st.rerun()