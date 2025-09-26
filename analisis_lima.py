# analisis_lima.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.express as px
import unidecode

# ---------------- CONFIGURACIÓN ----------------
st.set_page_config(layout="wide")
st.title('📊 Análisis Económico de Grandes Empresas Manufactureras en Lima (2022–2024)')

# ---------------- UTILIDADES ----------------
@st.cache_data
def load_data(filepath):
    try:
        return pd.read_csv(filepath, sep='|')
    except Exception as e:
        st.error(f"Error al cargar {filepath}: {e}")
        return None

@st.cache_data
def load_geojson(url):
    try:
        return gpd.read_file(url)
    except Exception as e:
        st.error(f"No se pudo cargar GeoJSON: {e}")
        return None

def prepare_df(df, year):
    """Filtra Lima y selecciona columnas relevantes, añadiendo año."""
    subset = df[df['departamento'].str.upper() == 'LIMA'][[
        'provincia', 'distrito', 'ciiu', 'sector', 'venta_prom', 'trabajador', 'experiencia'
    ]].copy()
    subset['año'] = year
    return subset

# ---------------- MAIN ----------------
def main():
    # --- 1. Cargar datos ---
    df_2022 = load_data("data/GRAN_EMPRESA_2022_MANUFACTURA.csv")
    df_2023 = load_data("data/GRAN_EMPRESA_2023_MANUFACTURA.csv")
    df_2024 = load_data("data/GRAN_EMPRESA_2024_MANUFACTURA.csv")
    
    if df_2022 is None or df_2023 is None or df_2024 is None:
        st.stop()

    combined_df = pd.concat([
        prepare_df(df_2022, 2022),
        prepare_df(df_2023, 2023),
        prepare_df(df_2024, 2024)
    ])

    # --- 2. Selector de provincias ---
    all_provinces = combined_df['provincia'].unique().tolist()
    selected_provinces = st.multiselect(
        '📍 Selecciona las provincias a visualizar',
        all_provinces,
        default=all_provinces
    )
    filtered_df = combined_df[combined_df['provincia'].isin(selected_provinces)]

    # --- 3. Gráfico de dispersión interactivo ---
    st.header("🔎 Relación entre Venta Promedio, Trabajadores y Experiencia")
    promedios = filtered_df.groupby(['provincia', 'año']).mean(numeric_only=True).reset_index()

    fig_scatter = px.scatter(
        promedios,
        x="trabajador",
        y="venta_prom",
        size="experiencia",
        color="año",
        hover_name="provincia",
        labels={"venta_prom": "Venta Promedio (S/)", "trabajador": "Trabajadores"},
        title="Relación entre Venta, Trabajadores y Experiencia"
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # --- 4. Comparación de ventas promedio/totales ---
    st.header("📊 Comparación de Venta por Provincia")
    modo = st.radio("Selecciona el tipo de análisis:", ["Promedio", "Total"], horizontal=True)

    if modo == "Promedio":
        ventas = filtered_df.groupby(['provincia', 'año'])['venta_prom'].mean().reset_index()
        titulo = "Comparación de Venta Promedio por Provincia (2022–2024)"
    else:
        ventas = filtered_df.groupby(['provincia', 'año'])['venta_prom'].sum().reset_index()
        titulo = "Comparación de Ventas Totales por Provincia (2022–2024)"

    fig_bar = px.bar(
        ventas,
        x="provincia",
        y="venta_prom",
        color="año",
        barmode="group",
        labels={"venta_prom": "Ventas (S/)", "provincia": "Provincia"},
        title=titulo
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- 5. Mapa de calor distrital ---
    st.header("🗺️ Mapa de calor distrital de ventas en Lima")

    # GeoJSON desde GitHub
    URL_GEOJSON = "https://github.com/maoliveroc304/Portafolio_Proyecto1_/tree/main/data/lima_distritos.geojson"
    gdf_lima = load_geojson(URL_GEOJSON)
    if gdf_lima is None:
        st.stop()

    # Selector de año
    year_selected = st.radio("Selecciona el año para el mapa:", [2022, 2023, 2024], horizontal=True)
    df_year = combined_df[combined_df['año'] == year_selected]

    # Normalizar texto
    df_year["distrito_norm"] = df_year["distrito"].str.upper().apply(lambda x: unidecode.unidecode(x.strip()))
    gdf_lima["DISTRITO_NORM"] = gdf_lima["DISTRITO"].str.upper().apply(lambda x: unidecode.unidecode(x.strip()))

    # Ventas por distrito
    ventas_df = df_year.groupby("distrito_norm")["venta_prom"].sum().reset_index()
    ventas_df.rename(columns={"distrito_norm": "DISTRITO_NORM", "venta_prom": "venta_millones"}, inplace=True)
    ventas_df["venta_millones"] = ventas_df["venta_millones"] / 1_000_000  # en millones

    # Merge y filtro mínimo
    merged = gdf_lima.merge(ventas_df, on="DISTRITO_NORM", how="left")
    UMBRAL = 0.5
    merged["venta_millones_filtrada"] = merged["venta_millones"].apply(lambda x: x if x >= UMBRAL else None)

    # Plot mapa
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    merged.plot(ax=ax, color="lightgrey", edgecolor="white", linewidth=0.5)  # base distritos
    merged.plot(
        column="venta_millones_filtrada",
        cmap="OrRd",
        linewidth=0.8,
        ax=ax,
        edgecolor="0.8",
        legend=True
    )
    ax.axis("off")
    st.pyplot(fig)

if __name__ == "__main__":
    main()
