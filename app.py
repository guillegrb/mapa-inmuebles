
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from time import sleep
from io import BytesIO

st.set_page_config(page_title="Mapa de Inmuebles", layout="wide")

st.title("📍 Visualizador de inmuebles en mapa")

# Subir archivo Excel
archivo = st.file_uploader("📁 Sube tu archivo Excel (.xlsx)", type=["xlsx"])

if archivo:
    # Leer el Excel
    df = pd.read_excel(archivo)

    columnas_esperadas = {"Dirección", "Precio", "Enlace", "Porcentaje de ahorro"}
    if not columnas_esperadas.issubset(df.columns):
        st.error("❌ El archivo debe tener las columnas: Dirección, Precio, Enlace, Porcentaje de ahorro")
    else:
        # Filtros antes de geocodificar
        with st.sidebar:
            st.header("🔎 Filtros")
            ahorro_min = st.slider("Porcentaje mínimo de ahorro (%)", 0, 100, 0)
            precio_max = st.number_input("Precio máximo (€)", value=1_000_000)

        df_filtrado = df[
            (df["Porcentaje de ahorro"] >= ahorro_min) &
            (df["Precio"] <= precio_max)
        ]

        if df_filtrado.empty:
            st.warning("⚠️ No hay resultados que cumplan los filtros.")
        else:
            geolocator = Nominatim(user_agent="app_mapa_inmuebles")
            coordenadas = []

            with st.spinner("🔍 Geocodificando direcciones..."):
                for direccion in df_filtrado["Dirección"]:
                    try:
                        location = geolocator.geocode(direccion)
                        if location:
                            coordenadas.append((location.latitude, location.longitude))
                        else:
                            coordenadas.append((None, None))
                    except:
                        coordenadas.append((None, None))
                    sleep(1)

            df_filtrado["Latitud"] = [lat for lat, lon in coordenadas]
            df_filtrado["Longitud"] = [lon for lat, lon in coordenadas]

            if df_filtrado["Latitud"].notna().sum() == 0:
                st.warning("⚠️ No se pudo geolocalizar ninguna dirección.")
            else:
                lat_init = df_filtrado["Latitud"].dropna().iloc[0]
                lon_init = df_filtrado["Longitud"].dropna().iloc[0]
                mapa = folium.Map(location=[lat_init, lon_init], zoom_start=13)

                for _, row in df_filtrado.iterrows():
                    if pd.notna(row["Latitud"]) and pd.notna(row["Longitud"]):
                        popup = folium.Popup(
                            f"<b>Dirección:</b> {row['Dirección']}<br>"
                            f"<b>Precio:</b> {row['Precio']}<br>"
                            f"<b>Ahorro:</b> {row['Porcentaje de ahorro']}<br>"
                            f"<a href='{row['Enlace']}' target='_blank'>Ver propiedad</a>",
                            max_width=300
                        )
                        folium.Marker(
                            location=[row["Latitud"], row["Longitud"]],
                            popup=popup,
                            icon=folium.Icon(color="blue", icon="home")
                        ).add_to(mapa)

                st.success("✅ Mapa generado:")
                st_data = st_folium(mapa, width=1200, height=600)

                # Descargar como HTML
                html_out = "mapa_inmuebles.html"
                mapa.save(html_out)
                with open(html_out, "rb") as f:
                    st.download_button("💾 Descargar mapa en HTML", f, file_name="mapa_inmuebles.html")
