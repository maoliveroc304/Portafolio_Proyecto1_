# -----------------------------
# LIBRERÍAS
# -----------------------------
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd
import numpy as np
import requests
import io
import unicodedata
import os

# -----------------------------
# CONFIGURACIÓN
# -----------------------------
st.set_page_config(layout="wide")
st.title('Análisis del Desempeño Económico de Grandes Empresas Manufactureras en Lima (2022-2024)')

# -----------------------------
# FUNCIONES AUXILIARES
# -----------------------------
@st.cache_data
def load_data(filepath):
    try:
        return pd.read_csv(filepath, sep='|')
    except FileNotFoundError:
        st.error(f"Archivo no encontrado: {filepath}")
    except Exception as e:
        st.error(f"Error al cargar {filepath}: {e}")
    return None

def prepare_df(df, year):
    """Filtra Lima y selecciona columnas relevantes, añadiendo año."""
    subset = df[df['departamento'] == 'LIMA'][
        ['provincia', 'distrito', 'ciiu', 'sector', 'venta_prom', 'trabajador', 'experiencia']
    ].copy()
    subset['año'] = year
    return subset

def normalize_text(s):
    """Normaliza texto para evitar problemas de tildes y mayúsculas."""
    if isinstance(s, str):
        s = unicodedata.normalize("NFKD", s)
        return "".join([c for c in s if not unicodedata.combining(c)]).upper().strip()
    return s

@st.cache_data
def load_geojson_from_github(url):
    """Carga GeoJSON directamente desde GitHub para Streamlit Cloud"""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            geojson_bytes = io.BytesIO(response.content)
            gdf = gpd.read_file(geojson_bytes)
            return gdf
        else:
            st.error(f"No se pudo descargar el archivo GeoJSON desde GitHub. Status: {response.status_code}")
    except Exception as e:
        st.error(f"Error al descargar GeoJSON: {e}")
    return None

# -----------------------------
# GRÁFICOS
# -----------------------------
def plot_scatter(df):
    """Gráfico de dispersión con Plotly."""
    import plotly.express as px
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
        labels={
            "trabajador": "Promedio de Trabajadores",
            "venta_prom": "Promedio de Ventas (S/.)"
        },
        title="Relación entre Venta, Trabajadores y Experiencia"
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_bars(df):
    """Gráfico de barras comparativo con Plotly."""
    import plotly.express as px
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

def plot_provincial_map_static(gdf, df, year_selected, provincias_sel):
    """Mapa provincial de ventas en Lima con distritos sin datos en gris."""
    st.subheader(f"🗺️ Mapa provincial de ventas en Lima - {year_selected}")

    # Filtrar solo LIMA en shapefile
    gdf_lima = gdf[gdf["DEPARTAMEN"].apply(normalize_text) == "LIMA"].copy()
    gdf_lima["PROV_APP"] = gdf_lima["PROVINCIA"].apply(normalize_text)

    # Filtrar dataset por año y provincias seleccionadas
    df_year = df[(df["año"] == year_selected) & (df["provincia"].isin(provincias_sel))].copy()
    df_year = df_year.groupby("provincia")["venta_prom"].sum().reset_index()
    df_year["venta_millones"] = df_year["venta_prom"] / 1_000_000
    df_year["provincia"] = df_year["provincia"].apply(normalize_text)

    # Merge shapefile + ventas
    merged = gdf_lima.merge(df_year, left_on="PROV_APP", right_on="provincia", how="left")
    merged["venta_millones"] = merged["venta_millones"].fillna(0)

    # Umbral mínimo de ventas para pintar
    UMBRAL = 0.1
    merged["venta_plot"] = merged["venta_millones"].apply(lambda x: x if x >= UMBRAL else np.nan)

    # Dibujar mapa
    fig, ax = plt.subplots(figsize=(10, 8))
    merged.plot(
        column="venta_plot",
        cmap="OrRd",
        linewidth=0.8,
        ax=ax,
        edgecolor="0.8",
        legend=True,
        legend_kwds={"label": "Ventas (Millones de S/.)", "orientation": "vertical"},
        missing_kwds={
            "color": "#f0f0f0",   # gris claro
            "edgecolor": "0.8",
            "label": "Sin datos"
        }
    )
    ax.axis("off")
    st.pyplot(fig)

# -----------------------------
# MAIN
# -----------------------------
def main():
    # Cargar datos (2022, 2023, 2024)
    df_2022 = load_data('GRAN_EMPRESA_2022_MANUFACTURA.csv')
    df_2023 = load_data('GRAN_EMPRESA_2023_MANUFACTURA.csv')
    df_2024 = load_data('GRAN_EMPRESA_2024_MANUFACTURA.csv')

    if df_2022 is None or df_2023 is None or df_2024 is None:
        st.error("No se pudieron cargar los datos. Verifica las rutas de los archivos.")
        return

    # Preparar datos combinados
    combined_df = pd.concat([
        prepare_df(df_2022, 2022),
        prepare_df(df_2023, 2023),
        prepare_df(df_2024, 2024)
    ])

    # Filtro de provincias
    all_provinces = combined_df["provincia"].unique().tolist()
    selected_provinces = st.multiselect(
        "Selecciona las provincias a visualizar",
        all_provinces,
        default=all_provinces
    )

    filtered_df = combined_df[combined_df["provincia"].isin(selected_provinces)]

    # Selector de año para el mapa
    year_selected = st.selectbox("Selecciona el año para el mapa", [2022, 2023, 2024])

    # Dibujar gráficos interactivos
    plot_scatter(filtered_df)
    plot_bars(filtered_df)
    plot_heatmap(filtered_df)

    # Cargar GeoJSON desde GitHub
    URL_GEOJSON = "https://raw.githubusercontent.com/maoliveroc304/Portafolio_Proyecto1_/main/data/lima_distritos.geojson"
    gdf = load_geojson_from_github(URL_GEOJSON)

    if gdf is not None:
        # Dibujar mapa estático
        plot_provincial_map_static(gdf, combined_df, year_selected, selected_provinces)

if __name__ == "__main__":
    main()
