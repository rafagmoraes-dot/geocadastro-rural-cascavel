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

st_autorefresh(interval=15000, key="atualizacao_automatica")

URL_PLANILHA = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSmKq5S5dpSJBpbmPiP8cpR2K3h3hoYMpmf6NJDpNSvVVyxLnxAxEJFhePInJgvbYvrbKhMvMN1e1pt/pub?output=csv"

@st.cache_data(ttl=60)
def carregar_dados():
    gdf_geo = gpd.read_file("cadastro_cascavel.geojson")
    cascavel = gpd.read_file("cascavel.geojson")
    tabela = pd.read_csv(URL_PLANILHA)

    gdf_geo["id"] = pd.to_numeric(
        gdf_geo["id"],
        errors="coerce"
    ).fillna(-1).astype(int).astype(str)

    tabela["id"] = pd.to_numeric(
        tabela["id"],
        errors="coerce"
    ).fillna(-1).astype(int).astype(str)

    gdf = gdf_geo[["id", "geometry"]].merge(
        tabela,
        on="id",
        how="left"
    )

    gdf["id"] = pd.to_numeric(
        gdf["id"],
        errors="coerce"
    ).fillna(-1).astype(int).astype(str)

    gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs=gdf_geo.crs)

    return gdf, cascavel

gdf, cascavel = carregar_dados()

st.title("GeoCadastro Rural - Cascavel")
st.write("Sistema WebGIS dinâmico para consulta da situação fundiária dos imóveis rurais do município de Cascavel.")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total de imóveis", len(gdf))

with col2:
    st.metric("Titulados", len(gdf[gdf["Situacao"] == "Titulado"]))

with col3:
    st.metric("Pendentes", len(gdf[gdf["Situacao"] == "Pendente de titulação"]))

with col4:
    st.metric("Área total (ha)", round(gdf["Área (ha)"].sum(), 2))

st.sidebar.header("Filtros")

situacao = st.sidebar.selectbox(
    "Situação",
    ["Todos", "Titulado", "Pendente de titulação"]
)

busca_proprietario = st.sidebar.text_input("Buscar por proprietário")
busca_imovel = st.sidebar.text_input("Buscar por imóvel")

area_min = float(gdf["Área (ha)"].min())
area_max = float(gdf["Área (ha)"].max())

faixa_area = st.sidebar.slider(
    "Filtrar por área (ha)",
    min_value=area_min,
    max_value=area_max,
    value=(area_min, area_max)
)

gdf_filtrado = gdf.copy()

if situacao != "Todos":
    gdf_filtrado = gdf_filtrado[gdf_filtrado["Situacao"] == situacao]

if busca_proprietario:
    gdf_filtrado = gdf_filtrado[
        gdf_filtrado["Proprietario"].str.contains(
            busca_proprietario,
            case=False,
            na=False
        )
    ]

if busca_imovel:
    gdf_filtrado = gdf_filtrado[
        gdf_filtrado["Imovel"].str.contains(
            busca_imovel,
            case=False,
            na=False
        )
    ]

gdf_filtrado = gdf_filtrado[
    (gdf_filtrado["Área (ha)"] >= faixa_area[0]) &
    (gdf_filtrado["Área (ha)"] <= faixa_area[1])
]

st.sidebar.header("Destaque")

ids_disponiveis = ["Nenhum"] + sorted(
    gdf_filtrado["id"].dropna().astype(str).unique().tolist(),
    key=lambda x: int(x) if x.isdigit() else 999999
)

id_selecionado = st.sidebar.selectbox(
    "Destacar imóvel pelo ID",
    ids_disponiveis
)

if id_selecionado == "Nenhum":
    id_selecionado = None
    
if "id_destacado" not in st.session_state:
    st.session_state["id_destacado"] = None

id_selecionado = st.session_state["id_destacado"]

m = folium.Map(
    location=[-24.95, -53.45],
    zoom_start=10,
    tiles="CartoDB Positron"
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
                fields=[
                    "id",
                    "Proprietario",
                    "Imovel",
                    "Numero",
                    "Situacao",
                    "Área (ha)",
                    "Município",
                    "UF",
                    "Observação",
                    "Responsável",
                    "Data de Atualização"
                ],
                aliases=[
                    "ID:",
                    "Proprietário:",
                    "Imóvel:",
                    "Número:",
                    "Situação:",
                    "Área (ha):",
                    "Município:",
                    "UF:",
                    "Observação:",
                    "Responsável:",
                    "Data de atualização:"
                ],
                localize=True,
                labels=True
            )
        ).add_to(m)

adicionar_camada(
    gdf_filtrado[gdf_filtrado["Situacao"] == "Titulado"],
    "Imóveis titulados",
    "green"
)

adicionar_camada(
    gdf_filtrado[gdf_filtrado["Situacao"] == "Pendente de titulação"],
    "Imóveis pendentes de titulação",
    "red"
)

if id_selecionado is not None:
    gdf_selecionado = gdf_filtrado[gdf_filtrado["id"] == id_selecionado]

    if len(gdf_selecionado) > 0:
        folium.GeoJson(
            data=gdf_selecionado,
            show=True,
            control=False,
            style_function=lambda feature: {
                "fillColor": "yellow",
                "color": "yellow",
                "weight": 6,
                "fillOpacity": 0.35
            }
        ).add_to(m)
        
            popup=folium.GeoJsonPopup(
                fields=[
                    "id",
                    "Proprietario",
                    "Imovel",
                    "Numero",
                    "Situacao",
                    "Área (ha)",
                    "Município",
                    "UF",
                    "Observação",
                    "Responsável",
                    "Data de Atualização"
                ],
                aliases=[
                    "ID:",
                    "Proprietário:",
                    "Imóvel:",
                    "Número:",
                    "Situação:",
                    "Área (ha):",
                    "Município:",
                    "UF:",
                    "Observação:",
                    "Responsável:",
                    "Data de atualização:"
                ],
                localize=True,
                labels=True
            )
        ).add_to(m)

legend_html = '''
<div style="
position: fixed;
bottom: 50px;
left: 50px;
width: 190px;
background-color: white;
border:2px solid grey;
z-index:9999;
font-size:14px;
padding: 10px;
border-radius: 8px;
">
<b>Legenda</b><br>

<span style="
display:inline-block;
width:12px;
height:12px;
background:green;
margin-right:5px;">
</span>
Imóveis titulados<br>

<span style="
display:inline-block;
width:12px;
height:12px;
background:red;
margin-right:5px;">
</span>
Pendentes de titulação<br>

<span style="
display:inline-block;
width:18px;
height:0px;
border-top:4px solid #003366;
margin-right:5px;">
</span>
Limite de Cascavel

</div>
'''

m.get_root().html.add_child(folium.Element(legend_html))

m.get_root().html.add_child(folium.Element(legend_html))

if id_selecionado is not None:
    gdf_selecionado = gdf_filtrado[gdf_filtrado["id"] == id_selecionado]

    if len(gdf_selecionado) > 0:
        folium.GeoJson(
            gdf_selecionado,
            name=f"Imóvel selecionado - ID {id_selecionado}",
            style_function=lambda feature: {
                "fillColor": "yellow",
                "color": "yellow",
                "weight": 6,
                "fillOpacity": 0.35
            }
        ).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

st.subheader("Mapa interativo dos imóveis")
st.write(f"Imóveis exibidos no mapa: **{len(gdf_filtrado)}**")
st.caption("A tabela de atributos é lida de uma planilha Google Sheets publicada como CSV e atualizada automaticamente a cada 15 segundos.")

st_folium(m, width=1200, height=650)

st.subheader("Tabela de imóveis filtrados")

tabela = gdf_filtrado[
    [
        "id",
        "Proprietario",
        "Imovel",
        "Numero",
        "Situacao",
        "Área (ha)",
        "Município",
        "UF",
        "Observação",
        "Responsável",
        "Data de Atualização"
    ]
]

evento_tabela = st.dataframe(
    tabela,
    use_container_width=True,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row"
)

if evento_tabela.selection.rows:
    linha = evento_tabela.selection.rows[0]
    novo_id = str(tabela.iloc[linha]["id"])

    if st.session_state["id_destacado"] != novo_id:
        st.session_state["id_destacado"] = novo_id
        st.rerun()

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
    contagem = gdf_filtrado["Situacao"].value_counts().reset_index()
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
        .groupby("Situacao")["Área (ha)"]
        .sum()
        .reset_index()
    )

    area_situacao.columns = ["Situação", "Área (ha)"]

    fig_barra = px.bar(
        area_situacao,
        x="Situação",
        y="Área (ha)",
        title="Área total por situação fundiária"
    )

    st.plotly_chart(fig_barra, use_container_width=True)
