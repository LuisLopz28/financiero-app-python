import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Usuarios simulados (puedes cambiar esto a tu gusto)
USUARIOS = {
    "luis": "1234",
    "admin": "adminpass"
}

def login():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False

    if not st.session_state.autenticado:
        st.title("🔐 Iniciar sesión")
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        if st.button("Iniciar sesión"):
            if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
                st.session_state.autenticado = True
                st.experimental_rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
        st.stop()

login()

# --- Configuración de página ---
st.set_page_config(page_title="Análisis Financiero", layout="wide")

st.title("📊 Análisis de Estados Financieros")
st.markdown("Carga un archivo financiero anual para procesarlo con las tablas auxiliares integradas.")

# --- Archivos auxiliares por defecto ---
ARCHIVO_CRUZAR = "Cruzar - Tabla Auxiliar.xlsx"
ARCHIVO_AGIL = "Agil - Tabla Auxiliar.xlsx"

# --- Cargar auxiliares al iniciar ---
@st.cache_data
def cargar_tablas_auxiliares():
    cruzar_df = pd.read_excel(ARCHIVO_CRUZAR)
    agil_df = pd.read_excel(ARCHIVO_AGIL)
    return cruzar_df, agil_df

cruzar_df, agil_df = cargar_tablas_auxiliares()

# --- Subir archivo financiero ---
archivo_financiero = st.file_uploader("📤 Subir archivo de estado financiero", type=["xlsx"])

if archivo_financiero:
    ANIO = archivo_financiero.name.split('.')[0][-4:]
    xls = pd.ExcelFile(archivo_financiero)

    # Filtrar hojas relevantes
    nombres_hojas = cruzar_df["Name"].dropna().unique()
    datos_dict = {hoja: xls.parse(hoja, header=None) for hoja in nombres_hojas if hoja in xls.sheet_names}

    def es_mes(col):
        col = str(col).lower()
        meses = {'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'}
        return any(m in col for m in meses) and 'total' not in col

    def mes_a_num(col):
        meses = {'enero':1, 'febrero':2, 'marzo':3, 'abril':4, 'mayo':5, 'junio':6,
                 'julio':7, 'agosto':8, 'septiembre':9, 'octubre':10, 'noviembre':11, 'diciembre':12}
        col = str(col).lower()
        return next((v for k, v in meses.items() if k in col), None)

    resultados = []

    for hoja, df in datos_dict.items():
        if df.empty:
            continue

        header_row_idx = df.first_valid_index()
        columnas = df.iloc[header_row_idx].fillna("").astype(str).tolist()
        agil_sub = agil_df[agil_df["Linea"].notna()]

        for _, agil in agil_sub.iterrows():
            try:
                linea_excel = int(agil["Linea"])
                fila = df.iloc[linea_excel - 1]
            except:
                continue

            for i, valor in enumerate(fila[1:], start=1):
                col_nombre = columnas[i] if i < len(columnas) else f"Col_{i}"
                if es_mes(col_nombre):
                    if pd.notna(valor) and str(valor).strip():
                        mes_num = mes_a_num(col_nombre)
                        resultados.append({
                            "Name": hoja,
                            "Item": agil['Item'],
                            "Sub Item": agil['Sub Item'],
                            "Relacion": agil['Relacion'],
                            "Nombre Item": agil['Nombre Item'],
                            "Mes": col_nombre.strip(),
                            "Mes_Num": mes_num,
                            "Año": ANIO,
                            "Fecha": datetime(int(ANIO), mes_num, 1) if mes_num else None,
                            "Valor": valor
                        })

    df_resultados = pd.DataFrame(resultados)
    df_resultados["Valor"] = pd.to_numeric(df_resultados["Valor"], errors="coerce")

    df_final = (
        df_resultados
        .merge(cruzar_df, on="Name", how="left")
        .drop_duplicates()
        [["Pais", "Departamento", "Proyecto", "Actividad", "Name", "Item",
          "Sub Item", "Relacion", "Nombre Item", "Año", "Mes", "Mes_Num", "Fecha", "Valor"]]
    )

    # Mostrar tabla
    st.success(f"✅ Procesamiento completo. Registros: {len(df_final)}")
    st.dataframe(df_final, use_container_width=True)

    # Botón para descargar Excel
    output = io.BytesIO()
    df_final.to_excel(output, index=False, engine='openpyxl')
    st.download_button(
        label="📥 Descargar Excel",
        data=output.getvalue(),
        file_name="DataFinanciero.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
