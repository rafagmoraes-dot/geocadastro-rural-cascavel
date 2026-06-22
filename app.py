import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="GeoCadastro Rural - Cascavel",
    layout="wide"
)

@st.cache_data
def carregar_dados():
    gdf = gpd.read_file("cadastro_cascavel.geojson")

    gdf = gdf.rename(columns={
        "Proprietar": "Proprietário",
        "Imovel": "Imóvel",
        "Numero": "Número",
        "Situacao": "Situação",
        "Área (ha)": "Área_ha",
        "Municipio": "Município"
    })

    return gdf

gdf = carregar_dados()

st.title("GeoCadastro Rural - Cascavel")
st.write("Sistema WebGIS para consulta da situação fundiária dos imóveis rurais do município de Cascavel.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de imóveis", len(gdf))

with col2:
    st.metric("Titulados", len(gdf[gdf["Situação"] == "Titulado"]))

with col3:
    st.metric("Pendentes", len(gdf[gdf["Situação"] == "Pendente de titulação"]))

with col4:
    st.metric("Área total (ha)", round(gdf["Área_ha"].sum(), 2))

st.sidebar.header("Filtros")

situacao = st.sidebar.selectbox(
    "Situação",
    ["Todos", "Titulado", "Pendente de titulação"]
)

if situacao == "Todos":
    gdf_filtrado = gdf.copy()
else:
    gdf_filtrado = gdf[gdf["Situação"] == situacao].copy()

def estilo_imovel(feature):
    situacao = feature["properties"]["Situação"]

    if situacao == "Titulado":
        cor = "green"
    else:
        cor = "red"

    return {
        "fillColor": cor,
        "color": cor,
        "weight": 1,
        "fillOpacity": 0.55
    }

m = folium.Map(
    location=[-24.95, -53.45],
    zoom_start=10
)

folium.GeoJson(
    gdf_filtrado,
    style_function=estilo_imovel,
    popup=folium.GeoJsonPopup(
        fields=[
            "Proprietário",
            "Imóvel",
            "Número",
            "Situação",
            "Área_ha",
            "Município"
        ],
        aliases=[
            "Proprietário:",
            "Imóvel:",
            "Número:",
            "Situação:",
            "Área (ha):",
            "Município:"
        ],
        localize=True,
        labels=True
    )
).add_to(m)

st.subheader("Mapa interativo dos imóveis")
st_folium(m, width=1200, height=650)
