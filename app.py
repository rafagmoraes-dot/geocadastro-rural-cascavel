import streamlit as st
import geopandas as gpd

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


st.title("🌎 GeoCadastro Rural - Cascavel")

st.markdown("""
### Sistema WebGIS para consulta da situação fundiária dos imóveis rurais do município de Cascavel.

O sistema permite:

- 🗺️ Visualização dos imóveis em mapa interativo;
- 🔎 Pesquisa por proprietário e imóvel;
- 📏 Filtragem por área;
- 🟢 Identificação dos imóveis titulados;
- 🔴 Identificação dos imóveis pendentes de titulação;
- 📊 Análise estatística dos dados.
""")

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total de imóveis",
        len(gdf)
    )

with col2:
    st.metric(
        "Titulados",
        len(gdf[gdf["Situação"]=="Titulado"])
    )

with col3:
    st.metric(
        "Pendentes",
        len(gdf[gdf["Situação"]=="Pendente de titulação"])
    )

with col4:
    st.metric(
        "Área total (ha)",
        round(gdf["Área_ha"].sum(),2)
    )

st.divider()

st.info(
"""
⬅️ Utilize o menu lateral para navegar entre as páginas do sistema.

Próximas páginas:

🗺️ Mapa Interativo

📊 Estatísticas

🔴 Imóveis Pendentes

📋 Dados

ℹ️ Sobre o Projeto
"""
)
