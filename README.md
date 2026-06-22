# GeoCadastro Rural - Cascavel

## Descrição

Aplicação WebGIS desenvolvida em Python para visualização e consulta da situação fundiária dos imóveis rurais do município de Cascavel - PR.

O sistema integra dados espaciais em formato GeoJSON com uma base de atributos mantida em Google Sheets, permitindo atualização automática das informações e disponibilizando uma interface web interativa construída com Streamlit.

---

## Funcionalidades

- Visualização dos imóveis em mapa interativo;
- Diferenciação por situação fundiária;
- Filtros por:
  - Situação;
  - Proprietário;
  - Imóvel;
  - Área (ha);
- Pop-up com informações detalhadas;
- Destaque de imóvel selecionado;
- Tabela dinâmica de atributos;
- Exportação dos dados em CSV;
- Gráficos estatísticos;
- Atualização automática dos dados a cada 15 segundos.

---

## Tecnologias utilizadas

- Python
- Streamlit
- Pandas
- GeoPandas
- Folium
- Plotly
- Google Sheets
- GitHub

---

## Estrutura do projeto

```text
├── app.py
├── cadastro_cascavel.geojson
├── cascavel.geojson
├── requirements.txt
└── README.md
```

---

## Fluxo dos dados

```text
Google Sheets
        ↓
CSV publicado
        ↓
Pandas
        ↓
Merge com GeoJSON
        ↓
Folium + Plotly
        ↓
Streamlit
        ↓
Aplicação WebGIS
```

---

## Metodologia adotada

Optou-se por uma arquitetura simplificada, utilizando Google Sheets como banco de dados de atributos e arquivos GeoJSON para armazenamento das geometrias. Essa abordagem permite atualização automática das informações sem necessidade de APIs ou bancos de dados dedicados, tornando a solução mais simples, de baixo custo e de fácil manutenção.

---

## Aplicações

Esta metodologia pode ser empregada em:

- Prefeituras municipais;
- Secretarias de Agricultura;
- Projetos de regularização fundiária;
- Cooperativas e associações de produtores;
- Projetos acadêmicos;
- Pequenas equipes que necessitam de atualização frequente das informações.

---

## Autor

**Rafaela Gama de Moraes**

Geógrafa | Especialista em Engenharia e Gestão Ambiental

---

## Licença

Projeto desenvolvido para fins acadêmicos.
