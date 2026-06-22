import streamlit as st
import geopandas as gpd
import pandas as pd
import folium
import plotly.express as px
from streamlit_folium import st_folium
from streamlit_autorefresh import st_autorefresh

st.set_page_config(
    page_title="GeoCadastro Rural - Cascavel",
    layout="wide"
)

st_autorefresh(interval=60000, key="atualizacao_automatica")

URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSnrBKdKj_i4-IGlSc1dS_Vn9Go0_9whzxvwf6JL_zFW9RBfiJUSUdgdBseowgwezCNIVUGMUo-Blw_/pub?output=csv"

@st.cache_data(ttl=60)
def carregar_dados():
    gdf = gpd.read_file("cadastro_cascavel.geojson")
    cascavel = gpd.read_file("cascavel.geojson")
    status = pd.read_csv(URL_PLANILHA)

    gdf = gdf.rename(columns={
        "Proprietar": "Proprietário",
        "Imovel": "Imóvel",
        "Numero": "Número",
        "Municipio": "Município",
        "Área (ha)": "Área_ha"
    })

    # Cria chave pela ordem das linhas: 0, 1, 2, 3...
    gdf = gdf.reset_index(drop=True)
    gdf["id_planilha"] = gdf.index.astype(str)

    status["id_planilha"] = status["id"].astype(str)
    status["Situacao"] = status["Situacao"].str.strip()

    gdf = gdf.drop(columns=["Situacao"], errors="ignore")

    gdf = gdf.merge(
        status[["id_planilha", "Situacao"]],
        on="id_planilha",
        how="left"
    )

    gdf = gdf.rename(columns={
        "Situacao": "Situação"
    })

    return gdf, cascavel

gdf, cascavel = carregar_dados()

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

gdf_filtrado = gdf.copy()

if situacao != "Todos":
    gdf_filtrado = gdf_filtrado[gdf_filtrado["Situação"] == situacao]

if busca_proprietario:
    gdf_filtrado = gdf_filtrado[
        gdf_filtrado["Proprietário"].str.contains(busca_proprietario, case=False, na=False)
    ]

if busca_imovel:
    gdf_filtrado = gdf_filtrado[
        gdf_filtrado["Imóvel"].str.contains(busca_imovel, case=False, na=False)
    ]

gdf_filtrado = gdf_filtrado[
    (gdf_filtrado["Área_ha"] >= faixa_area[0]) &
    (gdf_filtrado["Área_ha"] <= faixa_area[1])
]

m = folium.Map(
    location=[-24.95, -53.45],
    zoom_start=10,
    tiles="OpenStreetMap"
)

folium.GeoJson(
    cascavel,
    name="Limite de Cascavel",
    style_function=lambda feature: {
        "fillColor": "transparent",
        "color": "#003366",
        "weight": 3,
        "fillOpacity": 0
    }
).add_to(m)

def adicionar_camada(dados, nome, cor):
    if len(dados) > 0:
        folium.GeoJson(
            dados,
            name=nome,
            style_function=lambda feature: {
                "fillColor": cor,
                "color": cor,
                "weight": 1,
                "fillOpacity": 0.55
            },
            popup=folium.GeoJsonPopup(
                fields=["Proprietário", "Imóvel", "Número", "Situação", "Área_ha", "Município"],
                aliases=["Proprietário:", "Imóvel:", "Número:", "Situação:", "Área (ha):", "Município:"],
                localize=True,
                labels=True
            )
        ).add_to(m)

adicionar_camada(
    gdf_filtrado[gdf_filtrado["Situação"] == "Titulado"],
    "Imóveis titulados",
    "green"
)

adicionar_camada(
    gdf_filtrado[gdf_filtrado["Situação"] == "Pendente de titulação"],
    "Imóveis pendentes de titulação",
    "red"
)

folium.LayerControl(collapsed=False).add_to(m)

st.subheader("Mapa interativo dos imóveis")
st.write(f"Imóveis exibidos no mapa: **{len(gdf_filtrado)}**")
st.caption("A situação fundiária é lida de uma planilha Google Sheets publicada como CSV e atualizada automaticamente a cada 60 segundos.")

st_folium(m, width=1200, height=650)

st.subheader("Tabela de imóveis filtrados")

tabela = gdf_filtrado[
    ["id_planilha", "Proprietário", "Imóvel", "Número", "Situação", "Área_ha", "Município", "UF"]
]

st.dataframe(tabela, use_container_width=True)

csv = tabela.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇️ Baixar dados filtrados em CSV",
    csv,
    "imoveis_filtrados.csv",
    "text/csv"
)

st.subheader("Estatísticas dos imóveis filtrados")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    contagem = gdf_filtrado["Situação"].value_counts().reset_index()
    contagem.columns = ["Situação", "Quantidade"]

    fig_pizza = px.pie(
        contagem,
        values="Quantidade",
        names="Situação",
        title="Distribuição por situação fundiária"
    )

    st.plotly_chart(fig_pizza, use_container_width=True)

with col_graf2:
    area_situacao = (
        gdf_filtrado
        .groupby("Situação")["Área_ha"]
        .sum()
        .reset_index()
    )

    fig_barra = px.bar(
        area_situacao,
        x="Situação",
        y="Área_ha",
        title="Área total por situação fundiária"
    )

    st.plotly_chart(fig_barra, use_container_width=True)
