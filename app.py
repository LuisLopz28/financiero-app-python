import streamlit as st
import pandas as pd
from datetime import datetime
from utils import cargar_datos, procesar_datos, usuarios, verificar_login

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="App Financiera", layout="wide", page_icon="💰")

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Inicio de Sesión")

    usuario = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    if st.button("Iniciar Sesión"):
        if verificar_login(usuario, password):
            st.session_state.autenticado = True
            st.success("Inicio de sesión exitoso 🎉")
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    st.stop()

# --- INTERFAZ PRINCIPAL ---
st.markdown("<h1 style='color:#00b4d8;'>📊 Análisis de Estado Financiero</h1>", unsafe_allow_html=True)

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/3/3f/Finance_icon.svg/1200px-Finance_icon.svg.png", width=100)
    st.header("⚙️ Parámetros")
    archivo_financiero = st.file_uploader("Estado Financiero", type="xlsx")
    archivo_cruzar = st.file_uploader("Cruzar", type="xlsx")
    archivo_agil = st.file_uploader("Agil", type="xlsx")

if archivo_financiero and archivo_cruzar and archivo_agil:
    with st.spinner("Procesando archivos..."):
        cruzar_df, agil_df, datos_dict, anio = cargar_datos(archivo_cruzar, archivo_agil, archivo_financiero)
        df_final = procesar_datos(cruzar_df, agil_df, datos_dict, anio)
        st.success(f"Datos procesados. Total registros: {len(df_final)}")

        st.dataframe(df_final, use_container_width=True)

        st.download_button(
            "📥 Descargar Excel",
            df_final.to_excel(index=False, engine='openpyxl'),
            file_name="ResultadoFinanciero.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
else:
    st.info("🔍 Carga los tres archivos para iniciar el análisis.")
