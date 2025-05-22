import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go

# Carpeta para almacenar informes
DATA_DIR = "informes_historicos"
os.makedirs(DATA_DIR, exist_ok=True)

def guardar_informe(df):
    fecha = datetime.now().strftime("%Y-%m-%d")
    archivo = os.path.join(DATA_DIR, f"informe_{fecha}.csv")
    df.to_csv(archivo, index=False)
    st.success(f"Informe guardado como {archivo}")

def cargar_informes():
    archivos = sorted([f for f in os.listdir(DATA_DIR) if f.endswith(".csv")])
    informes = {}
    for f in archivos:
        fecha = f.split("_")[1].replace(".csv", "")
        informes[fecha] = pd.read_csv(os.path.join(DATA_DIR, f))
    return informes

def graficar_plan_vs_real(df):
    equipos = df['Equipo'].unique()
    planificado = df.groupby('Equipo')['Tonelaje Planificado'].sum()
    real = df.groupby('Equipo')['Tonelaje Real'].sum()
    promedio_plan = planificado.mean()
    promedio_real = real.mean()

    fig = go.Figure()
    fig.add_trace(go.Bar(x=equipos, y=planificado, name='Planificado'))
    fig.add_trace(go.Bar(x=equipos, y=real, name='Real'))
    fig.add_trace(go.Scatter(x=equipos, y=[promedio_plan]*len(equipos), mode='lines', name='Promedio Planificado'))
    fig.add_trace(go.Scatter(x=equipos, y=[promedio_real]*len(equipos), mode='lines', name='Promedio Real'))
    fig.update_layout(barmode='group', title="Tonelaje Planificado vs Real por Equipo")
    st.plotly_chart(fig)

def analizar_diferencias(df_hoy, df_ayer):
    resumen = pd.DataFrame()
    resumen['Equipo'] = df_hoy['Equipo']
    resumen['Tonelaje Planificado Hoy'] = df_hoy['Tonelaje Planificado']
    resumen['Tonelaje Planificado Ayer'] = df_ayer['Tonelaje Planificado']
    resumen['Diferencia Planificado'] = resumen['Tonelaje Planificado Hoy'] - resumen['Tonelaje Planificado Ayer']
    resumen['Tonelaje Real Hoy'] = df_hoy['Tonelaje Real']
    resumen['Tonelaje Real Ayer'] = df_ayer['Tonelaje Real']
    resumen['Diferencia Real'] = resumen['Tonelaje Real Hoy'] - resumen['Tonelaje Real Ayer']

    st.write("### Análisis Día vs Día Anterior")
    st.dataframe(resumen)

    diff_real_total = resumen['Diferencia Real'].sum()
    if diff_real_total > 0:
        st.success(f"La producción aumentó {diff_real_total:.2f} toneladas respecto al día anterior.")
    elif diff_real_total < 0:
        st.warning(f"La producción disminuyó {abs(diff_real_total):.2f} toneladas respecto al día anterior.")
    else:
        st.info("La producción se mantuvo igual respecto al día anterior.")

# Interfaz Streamlit
st.title("Informe Operacional Diario")

uploaded_file = st.file_uploader("Cargar informe diario (Excel o CSV)", type=['xlsx', 'csv'])
if uploaded_file:
    if uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)
    else:
        df = pd.read_csv(uploaded_file)
    st.write("Datos cargados:")
    st.dataframe(df)

    if st.button("Guardar Informe Diario"):
        guardar_informe(df)

informes = cargar_informes()
fechas = list(informes.keys())
fecha_seleccionada = st.selectbox("Seleccionar fecha para visualizar", fechas)

if fecha_seleccionada:
    df_seleccionado = informes[fecha_seleccionada]
    st.write(f"Informe del {fecha_seleccionada}")
    st.dataframe(df_seleccionado)
    graficar_plan_vs_real(df_seleccionado)

    idx = fechas.index(fecha_seleccionada)
    if idx > 0:
        fecha_ayer = fechas[idx-1]
        df_ayer = informes[fecha_ayer]
        analizar_diferencias(df_seleccionado, df_ayer)
    else:
        st.info("No hay datos del día anterior para comparar.")