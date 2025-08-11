import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊",
    layout="wide"
)

# --- Carregamento dos dados ---
df = pd.read_csv("https://raw.githubusercontent.com/guilhermeonrails/data-jobs/refs/heads/main/salaries.csv")

# --- Tradução e Limpeza dos Dados ---
# Mapeia os valores codificados para nomes mais descritivos em português para melhorar a legibilidade dos filtros e gráficos.
mapa_senioridade = {
    'EN': 'Iniciante',
    'MI': 'Intermediário',
    'SE': 'Sênior',
    'EX': 'Executivo'
}
mapa_contrato = {
    'FT': 'Tempo Integral',
    'PT': 'Meio Período',
    'CT': 'Contrato',
    'FL': 'Freelance'
}
mapa_tamanho_empresa = {
    'S': 'Pequena (até 50)',
    'M': 'Média (51 a 250)',
    'L': 'Grande (+250)'
}
df['experience_level'] = df['experience_level'].map(mapa_senioridade)
df['employment_type'] = df['employment_type'].map(mapa_contrato)
df['company_size'] = df['company_size'].map(mapa_tamanho_empresa)

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔎 Filtros")

# Filtro de Ano
anos_disponiveis = sorted(df['work_year'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['experience_level'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['employment_type'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['company_size'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do Dataframe ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
df_filtrado = df[
    (df['work_year'].isin(anos_selecionados)) &
    (df['experience_level'].isin(senioridades_selecionadas)) &
    (df['employment_type'].isin(contratos_selecionados)) &
    (df['company_size'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
st.title("🎲 Dashboard de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty:
    salario_medio = df_filtrado['salary_in_usd'].mean()
    salario_maximo = df_filtrado['salary_in_usd'].max()
    total_registros = df_filtrado.shape[0]
    cargo_mais_frequente = df_filtrado['job_title'].mode()[0]
else:
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, "N/A"

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário médio", f"${salario_medio:,.0f}")
col2.metric("Salário máximo", f"${salario_maximo:,.0f}")
col3.metric("Total de registros", f"{total_registros:,}")
col4.metric("Cargo mais frequente", cargo_mais_frequente)

st.markdown("---")

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not df_filtrado.empty:
        # Agrupa por cargo, calcula a média salarial, pega os 10 maiores e ordena para o gráfico
        top_cargos = df_filtrado.groupby('job_title')['salary_in_usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        grafico_cargos = px.bar(
            top_cargos,
            x='salary_in_usd',
            y='job_title',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'salary_in_usd': 'Média salarial anual (USD)', 'job_title': ''}
        )
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2:
    if not df_filtrado.empty:
        # Cria um histograma para ver a distribuição dos salários
        grafico_hist = px.histogram(
            df_filtrado,
            x='salary_in_usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'salary_in_usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not df_filtrado.empty:
        # Mapeia a proporção de trabalho remoto para categorias legíveis
        tipo_trabalho_map = {100: 'Remoto', 50: 'Híbrido', 0: 'Presencial'}
        remoto_contagem = df_filtrado['remote_ratio'].map(tipo_trabalho_map).value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'contagem'] # Renomeia colunas para o gráfico

        # Cria um gráfico de pizza para mostrar a proporção
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='contagem',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

with col_graf4:
    if not df_filtrado.empty:
        # Filtra apenas para a vaga de "Data Scientist" para o mapa
        df_ds = df_filtrado[df_filtrado['job_title'] == 'Data Scientist']
        # Agrupa por país de residência para calcular o salário médio
        media_ds_pais = df_ds.groupby('employee_residence')['salary_in_usd'].mean().reset_index()
        # Cria o mapa coroplético
        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='employee_residence',
            color='salary_in_usd',
            color_continuous_scale='rdylgn',
            title='Salário médio de Cientista de Dados por país',
            labels={'salary_in_usd': 'Salário médio (USD)', 'employee_residence': 'País'}
        )
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados")
st.dataframe(df_filtrado)