import streamlit as st
import pandas as pd
import plotly.express as px

# Verifica si hay datos procesados en la sesión
if "autenticado" not in st.session_state or not st.session_state.autenticado:
    st.warning("🔒 Debes iniciar sesión desde la página principal.")
    st.stop()

if "df_final" not in st.session_state:
    st.warning("📁 Aún no has cargado los archivos. Ve a la página principal para procesarlos.")
    st.stop()

df_final = st.session_state.df_final

st.markdown("<h1 style='color:#00b4d8;'>📈 Visualización de Resultados</h1>", unsafe_allow_html=True)

# --- Filtros ---
with st.sidebar:
    st.header("🎛️ Filtros de visualización")
    paises = st.multiselect("País", options=df_final["Pais"].dropna().unique(), default=None)
    proyectos = st.multiselect("Proyecto", options=df_final["Proyecto"].dropna().unique(), default=None)
    anios = st.multiselect("Año", options=df_final["Año"].dropna().unique(), default=None)

df_filtrado = df_final.copy()

if paises:
    df_filtrado = df_filtrado[df_filtrado["Pais"].isin(paises)]
if proyectos:
    df_filtrado = df_filtrado[df_filtrado["Proyecto"].isin(proyectos)]
if anios:
    df_filtrado = df_filtrado[df_filtrado["Año"].isin(anios)]

# --- Gráfico de líneas por Proyecto ---
st.subheader("📊 Evolución mensual por Proyecto")

if df_filtrado.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados.")
else:
    df_group = (
        df_filtrado
        .groupby(["Fecha", "Proyecto"], as_index=False)
        .agg({"Valor": "sum"})
        .sort_values("Fecha")
    )

    fig = px.line(
        df_group,
        x="Fecha",
        y="Valor",
        color="Proyecto",
        markers=True,
        title="Tendencia mensual del valor financiero",
        labels={"Valor": "Valor ($)", "Fecha": "Fecha"}
    )

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# --- Tabla resumen por Departamento y Proyecto ---
st.subheader("📋 Resumen por Departamento y Proyecto")
resumen = (
    df_filtrado
    .groupby(["Departamento", "Proyecto"], as_index=False)
    .agg({"Valor": "sum"})
    .sort_values(by="Valor", ascending=False)
)

st.dataframe(resumen, use_container_width=True, height=400)
