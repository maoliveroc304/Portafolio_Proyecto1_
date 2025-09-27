# -----------------------------
# LIBRERÍAS
# -----------------------------
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import unicodedata
import plotly.express as px

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
st.set_page_config(layout="wide")
st.title('Análisis del Desempeño Económico de Grandes Empresas Manufactureras en Lima (2022-2024)')

# -----------------------------
# FUNCIONES AUXILIARES
# -----------------------------
@st.cache_data
def load_data(file):
    """Carga CSV desde un archivo subido por el usuario"""
    try:
        return pd.read_csv(file, sep='|')
    except Exception as e:
        st.error(f"Error al cargar {file.name if hasattr(file,'name') else file}: {e}")
        return None

def prepare_df(df, year):
    """Filtra Lima y selecciona columnas relevantes, añadiendo año."""
    subset = df[df['departamento'] == 'LIMA'][['provincia', 'distrito', 'ciiu', 'sector', 'venta_prom', 'trabajador', 'experiencia']].copy()
    subset['año'] = year
    return subset

def normalize_text(s):
    """Normaliza texto para evitar problemas de tildes y mayúsculas."""
    if isinstance(s, str):
        s = unicodedata.normalize("NFKD", s)
        return "".join([c for c in s if not unicodedata.combining(c)]).upper().strip()
    return s

# -----------------------------
# GRÁFICOS
# -----------------------------
def plot_scatter(df):
    """Gráfico de dispersión con Plotly."""
    st.subheader("📊 Relación entre Venta Promedio, Trabajadores y Experiencia")
    promedios = df.groupby(['provincia', 'año'])[['venta_prom', 'trabajador', 'experiencia']].mean().reset_index()
    fig = px.scatter(
        promedios,
        x="trabajador",
        y="venta_prom",
        color="año",
        symbol="año",
        size="experiencia",
        hover_data=["provincia"],
        labels={"trabajador": "Promedio de Trabajadores", "venta_prom": "Promedio de Ventas (S/.)"},
        title="Relación entre Venta, Trabajadores y Experiencia"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_bars(df):
    """Gráfico de barras comparativo con Plotly."""
    st.subheader("📊 Comparación de Venta Promedio por Provincia")
    ventas = df.groupby(['provincia', 'año'])['venta_prom'].mean().reset_index()
    ventas["venta_millones"] = ventas["venta_prom"] / 1_000_000
    fig = px.bar(
        ventas,
        x="provincia",
        y="venta_millones",
        color="año",
        barmode="group",
        labels={"venta_millones": "Venta Promedio (Millones S/.)"},
        title="Comparación de Venta Promedio por Provincia"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_heatmap(df):
    """Mapa de calor (heatmap) por provincia."""
    st.subheader("📊 Ventas Totales por Provincia")
    ventas_totales = df.groupby(['provincia', 'año'])['venta_prom'].sum().reset_index()
    ventas_totales["venta_millones"] = ventas_totales["venta_prom"] / 1_000_000
    pivot = ventas_totales.pivot(index="provincia", columns="año", values="venta_millones")
    fig, ax = plt.subplots(figsize=(10, 7))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlGnBu", ax=ax)
    ax.set_title("Ventas Totales por Provincia (Millones de S/.)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Provincia")
    st.pyplot(fig)

def plot_correlation(df):
    """Gráfico de correlación entre variables."""
    st.subheader("📊 Matriz de correlación")
    corr_df = df[['venta_prom', 'trabajador', 'experiencia']]
    corr = corr_df.corr()
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    ax.set_title("Correlación entre Venta, Trabajadores y Experiencia")
    st.pyplot(fig)

# -----------------------------
# MAIN
# -----------------------------
def main():
    st.sidebar.header("Carga de archivos CSV")
    file_2022 = st.sidebar.file_uploader("Selecciona CSV 2022", type=['csv'])
    file_2023 = st.sidebar.file_uploader("Selecciona CSV 2023", type=['csv'])
    file_2024 = st.sidebar.file_uploader("Selecciona CSV 2024", type=['csv'])

    if file_2022 and file_2023 and file_2024:
        # Cargar datos
        df_2022 = load_data(file_2022)
        df_2023 = load_data(file_2023)
        df_2024 = load_data(file_2024)

        # Preparar datos combinados
        combined_df = pd.concat([
            prepare_df(df_2022, 2022),
            prepare_df(df_2023, 2023),
            prepare_df(df_2024, 2024)
        ])

        # Filtro de años
        years_selected = st.multiselect("Selecciona los años a visualizar", [2022, 2023, 2024], default=[2022, 2023, 2024])
        filtered_df = combined_df[combined_df["año"].isin(years_selected)]

        # Filtro de provincias
        all_provinces = filtered_df["provincia"].unique().tolist()
        selected_provinces = st.multiselect("Selecciona las provincias a visualizar", all_provinces, default=all_provinces)
        filtered_df = filtered_df[filtered_df["provincia"].isin(selected_provinces)]

        # Dibujar gráficos
        plot_scatter(filtered_df)
        plot_bars(filtered_df)
        plot_heatmap(filtered_df)
        plot_correlation(filtered_df)
    else:
        st.info("Sube los tres archivos CSV (2022, 2023, 2024) para visualizar los análisis.")

if __name__ == "__main__":
    main()
