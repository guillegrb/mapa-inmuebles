import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.geocoders import OpenCage

# Configuración de la API de OpenCage
API_KEY = "87b6265a9a23449ca54620eeff3f5ea4"

st.set_page_config(page_title="Mapa de Inmuebles", layout="wide")
st.title("🗺️ Mapa de Inmuebles con Ahorro")

uploaded_file = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if not {"Dirección", "Precio", "Enlace", "Porcentaje de ahorro"}.issubset(df.columns):
        st.error("El archivo debe contener las columnas: Dirección, Precio, Enlace y Porcentaje de ahorro")
    else:
        geolocator = OpenCage(API_KEY)
        m = folium.Map(location=[-15.78, -47.92], zoom_start=5)
        marker_cluster = MarkerCluster().add_to(m)

        for _, row in df.iterrows():
            try:
                location = geolocator.geocode(row['Dirección'])
                if location:
                    popup_html = f"""<b>Precio:</b> {row['Precio']}<br>
<b>Ahorro:</b> {row['Porcentaje de ahorro']}<br>
<a href="{row['Enlace']}" target="_blank">Ver enlace</a>"""
                    folium.Marker(
                        location=[location.latitude, location.longitude],
                        popup=popup_html,
                        tooltip=row['Dirección']
                    ).add_to(marker_cluster)
            except Exception as e:
                st.warning(f"No se pudo localizar: {row['Dirección']}")

        st_folium(m, width=1000, height=600)