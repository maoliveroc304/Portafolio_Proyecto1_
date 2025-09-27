import os

def main():
    # Definir carpeta de datos
    data_folder = 'data'  # si está en la misma carpeta que tu script, ajusta si es ruta absoluta

    # Cargar datos
    df_2022 = load_data(os.path.join(data_folder, 'GRAN_EMPRESA_2022_MANUFACTURA.csv'))
    df_2023 = load_data(os.path.join(data_folder, 'GRAN_EMPRESA_2023_MANUFACTURA.csv'))
    df_2024 = load_data(os.path.join(data_folder, 'GRAN_EMPRESA_2024_MANUFACTURA.csv'))

    if df_2022 is None or df_2023 is None or df_2024 is None:
        st.error("No se pudieron cargar los datos. Verifica las rutas de los archivos.")
        return

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
