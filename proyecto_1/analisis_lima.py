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
    """Carga CSV desde la ruta indicada."""
    try:
        return pd.read_csv(filepath, sep='|')
    except Exception as e:
        st.error(f"Error al cargar {filepath}: {e}")
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
# FUNCIONES DE GRÁFICOS ROBUSTAS
# -----------------------------

def plot_scatter(df):
    if df.empty:
        st.warning("No hay datos para generar el scatter plot. Selecciona al menos un año y una provincia.")
        return

    promedios = df.groupby(['provincia', 'año'])[['venta_prom', 'trabajador', 'experiencia']].mean().reset_index()
    if promedios.empty:
        st.warning("No hay datos promedio para generar el scatter plot.")
        return

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
    fig.update_traces(showlegend=True)
    fig.update_layout(
        legend_title_text="Año",
        legend=dict(
            orientation='h',
            y=-0.2,
            x=0,
            xanchor='left',
            yanchor='top',
            itemsizing='constant'
        ),
        legend_itemclick=False,
        legend_itemdoubleclick=False,
        margin=dict(b=80)
    )
    st.plotly_chart(fig, use_container_width=True)


def plot_bars(df):
    if df.empty:
        st.warning("No hay datos para generar el gráfico de barras.")
        return

    ventas = df.groupby(['provincia', 'año'])['venta_prom'].mean().reset_index()
    if ventas.empty:
        st.warning("No hay datos promedio de venta para generar el gráfico de barras.")
        return

    ventas["venta_millones"] = ventas["venta_prom"] / 1_000_000
    fig = px.bar(
        ventas,
        x="provincia",
        y="venta_millones",
        color="año",
        barmode="group",
        labels={"venta_millones": "Venta Promedio (Millones S/.)"},
    )
    st.plotly_chart(fig, use_container_width=True)

def plot_heatmap(df):
    if df.empty:
        st.warning("No hay datos para generar el heatmap.")
        return

    ventas_totales = df.groupby(['provincia', 'año'])['venta_prom'].sum().reset_index()
    if ventas_totales.empty:
        st.warning("No hay datos de ventas totales para generar el heatmap.")
        return

    ventas_totales["venta_millones"] = ventas_totales["venta_prom"] / 1_000_000
    pivot = ventas_totales.pivot(index="provincia", columns="año", values="venta_millones")
    if pivot.empty:
        st.warning("No hay datos para generar el heatmap después de pivotear.")
        return

    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="YlGnBu", ax=ax)
    ax.set_title("Ventas Totales por Provincia (Millones de S/.)")
    ax.set_xlabel("Año")
    ax.set_ylabel("Provincia")
    st.pyplot(fig)


def plot_correlation(df):
    if df.empty:
        st.warning("No hay datos para generar la matriz de correlación.")
        return

    corr_df = df[['venta_prom', 'trabajador', 'experiencia']]
    if corr_df.empty:
        st.warning("No hay datos válidos para calcular la correlación.")
        return

    corr = corr_df.corr()
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.heatmap(corr, annot=True, cmap="coolwarm", ax=ax)
    ax.set_title("Correlación entre Venta, Trabajadores y Experiencia")
    st.pyplot(fig)


def plot_linear_regression(df):
    if df.empty:
        st.warning("No hay datos para generar la regresión lineal.")
        return

    st.subheader("📈 Regresión Lineal: Venta vs Trabajadores")
    show_points = st.checkbox("Mostrar puntos en la regresión lineal", value=False)

    df_plot = df.copy()
    df_plot['venta_prom_millones'] = df_plot['venta_prom'] / 1_000_000
    if df_plot.empty:
        st.warning("No hay datos válidos para la regresión lineal.")
        return

    fig, ax = plt.subplots(figsize=(6,4))
    sns.regplot(
        data=df_plot,
        x="trabajador",
        y="venta_prom_millones",
        scatter=show_points,
        line_kws={"color":"red"},
        ci=95
    )
    ax.set_xlabel("Número de Trabajadores")
    ax.set_ylabel("Venta Promedio (Millones S/.)")
    ax.set_title("Regresión Lineal: Venta vs Trabajadores")
    st.pyplot(fig)


def plot_caja_bigotes(df):
    if df.empty:
        st.warning("No hay datos para generar el boxplot.")
        return

    col1, col2 = st.columns(2)
    with col1:
        p_low = st.number_input("Percentil inferior (0-1)", value=0.01, step=0.01, format="%.2f")
    with col2:
        p_high = st.number_input("Percentil superior (0-1)", value=0.90, step=0.01, format="%.2f")

    if not (0 <= p_low <= 1) or not (0 <= p_high <= 1):
        st.error("Los percentiles deben estar entre 0 y 1.")
        return
    if p_low > p_high:
        st.error("El percentil inferior debe ser menor o igual al percentil superior.")
        return

    df_plot = df.copy()
    df_plot['venta_prom_millones'] = df_plot['venta_prom'] / 1_000_000

    lower = df_plot['venta_prom_millones'].quantile(p_low)
    upper = df_plot['venta_prom_millones'].quantile(p_high)
    df_filtered = df_plot[(df_plot['venta_prom_millones'] >= lower) & (df_plot['venta_prom_millones'] <= upper)]

    if df_filtered.empty:
        st.warning("No hay datos en los percentiles seleccionados.")
        return

    max_exp = df_filtered['experiencia'].max()
    if pd.isna(max_exp) or max_exp == 0:
        st.warning("No hay valores válidos de experiencia para graficar.")
        return

    bins = [0, 5, 10, 20, 30, 50, max_exp]
    labels = ["0-5","6-10","11-20","21-30","31-50","50+"]
    df_filtered['experiencia_bin'] = pd.cut(df_filtered['experiencia'], bins=bins, labels=labels, include_lowest=True)

    fig, ax = plt.subplots(figsize=(12,6))
    sns.boxplot(
        y='experiencia_bin',
        x='venta_prom_millones',
        data=df_filtered,
        palette="Set3",
        orient='h'
    )
    ax.set_xlabel("Venta Promedio (Millones S/.)")
    ax.set_ylabel("Experiencia (años, bins)")
    ax.set_title(f"Distribución de Ventas por Experiencia (Percentiles {p_low*100:.0f}%-{p_high*100:.0f}%)")
    plt.tight_layout()
    st.pyplot(fig)
    st.markdown("*Nota: Se han excluido valores extremadamente dispersos para mejorar la legibilidad.*")

# -----------------------------
# MAIN
# -----------------------------
def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(BASE_DIR, '..', 'data', 'proyecto_1')
    
    file_2022 = os.path.join(data_folder, 'GRAN_EMPRESA_2022_MANUFACTURA.csv')
    file_2023 = os.path.join(data_folder, 'GRAN_EMPRESA_2023_MANUFACTURA.csv')
    file_2024 = os.path.join(data_folder, 'GRAN_EMPRESA_2024_MANUFACTURA.csv')

    df_2022 = load_data(file_2022)
    df_2023 = load_data(file_2023)
    df_2024 = load_data(file_2024)

    if df_2022 is None or df_2023 is None or df_2024 is None:
        st.error("No se pudieron cargar los datos. Verifica que los archivos existan en la carpeta 'data'.")
        return

    combined_df = pd.concat([
        prepare_df(df_2022, 2022),
        prepare_df(df_2023, 2023),
        prepare_df(df_2024, 2024)
    ])

    years_selected = st.multiselect("Selecciona los años a visualizar", [2022, 2023, 2024], default=[2022, 2023, 2024])
    filtered_df = combined_df[combined_df["año"].isin(years_selected)]

    all_provinces = filtered_df["provincia"].unique().tolist()
    selected_provinces = st.multiselect("Selecciona las provincias a visualizar", all_provinces, default=all_provinces)
    filtered_df = filtered_df[filtered_df["provincia"].isin(selected_provinces)]

    # -----------------------------
    # Fila 1: Scatter y Heatmap
    # -----------------------------
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📊 Relación entre Venta, Trabajadores y Experiencia")
        plot_scatter(filtered_df)
    with col2:
        st.subheader("📊 Ventas Totales por Provincia")
        plot_heatmap(filtered_df)

    # -----------------------------
    # Fila 2: Barras y Correlación
    # -----------------------------
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("📊 Comparación de Venta Promedio por Provincia")
        plot_bars(filtered_df)
    with col4:
        st.subheader("📊 Matriz de Correlación")
        plot_correlation(filtered_df)

    # -----------------------------
    # Fila 3: Regresión Lineal y Boxplot (caja y bigotes)
    # -----------------------------
    col5, col6 = st.columns(2)
    with col5:
        plot_linear_regression(filtered_df)
    with col6:
        plot_caja_bigotes(filtered_df)

if __name__ == "__main__":
    main()

    # ---------------- FOOTER ----------------
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.85rem; color:gray;'>
    © 2025 · Miguel Olivero · Todos los derechos reservados · 
    <a href='https://datosabiertos.gob.pe/dataset/desempe%C3%B1o-econ%C3%B3mico-de-las-grandes-empresas-manufactureras-ministerio-de-la-produccion' target='_blank' style='color:gray; text-decoration:underline;'>Fuentes</a>
    </div>
    """, unsafe_allow_html=True)
