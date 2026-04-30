# app.py
import streamlit as st
from auth import register_user, login_user
from rsc_engine import calculate_top20

st.set_page_config(page_title="RSC TOP20", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# ---------------- LOGIN ----------------
if not st.session_state.logged_in:
    st.title("🔐 Acceso")

    tab1, tab2 = st.tabs(["Login", "Registro"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Entrar"):
            if login_user(email, password):
                st.session_state.logged_in = True
                st.success("Bienvenido")
                st.rerun()
            else:
                st.error("Credenciales incorrectas")

    with tab2:
        new_email = st.text_input("Nuevo email")
        new_pass = st.text_input("Nueva password", type="password")
        if st.button("Registrarse"):
            if register_user(new_email, new_pass):
                st.success("Usuario creado")
            else:
                st.error("Usuario ya existe")

# ---------------- APP ----------------
else:
    st.title("📈 TOP 20 RSCValor")

    with st.spinner("Calculando ranking..."):
        top20 = calculate_top20()

    st.dataframe(top20, use_container_width=True)

    if st.button("Cerrar sesión"):
        st.session_state.logged_in = False
        st.rerun()