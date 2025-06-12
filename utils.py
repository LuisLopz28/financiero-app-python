import pandas as pd
from datetime import datetime
import hashlib

# Usuarios simulados (ideal usar db en producción)
usuarios = {
    "luis": hashlib.sha256("1234".encode()).hexdigest(),
    "admin": hashlib.sha256("admin123".encode()).hexdigest()
}

def verificar_login(usuario, contraseña):
    hash_pass = hashlib.sha256(contraseña.encode()).hexdigest()
    return usuarios.get(usuario) == hash_pass

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

def cargar_datos(archivo_cruzar, archivo_agil, archivo_financiero):
    cruzar_df = pd.read_excel(archivo_cruzar)
    agil_df = pd.read_excel(archivo_agil)
    xls = pd.ExcelFile(archivo_financiero)
    anio = archivo_financiero.name.split('.')[0][-4:]
    hojas = cruzar_df["Name"].dropna().unique()
    datos_dict = {hoja: xls.parse(hoja, header=None) for hoja in hojas if hoja in xls.sheet_names}
    return cruzar_df, agil_df, datos_dict, anio

def procesar_datos(cruzar_df, agil_df, datos_dict, anio):
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
                            "Año": anio,
                            "Fecha": datetime(int(anio), mes_num, 1) if mes_num else None,
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
    return df_final
