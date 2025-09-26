# analisis_lima.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
RUTA_SHAPEFILE = "data/Distrital_INEI_2023_geogpsperu_SuyoPomalia.shp"
RUTA_GEOJSON = "data/lima_distritos.geojson"

# Archivos CSV
RUTA_VENTAS_2022 = "data/GRAN_EMPRESA_2022_MANUFACTURA.csv"
RUTA_VENTAS_2023 = "data/GRAN_EMPRESA_2023_MANUFACTURA.csv"
RUTA_VENTAS_2024 = "data/GRAN_EMPRESA_2024_MANUFACTURA.csv"

# ---------------- FUNCIONES ----------------
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

@st.cache_data
def load_geodata():
    try:
        return gpd.read_file(RUTA_GEOJSON)
    except Exception:
        return gpd.read_file(RUTA_SHAPEFILE)

# ---------------- DATA ----------------
# Cargar shapefile o geojson
gdf = load_geodata()

# Asegurar que el nombre de distrito esté en mayúsculas
if "NOMBDIST" in gdf.columns:
    gdf["NOMBDIST"] = gdf["NOMBDIST"].str.upper()
elif "DISTRITO" in gdf.columns:
    gdf["NOMBDIST"] = gdf["DISTRITO"].str.upper()

# Filtrar solo Lima
if "DEPARTAMEN" in gdf.columns:
    gdf_lima = gdf[gdf["DEPARTAMEN"].str.upper() == "LIMA"]
else:
    gdf_lima = gdf  # geojson ya debería estar filtrado a Lima

# Cargar ventas
df_2022 = load_data(RUTA_VENTAS_2022)
df_2023 = load_data(RUTA_VENTAS_2023)
df_2024 = load_data(RUTA_VENTAS_2024)

# Unificar en un solo DataFrame con columna "año"
df_2022["año"] = 2022
df_2023["año"] = 2023
df_2024["año"] = 2024
df_all = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)

# Normalizar distritos
df_all["distrito"] = df_all["distrito"].str.upper().str.strip()

# ---------------- STREAMLIT APP ----------------
st.set_page_config(page_title="Análisis Lima", layout="wide")

st.title("📊 Análisis de Ventas en Lima")
st.write("Mapa de calor distrital + comparación de provincias por año (2022–2024).")

# Selector de año
anio = st.radio("Selecciona el año:", options=sorted(df_all["año"].unique()), horizontal=True)

# Selector de métrica
metrica = st.selectbox(
    "Métrica a mostrar:",
    ["Promedio de ventas", "Total de ventas"]
)

# Filtro por año
df_year = df_all[df_all["año"] == anio]

# Agregar datos por distrito
if metrica == "Promedio de ventas":
    df_grouped = df_year.groupby("distrito", as_index=False)["venta_prom"].mean()
    columna_valor = "venta_prom"
    titulo_metrica = "Promedio de ventas"
else:
    df_grouped = df_year.groupby("distrito", as_index=False)["venta_prom"].sum()
    columna_valor = "venta_prom"
    titulo_metrica = "Ventas totales"

# Hacer merge con shapefile/geojson
gdf_merged = gdf_lima.merge(df_grouped, left_on="NOMBDIST", right_on="distrito", how="left")

# Plot mapa
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
gdf_lima.boundary.plot(ax=ax, linewidth=0.5, color="black")

# Distritos con datos válidos (filtrar ventas muy bajas para no distorsionar)
umbral = 10000  # mínimo de ventas para ser considerado en el mapa
gdf_data = gdf_merged[gdf_merged[columna_valor].notna() & (gdf_merged[columna_valor] > umbral)]
gdf_data.plot(
    column=columna_valor,
    cmap="Reds",
    linewidth=0.8,
    ax=ax,
    edgecolor="0.8",
    legend=True,
)

# Distritos sin datos o bajo umbral → gris transparente
gdf_no_data = gdf_merged[gdf_merged[columna_valor].isna() | (gdf_merged[columna_valor] <= umbral)]
gdf_no_data.plot(ax=ax, color="lightgrey", alpha=0.2, edgecolor="0.7")

ax.set_title(f"Mapa de calor de {titulo_metrica} por distrito — {anio}", fontsize=14)
ax.axis("off")
st.pyplot(fig)

# ---------------- Comparación de provincias ----------------
df_prov = df_year.groupby("provincia", as_index=False).agg(
    {columna_valor: "mean" if metrica == "Promedio de ventas" else "sum"}
)

st.subheader(f"📊 Comparación de {titulo_metrica} por Provincia — {anio}")
st.bar_chart(df_prov.set_index("provincia")[columna_valor])
