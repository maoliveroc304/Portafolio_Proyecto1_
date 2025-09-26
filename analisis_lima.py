# analisis_lima.py
import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
RUTA_SHAPEFILE = "data/Distrital_INEI_2023_geogpsperu_SuyoPomalia.shp"

# Archivos CSV
RUTA_VENTAS_2022 = "data/GRAN_EMPRESA_2022_MANUFACTURA.csv"
RUTA_VENTAS_2023 = "data/GRAN_EMPRESA_2023_MANUFACTURA.csv"
RUTA_VENTAS_2024 = "data/GRAN_EMPRESA_2024_MANUFACTURA.csv"

# ---------------- FUNCIONES ----------------
@st.cache_data
def load_data(path):
    return pd.read_csv(path)

@st.cache_data
def load_shapefile(path):
    return gpd.read_file(path)

# ---------------- DATA ----------------
# Cargar shapefile
gdf = load_shapefile(RUTA_SHAPEFILE)

# Filtrar solo Lima
gdf_lima = gdf[gdf["DEPARTAMEN"].str.upper() == "LIMA"]

# Cargar ventas
df_2022 = load_data(RUTA_VENTAS_2022)
df_2023 = load_data(RUTA_VENTAS_2023)
df_2024 = load_data(RUTA_VENTAS_2024)

# Unificar en un solo DataFrame con columna "año"
df_2022["año"] = 2022
df_2023["año"] = 2023
df_2024["año"] = 2024
df_all = pd.concat([df_2022, df_2023, df_2024], ignore_index=True)

# ---------------- STREAMLIT APP ----------------
st.set_page_config(page_title="Análisis Lima", layout="wide")

st.title("📊 Análisis de Ventas en Lima")
st.write("Mapa de calor distrital + comparación de provincias por año.")

# Selector de año
anio = st.radio("Selecciona el año:", options=sorted(df_all["año"].unique()), horizontal=True)

# Selector de métrica
metrica = st.selectbox(
    "Métrica a mostrar:",
    ["Promedio de ventas", "Total de ventas"]
)

# Filtrar por año
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

# Hacer merge con shapefile
gdf_merged = gdf_lima.merge(df_grouped, left_on="NOMBDIST", right_on="distrito", how="left")

# Plot mapa
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
gdf_lima.boundary.plot(ax=ax, linewidth=0.5, color="black")

# Distritos con datos válidos
gdf_data = gdf_merged[gdf_merged[columna_valor].notna() & (gdf_merged[columna_valor] > 1000)]
gdf_data.plot(
    column=columna_valor,
    cmap="Reds",
    linewidth=0.8,
    ax=ax,
    edgecolor="0.8",
    legend=True,
)

# Distritos sin datos → gris/transparente
gdf_no_data = gdf_merged[gdf_merged[columna_valor].isna() | (gdf_merged[columna_valor] <= 1000)]
gdf_no_data.plot(ax=ax, color="lightgrey", alpha=0.2, edgecolor="0.7")

ax.set_title(f"Mapa de calor de {titulo_metrica} por distrito — {anio}", fontsize=14)
ax.axis("off")
st.pyplot(fig)

# ---------------- Comparación de provincias ----------------
df_prov = df_year.groupby("provincia", as_index=False).agg(
    {columna_valor: "mean" if metrica=="Promedio de ventas" else "sum"}
)

st.subheader(f"📊 Comparación de {titulo_metrica} por Provincia — {anio}")
st.bar_chart(df_prov.set_index("provincia")[columna_valor])
