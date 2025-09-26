import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Análisis Económico Lima", layout="wide")

# ---------------- DATOS -----------------
# Rutas a los archivos
df_2022 = load_data("data/GRAN_EMPRESA_2022_MANUFACTURA.csv")
df_2023 = load_data("data/GRAN_EMPRESA_2023_MANUFACTURA.csv")
df_2024 = load_data("data/GRAN_EMPRESA_2024_MANUFACTURA.csv")
RUTA_GEOJSON = "data/lima_distritos.geojson"

RUTA_SHAPEFILE = "lima_distritos.geojson"
gdf_lima = gpd.read_file(RUTA_SHAPEFILE)

# Cargar datasets de ventas
ventas_2022 = pd.read_csv(RUTA_VENTAS_2022)
ventas_2023 = pd.read_csv(RUTA_VENTAS_2023)
ventas_2024 = pd.read_csv(RUTA_VENTAS_2024)

# Normalizamos para tener misma estructura
for df, year in zip([ventas_2022, ventas_2023, ventas_2024], [2022, 2023, 2024]):
    df["Año"] = year

ventas = pd.concat([ventas_2022, ventas_2023, ventas_2024], ignore_index=True)

# ---------------- SIDEBAR ----------------
st.sidebar.header("⚙️ Controles")

# Selección de año
anio = st.sidebar.selectbox("Selecciona el año", [2022, 2023, 2024])

# Provincias disponibles
provincias = ventas["Provincia"].unique().tolist()
provincias_sel = st.sidebar.multiselect(
    "Selecciona provincias",
    provincias,
    default=provincias[:1]  # por defecto la primera
)

# Métrica: Promedio o Total
metrica = st.sidebar.radio(
    "Métrica a mostrar",
    ["Promedio", "Total"]
)

# Umbral mínimo para mapa de calor
umbral_min = st.sidebar.number_input(
    "Umbral mínimo de ventas para incluir en el mapa",
    min_value=0.0, value=1000.0, step=500.0
)

# ---------------- FILTRADO ----------------
df_filtrado = ventas[
    (ventas["Año"] == anio) & (ventas["Provincia"].isin(provincias_sel))
]

# ---------------- GRÁFICOS ----------------
st.title("📊 Análisis Económico Lima")

# Gráfico comparativo por provincia
if metrica == "Promedio":
    df_agg = df_filtrado.groupby("Provincia")["Ventas"].mean().reset_index()
    titulo = "📊 Comparación de Venta Promedio por Provincia"
else:
    df_agg = df_filtrado.groupby("Provincia")["Ventas"].sum().reset_index()
    titulo = "📊 Comparación de Ventas Totales por Provincia"

fig_bar = px.bar(
    df_agg,
    x="Provincia",
    y="Ventas",
    color="Provincia",
    title=titulo,
    text_auto=True,
    hover_data={"Ventas": ":,.2f"}
)
fig_bar.update_layout(legend=dict(title="Provincias", itemsizing="constant"))

st.plotly_chart(fig_bar, use_container_width=True)

# Mapa de calor distrital
st.subheader("🗺️ Mapa de Calor Distrital (Lima)")

# Filtrar ventas por distrito y año
ventas_distrital = df_filtrado.groupby("Distrito")["Ventas"].sum().reset_index()

# Aplicar umbral: distritos con ventas < umbral = 0 (se verán en gris)
ventas_distrital.loc[ventas_distrital["Ventas"] < umbral_min, "Ventas"] = 0

# Merge con geometría
gdf_map = gdf_lima.merge(ventas_distrital, how="left", left_on="NOMB_DIST", right_on="Distrito")

# Colorear solo distritos con datos, los demás en gris/transparente
gdf_map["color"] = gdf_map["Ventas"].apply(lambda x: None if pd.isna(x) or x == 0 else x)

fig_map = px.choropleth_mapbox(
    gdf_map,
    geojson=gdf_map.geometry.__geo_interface__,
    locations=gdf_map.index,
    color="color",
    color_continuous_scale="Reds",
    mapbox_style="carto-positron",
    zoom=8.5,
    center={"lat": -12.0464, "lon": -77.0428},
    opacity=0.7,
    hover_name="NOMB_DIST",
    hover_data={"Ventas": ":,.2f"}
)

fig_map.update_layout(coloraxis_colorbar=dict(title="Ventas"))

st.plotly_chart(fig_map, use_container_width=True)

st.caption("Distritos sin datos aparecen en gris. El umbral mínimo filtra valores demasiado bajos para mejorar la escala de color.")
