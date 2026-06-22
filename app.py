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

# Indicadores gerais
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de imóveis", len(gdf))

with col2:
    st.metric("Titulados", len(gdf[gdf["Situação"] == "Titulado"]))

with col3:
    st.metric("Pendentes", len(gdf[gdf["Situação"] == "Pendente de titulação"]))

with col4:
    st.metric("Área total (ha)", round(gdf["Área_ha"].sum(), 2))

# Sidebar
st.sidebar.header("Filtros")

situacao = st.sidebar.selectbox(
    "Situação",
    ["Todos", "Titulado", "Pendente de titulação"]
)

busca_proprietario = st.sidebar.text_input("Buscar por proprietário")

busca_imovel = st.sidebar.text_input("Buscar por imóvel")

area_min = float(gdf["Área_ha"].min())
area_max = float(gdf["Área_ha"].max())

faixa_area = st.sidebar.slider(
    "Filtrar por área (ha)",
    min_value=area_min,
    max_value=area_max,
    value=(area_min, area_max)
)

# Aplicar filtros
gdf_filtrado = gdf.copy()

if situacao != "Todos":
    gdf_filtrado = gdf_filtrado[gdf_filtrado["Situação"] == situacao]

if busca_proprietario:
    gdf_filtrado = gdf_filtrado[
        gdf_filtrado["Proprietário"].str.contains(
            busca_proprietario,
            case=False,
            na=False
        )
    ]

if busca_imovel:
    gdf_filtrado = gdf_filtrado[
        gdf_filtrado["Imóvel"].str.contains(
            busca_imovel,
            case=False,
            na=False
        )
    ]

gdf_filtrado = gdf_filtrado[
    (gdf_filtrado["Área_ha"] >= faixa_area[0]) &
    (gdf_filtrado["Área_ha"] <= faixa_area[1])
]

st.subheader("Mapa interativo dos imóveis")
st.write(f"Imóveis exibidos no mapa: **{len(gdf_filtrado)}**")

# Estilo do mapa
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

st_folium(m, width=1200, height=650)

# Tabela
st.subheader("Tabela de imóveis filtrados")

st.dataframe(
    gdf_filtrado[
        ["Proprietário", "Imóvel", "Número", "Situação", "Área_ha", "Município", "UF"]
    ],
    use_container_width=True
)
