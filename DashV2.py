import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Afastamentos 2025 - IBAMA",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Cores do tema IBAMA
CORES_IBAMA = ['#006600', '#FFCC00', '#0066CC', '#009933', '#FF9900', '#003366']

# Título principal
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #006600;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #006600, #009933);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .insight-box {
        background: linear-gradient(135deg, #F093FB, #F5576C);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        border-left: 5px solid #FF4757;
    }
    .alert-box {
        background: linear-gradient(135deg, #FFB347, #FF6B6B);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        border-left: 5px solid #FF4500;
    }
    </style>
    <h1 class="main-header">🌍 Dashboard de Afastamentos 2025 - IBAMA</h1>
""", unsafe_allow_html=True)

# Carregar os dados
@st.cache_data
def load_data():
    file_path = "DATA Afastamentos 2025.xlsx"
    df = pd.read_excel(file_path, sheet_name="Afastamentos 2025")
    return df

def safe_date_conversion(date_series):
    """Conversão segura de datas com múltiplos formatos"""
    result = pd.to_datetime(date_series, errors='coerce')
    
    mask_na = result.isna()
    if mask_na.any():
        result[mask_na] = pd.to_datetime(
            date_series[mask_na], 
            dayfirst=True, 
            errors='coerce'
        )
    
    return result

# ✅ MAPEAMENTO SIMPLIFICADO E TESTADO
COUNTRY_MAPPING = {
    'EUA': 'United States',
    'Suíça': 'Switzerland',
    'Bolívia': 'Bolivia',
    'Itália': 'Italy',
    'China': 'China',
    'Reino Unido': 'United Kingdom',
    'Peru': 'Peru',
    'França': 'France',
    'Espanha': 'Spain',
    'Bélgica': 'Belgium',
    'Japão': 'Japan',
    'Trinidad e Tobago': 'Trinidad and Tobago',
    'Equador': 'Ecuador',
    'Grécia': 'Greece',
    'Argentina': 'Argentina',
    'Alemanha': 'Germany',
    'Costa Rica': 'Costa Rica',
    'Países Baixos': 'Netherlands',
    'Áustria': 'Austria',
    'Dinamarca': 'Denmark',
    'Noruega': 'Norway',
    'República Tcheca': 'Czechia',
    'Panamá': 'Panama',
    'Uruguai': 'Uruguay',
    'Coreia do Sul': 'South Korea',
    'Tailândia': 'Thailand',
    'Chile': 'Chile',
    'Colômbia': 'Colombia',
    'Indonésia': 'Indonesia',
    'África do Sul': 'South Africa',
    'México': 'Mexico',
    'Canadá': 'Canada',
    'Guiana Francesa': 'French Guiana',
    'Quênia': 'Kenya',
    'Portugal': 'Portugal',
    'Uzbequistão': 'Uzbekistan',
    'Suriname': 'Suriname',
    'Antártida': 'Antarctica',
    'Brasil': 'Brazil',
}

# Mapeamento de códigos ISO para países
ISO_MAPPING = {
    'United States': 'USA',
    'Switzerland': 'CHE',
    'Bolivia': 'BOL',
    'Italy': 'ITA',
    'China': 'CHN',
    'United Kingdom': 'GBR',
    'Peru': 'PER',
    'France': 'FRA',
    'Spain': 'ESP',
    'Belgium': 'BEL',
    'Japan': 'JPN',
    'Trinidad and Tobago': 'TTO',
    'Ecuador': 'ECU',
    'Greece': 'GRC',
    'Argentina': 'ARG',
    'Germany': 'DEU',
    'Costa Rica': 'CRI',
    'Netherlands': 'NLD',
    'Austria': 'AUT',
    'Denmark': 'DNK',
    'Norway': 'NOR',
    'Czechia': 'CZE',
    'Panama': 'PAN',
    'Uruguay': 'URY',
    'South Korea': 'KOR',
    'Thailand': 'THA',
    'Chile': 'CHL',
    'Colombia': 'COL',
    'Indonesia': 'IDN',
    'South Africa': 'ZAF',
    'Mexico': 'MEX',
    'Canada': 'CAN',
    'French Guiana': 'GUF',
    'Kenya': 'KEN',
    'Portugal': 'PRT',
    'Uzbekistan': 'UZB',
    'Suriname': 'SUR',
    'Antarctica': 'ATA',
    'Brazil': 'BRA',
}

try:
    df = load_data()
    
    # =============================================================================
    # PRÉ-PROCESSAMENTO DOS DADOS
    # =============================================================================
    
    st.sidebar.header("🔧 Configurações de Processamento")
    debug_mode = st.sidebar.checkbox("Modo Debug (mostrar dados processados)")
    
    # Mostrar colunas disponíveis em debug
    if debug_mode:
        st.sidebar.write("🔍 Colunas disponíveis:", df.columns.tolist())
    
    # Filtrar viagens não canceladas
    df_original = df.copy()
    df = df[df['Cancelada?'] == 'Não']
    
    # Conversão robusta de datas
    date_columns = ['Data entrada na DAI', 'Início do Afastamento', 'Final do Afastamento']
    
    for col in date_columns:
        df[col] = safe_date_conversion(df[col])
    
    # Remover linhas com datas de início ou fim inválidas
    df = df.dropna(subset=['Início do Afastamento', 'Final do Afastamento'])
    
    # Calcular duração (garantindo valores positivos)
    df['Duração (dias)'] = (df['Final do Afastamento'] - df['Início do Afastamento']).dt.days
    
    # Verificar e corrigir durações negativas
    duracoes_negativas = (df['Duração (dias)'] < 0).sum()
    if duracoes_negativas > 0:
        mask_neg = df['Duração (dias)'] < 0
        df.loc[mask_neg, ['Início do Afastamento', 'Final do Afastamento']] = \
            df.loc[mask_neg, ['Final do Afastamento', 'Início do Afastamento']].values
        df['Duração (dias)'] = (df['Final do Afastamento'] - df['Início do Afastamento']).dt.days
    
    # Calcular antecedência
    df['Antecedência (dias)'] = (df['Início do Afastamento'] - df['Data entrada na DAI']).dt.days
    df = df[df['Antecedência (dias)'] >= 0]
    
    # ✅ CONVERSÃO SEGURA DE CUSTO
    if 'Custo' in df.columns:
        df['Custo'] = pd.to_numeric(df['Custo'], errors='coerce')
    
    # Indicadores de planejamento
    df['Bem_Planejado'] = df['Antecedência (dias)'] >= 30
    
    # Classificação de duração
    df['Tipo_Duracao'] = pd.cut(df['Duração (dias)'], 
                                bins=[0, 5, 10, 30, 365], 
                                labels=['Muito Curta (≤5d)', 'Curta (6-10d)', 'Média (11-30d)', 'Longa (>30d)'])
    
    # Classificação de antecedência
    df['Categoria_Antecedencia'] = pd.cut(df['Antecedência (dias)'],
                                          bins=[0, 15, 30, 365],
                                          labels=['Urgência (0-15d)', 'Aviso Prévio (15-30d)', 'Bem Planejada (30+d)'])
    
    # =============================================================================
    # PROCESSAMENTO DE PAÍSES
    # =============================================================================
    
    df['País'] = df['País'].astype(str).str.strip()
    
    def mapear_pais(pais_input):
        if pd.isna(pais_input) or str(pais_input).lower() in ['nan', 'none', 'null', '']:
            return None
        
        pais_input_str = str(pais_input).strip()
        
        if pais_input_str in COUNTRY_MAPPING:
            return COUNTRY_MAPPING[pais_input_str]
        
        for pais_pt, pais_en in COUNTRY_MAPPING.items():
            if pais_pt.lower() == pais_input_str.lower():
                return pais_en
        
        return None
    
    df['País_Inglês'] = df['País'].apply(mapear_pais)
    
    if debug_mode:
        st.sidebar.write("🔍 Debug - Países em inglês únicos:", sorted(df['País_Inglês'].dropna().unique()))
        st.sidebar.write("📊 Contagem:", df['País_Inglês'].value_counts())
    
    # =============================================================================
    # TRATAMENTO DE OUTROS CAMPOS - APENAS COLUNAS QUE EXISTEM
    # =============================================================================
    
    df['Diretoria'] = df['Diretoria'].fillna('Não Informado')
    df['Tipo de Viagem'] = df['Tipo de Viagem'].fillna('Não Informado')
    df['Gênero'] = df['Gênero'].fillna('Não Informado')
    df['Mês_Início'] = df['Início do Afastamento'].dt.month_name()
    df['Trimestre'] = 'T' + df['Início do Afastamento'].dt.quarter.astype(str)
    
    meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # =============================================================================
    # SIDEBAR COM FILTROS
    # =============================================================================
    
    st.sidebar.header("🔧 Filtros")
    
    diretorias_disponiveis = sorted([d for d in df['Diretoria'].unique() if d not in ['Não Informado', 'nan']])
    tipos_viagem_disponiveis = sorted([t for t in df['Tipo de Viagem'].unique() if t not in ['Não Informado', 'nan']])
    
    tipo_selecionado = st.sidebar.selectbox(
        "Tipo de Viagem:",
        options=["Todos"] + tipos_viagem_disponiveis
    )
    
    diretoria_selecionada = st.sidebar.selectbox(
        "Diretoria:",
        options=["Todas"] + diretorias_disponiveis
    )
    
    df_filtrado = df.copy()
    
    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Tipo de Viagem'] == tipo_selecionado]
    
    if diretoria_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Diretoria'] == diretoria_selecionada]
    
    # =============================================================================
    # AGREGAÇÕES PARA OS MAPAS
    # =============================================================================
    
    df_com_pais = df_filtrado[df_filtrado['País_Inglês'].notna()].copy()
    
    viagens_por_pais = df_com_pais.groupby('País_Inglês').agg({
        'País': 'count',
        'Servidor': 'nunique',
        'Duração (dias)': 'mean'
    }).reset_index()
    viagens_por_pais.columns = ['País', 'Total_Viagens', 'Servidores_Unicos', 'Duração_Media']
    viagens_por_pais['ISO_Code'] = viagens_por_pais['País'].map(ISO_MAPPING)
    
    viagens_por_mes = df_filtrado.groupby('Mês_Início').size().reset_index(name='Viagens')
    viagens_por_mes['Mês_Início'] = pd.Categorical(
        viagens_por_mes['Mês_Início'], 
        categories=meses_ordem, 
        ordered=True
    )
    viagens_por_mes = viagens_por_mes.sort_values('Mês_Início')
    
    # =============================================================================
    # MÉTRICAS PRINCIPAIS
    # =============================================================================
    
    total_viagens = df_filtrado.shape[0]
    total_servidores = df_filtrado['Servidor'].nunique()
    duracao_media = df_filtrado['Duração (dias)'].mean()
    antecedencia_media = df_filtrado['Antecedência (dias)'].mean()
    total_paises = df_com_pais['País_Inglês'].nunique()
    
    custo_total = 0
    custo_medio = 0
    if 'Custo' in df_filtrado.columns:
        custo_total = df_filtrado['Custo'].sum() if pd.notna(df_filtrado['Custo'].sum()) else 0
        custo_medio = df_filtrado['Custo'].mean() if pd.notna(df_filtrado['Custo'].mean()) else 0
    
    st.header("📊 Métricas Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <h3>{total_viagens}</h3>
                <p>Total de Viagens</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #FFCC00, #FF9900);">
                <h3>{total_servidores}</h3>
                <p>Servidores Envolvidos</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #0066CC, #003366);">
                <h3>{duracao_media:.1f}</h3>
                <p>Duração Média (dias)</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #009933, #006600);">
                <h3>{total_paises}</h3>
                <p>Países com Viagens</p>
            </div>
        """, unsafe_allow_html=True)
    
    # =============================================================================
    # MÉTRICAS AVANÇADAS
    # =============================================================================
    
    st.header("📈 Métricas Avançadas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #FF6B6B, #C92A2A);">
                <h3>{antecedencia_media:.0f}</h3>
                <p>Antecedência Média (dias)</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        max_viagens_mes = viagens_por_mes['Viagens'].max() if not viagens_por_mes.empty else 0
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #FFD93D, #FF9F43);">
                <h3>{max_viagens_mes:.0f}</h3>
                <p>Pico de Viagens (1 mês)</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        duracao_total = df_filtrado['Duração (dias)'].sum()
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #A8E6CF, #56CCF2);">
                <h3>{duracao_total:.0f}</h3>
                <p>Total de Dias Afastados</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Segunda linha de métricas
    if 'Custo' in df_filtrado.columns and custo_total > 0:
        col1, col2, col3 = st.columns(3)
        
        custo_por_viagem = custo_total / total_viagens if total_viagens > 0 else 0
        
        with col1:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #11998E, #38EF7D);">
                    <h3>R$ {custo_total:,.0f}</h3>
                    <p>Custo Total</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #EB3349, #F45C43);">
                    <h3>R$ {custo_por_viagem:,.0f}</h3>
                    <p>Custo/Viagem</p>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            pct_bem_planejado = (df_filtrado['Bem_Planejado'].sum() / total_viagens * 100) if total_viagens > 0 else 0
            st.markdown(f"""
                <div class="metric-card" style="background: linear-gradient(135deg, #4158D0, #C850C0);">
                    <h3>{pct_bem_planejado:.0f}%</h3>
                    <p>Viagens Bem Planejadas (30+ dias)</p>
                </div>
            """, unsafe_allow_html=True)
    
    # =============================================================================
    # MAPA MUNDI
    # =============================================================================
    
    st.header("🗺️ Mapa Mundi - Países Visitados")
    
    if not viagens_por_pais.empty and not viagens_por_pais['ISO_Code'].isna().all():
        try:
            fig_mapa_mundi = px.choropleth(
                viagens_por_pais,
                locations='ISO_Code',
                color='Total_Viagens',
                hover_name='País',
                hover_data={
                    'ISO_Code': False,
                    'Total_Viagens': True,
                    'Servidores_Unicos': True,
                    'Duração_Media': ':.1f'
                },
                color_continuous_scale='Greens',
                title='Distribuição de Viagens por País',
                labels={
                    'Total_Viagens': 'Viagens',
                    'Servidores_Unicos': 'Servidores',
                    'Duração_Media': 'Duração Média'
                }
            )
            
            fig_mapa_mundi.update_layout(
                geo=dict(
                    showframe=True,
                    showcoastlines=True,
                    projection_type='natural earth',
                    bgcolor='rgba(255, 255, 255, 1)'
                ),
                height=600,
                hovermode='closest',
                coloraxis_colorbar=dict(
                    title="Número de Viagens",
                    thickness=15,
                    len=0.7
                )
            )
            
            st.plotly_chart(fig_mapa_mundi, use_container_width=True)
            
        except Exception as e:
            st.warning(f"⚠️ Erro ao gerar mapa mundi: {str(e)}")
    else:
        st.warning("⚠️ Não foi possível gerar o mapa mundi. Verifique os dados de países.")
    
    # =============================================================================
    # ANÁLISE DETALHADA POR PAÍS
    # =============================================================================
    
    st.header("🌍 Análise Detalhada por País")
    
    if not viagens_por_pais.empty:
        fig_mapa = px.bar(
            viagens_por_pais.sort_values('Total_Viagens', ascending=True).tail(15),
            x='Total_Viagens',
            y='País',
            orientation='h',
            title='Top 15 Países com Mais Viagens',
            color='Total_Viagens',
            color_continuous_scale='Greens',
            height=500,
            hover_data={'Servidores_Unicos': True, 'Duração_Media': ':.1f'}
        )
        fig_mapa.update_layout(
            xaxis_title="Número de Viagens",
            yaxis_title="País",
            hovermode='closest'
        )
        st.plotly_chart(fig_mapa, use_container_width=True)
        
        st.subheader("📍 Análise de Viagens vs Duração Média")
        
        try:
            fig_scatter = go.Figure(data=[
                go.Scatter(
                    x=viagens_por_pais['Total_Viagens'],
                    y=viagens_por_pais['Duração_Media'],
                    mode='markers+text',
                    marker=dict(
                        size=viagens_por_pais['Servidores_Unicos'] * 2,
                        color=viagens_por_pais['Total_Viagens'],
                        colorscale='Greens',
                        showscale=True,
                        colorbar=dict(title="Viagens"),
                        line=dict(width=1, color='white')
                    ),
                    text=viagens_por_pais['País'],
                    textposition="top center",
                    hovertemplate='<b>%{text}</b><br>Viagens: %{x}<br>Duração Média: %{y:.1f} dias<extra></extra>'
                )
            ])
            
            fig_scatter.update_layout(
                title='Análise de Viagens vs Duração Média por País<br><sub>Tamanho da bolha = Servidores únicos</sub>',
                xaxis_title='Número de Viagens',
                yaxis_title='Duração Média (dias)',
                height=500,
                hovermode='closest',
                template='plotly_white'
            )
            
            st.plotly_chart(fig_scatter, use_container_width=True)
        except Exception:
            st.info("Gráfico de scatter indisponível")
        
        st.subheader("📋 Detalhes Completos por País")
        
        df_paises_display = viagens_por_pais.sort_values('Total_Viagens', ascending=False).copy()
        df_paises_display = df_paises_display.drop('ISO_Code', axis=1)
        df_paises_display.columns = ['País', 'Total de Viagens', 'Servidores Únicos', 'Duração Média (dias)']
        df_paises_display['Total de Viagens'] = df_paises_display['Total de Viagens'].astype(int)
        df_paises_display['Servidores Únicos'] = df_paises_display['Servidores Únicos'].astype(int)
        df_paises_display['Duração Média (dias)'] = df_paises_display['Duração Média (dias)'].round(1)
        
        st.dataframe(df_paises_display, use_container_width=True)
    
    # =============================================================================
    # ANÁLISE TEMPORAL
    # =============================================================================
    
    st.header("📈 Análise Temporal")
    
    if not viagens_por_mes.empty:
        fig_mes = px.bar(
            viagens_por_mes, 
            x='Mês_Início', 
            y='Viagens',
            title='Viagens por Mês (mês de início)',
            color='Viagens',
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_mes, use_container_width=True)
    else:
        st.info("Não há dados para o gráfico mensal")
    
    # =============================================================================
    # 🎯 ANÁLISE DE EQUIDADE E ASPECTOS NEGLIGENCIADOS
    # =============================================================================
    
    st.header("🎯 Análise de Equidade e Aspectos Negligenciados")
    
    # 1. DISTRIBUIÇÃO DE GÊNERO POR TIPO DE VIAGEM
    st.subheader("👥 Distribuição de Gênero por Tipo de Viagem")
    
    col1, col2 = st.columns(2)
    
    with col1:
        genero_tipo = df_filtrado.groupby(['Tipo de Viagem', 'Gênero']).size().reset_index(name='Viagens')
        
        fig_genero_tipo = px.bar(
            genero_tipo,
            x='Tipo de Viagem',
            y='Viagens',
            color='Gênero',
            barmode='group',
            title='Acesso por Gênero: Quem viaja para qual tipo de evento?',
            color_discrete_map={'Masculino': '#0066CC', 'Feminino': '#FF6B9D', 'Não Informado': '#CCCCCC'}
        )
        st.plotly_chart(fig_genero_tipo, use_container_width=True)
    
    with col2:
        genero_tipo_pct = df_filtrado.groupby('Tipo de Viagem')['Gênero'].value_counts(normalize=True).unstack(fill_value=0) * 100
        
        fig_genero_tipo_pct = px.bar(
            genero_tipo_pct.reset_index().melt(id_vars='Tipo de Viagem'),
            x='Tipo de Viagem',
            y='value',
            color='Gênero',
            barmode='stack',
            title='Composição de Gênero por Tipo de Viagem (%)',
            labels={'value': 'Percentual (%)'},
            color_discrete_map={'Masculino': '#0066CC', 'Feminino': '#FF6B9D', 'Não Informado': '#CCCCCC'}
        )
        st.plotly_chart(fig_genero_tipo_pct, use_container_width=True)
    
    # Insight
    pct_fem_total = (df_filtrado['Gênero'] == 'Feminino').sum() / len(df_filtrado) * 100 if len(df_filtrado) > 0 else 0
    st.markdown(f"""
        <div class="alert-box">
        <b>⚠️ Alerta de Equidade:</b> Mulheres representam apenas <b>{pct_fem_total:.1f}%</b> das viagens registradas.
        <br>📌 Recomendação: Analisar barreiras de acesso e oportunidades desiguais por gênero em cada tipo de viagem.
        </div>
    """, unsafe_allow_html=True)
    
    # =============================================================================
    # 2. PARIDADE DE CUSTO E OPORTUNIDADE POR GÊNERO
    # =============================================================================
    
    if 'Custo' in df_filtrado.columns:
        st.subheader("💰 Paridade de Investimento: Análise de Custo por Gênero")
        
        col1, col2 = st.columns(2)
        
        with col1:
            custo_genero = df_filtrado.groupby('Gênero').agg({
                'Custo': ['mean', 'median', 'count'],
                'Duração (dias)': 'mean'
            }).round(2)
            
            custo_genero_display = pd.DataFrame({
                'Gênero': custo_genero.index,
                'Custo Médio (R$)': custo_genero['Custo']['mean'].values,
                'Custo Mediano (R$)': custo_genero['Custo']['median'].values,
                'Duração Média': custo_genero['Duração (dias)']['mean'].values,
                'Total de Viagens': custo_genero['Custo']['count'].values.astype(int)
            })
            
            st.dataframe(custo_genero_display, use_container_width=True)
        
        with col2:
            custo_gen_detail = df_filtrado.groupby('Gênero').agg({
                'Custo': 'mean',
                'Duração (dias)': 'mean'
            }).reset_index()
            
            fig_custo_gen = px.bar(
                custo_gen_detail,
                x='Gênero',
                y=['Custo', 'Duração (dias)'],
                barmode='group',
                title='Custo Médio e Duração por Gênero',
                labels={'value': 'Valor'},
                color_discrete_map={'Custo': '#FF6B6B', 'Duração (dias)': '#4ECDC4'}
            )
            fig_custo_gen.update_layout(yaxis_title="Valor", hovermode='closest')
            st.plotly_chart(fig_custo_gen, use_container_width=True)
        
        # Insight
        custo_m = df_filtrado[df_filtrado['Gênero'] == 'Masculino']['Custo'].mean()
        custo_f = df_filtrado[df_filtrado['Gênero'] == 'Feminino']['Custo'].mean()
        diff_pct = ((custo_m - custo_f) / custo_f * 100) if custo_f > 0 else 0
        
        st.markdown(f"""
            <div class="alert-box">
            <b>🚨 Achado Crítico:</b> Mulheres recebem <b>{'MENOS' if diff_pct > 0 else 'MAIS'} {abs(diff_pct):.1f}%</b> em orçamento médio de viagem.
            <br>💡 Questão para investigação: É uma diferença de especialização ou de oportunidade desigual?
            </div>
        """, unsafe_allow_html=True)
    
    # =============================================================================
    # 3. REPRESENTATIVIDADE POR DIRETORIA E GÊNERO
    # =============================================================================
    
    st.subheader("🏢 Diversidade por Diretoria: Distribuição de Gênero")
    
    genero_diretoria = df_filtrado.groupby(['Diretoria', 'Gênero']).size().reset_index(name='Viagens')
    
    fig_diversity = px.bar(
        genero_diretoria,
        x='Diretoria',
        y='Viagens',
        color='Gênero',
        barmode='stack',
        title='Composição de Gênero por Diretoria',
        color_discrete_map={'Masculino': '#0066CC', 'Feminino': '#FF6B9D', 'Não Informado': '#CCCCCC'}
    )
    st.plotly_chart(fig_diversity, use_container_width=True)
    
    # =============================================================================
    # 📋 ANÁLISE DE PLANEJAMENTO (ANTECEDÊNCIA)
    # =============================================================================
    
    st.header("📋 Análise de Planejamento e Governança")
    
    st.subheader("📅 Qualidade do Planejamento: Categorização de Antecedência")
    
    col1, col2 = st.columns(2)
    
    with col1:
        dist_antec = df_filtrado['Categoria_Antecedencia'].value_counts().reset_index(name='Viagens')
        dist_antec.columns = ['Categoria', 'Viagens']
        
        # Ordenar corretamente
        ordem_antec = ['Urgência (0-15d)', 'Aviso Prévio (15-30d)', 'Bem Planejada (30+d)']
        dist_antec['Categoria'] = pd.Categorical(dist_antec['Categoria'], categories=ordem_antec, ordered=True)
        dist_antec = dist_antec.sort_values('Categoria')
        
        fig_antec_dist = px.bar(
            dist_antec,
            x='Categoria',
            y='Viagens',
            color='Categoria',
            color_discrete_map={
                'Urgência (0-15d)': '#FF6B6B',
                'Aviso Prévio (15-30d)': '#FFD93D',
                'Bem Planejada (30+d)': '#6BCB77'
            },
            title='Distribuição de Planejamento: Tempo de Antecedência',
            labels={'Viagens': 'Número de Viagens'},
            text_auto='value'
        )
        st.plotly_chart(fig_antec_dist, use_container_width=True)
    
    with col2:
        pct_urgencia = (df_filtrado['Categoria_Antecedencia'] == 'Urgência (0-15d)').sum() / len(df_filtrado) * 100 if len(df_filtrado) > 0 else 0
        pct_aviso = (df_filtrado['Categoria_Antecedencia'] == 'Aviso Prévio (15-30d)').sum() / len(df_filtrado) * 100 if len(df_filtrado) > 0 else 0
        pct_bem = (df_filtrado['Categoria_Antecedencia'] == 'Bem Planejada (30+d)').sum() / len(df_filtrado) * 100 if len(df_filtrado) > 0 else 0
        
        fig_antec_pie = px.pie(
            values=[pct_urgencia, pct_aviso, pct_bem],
            names=['Urgência (0-15d)', 'Aviso Prévio (15-30d)', 'Bem Planejada (30+d)'],
            title='% de Viagens por Categoria de Planejamento',
            color_discrete_map={
                'Urgência (0-15d)': '#FF6B6B',
                'Aviso Prévio (15-30d)': '#FFD93D',
                'Bem Planejada (30+d)': '#6BCB77'
            }
        )
        st.plotly_chart(fig_antec_pie, use_container_width=True)
    
    # Insight
    st.markdown(f"""
        <div class="alert-box">
        <b>🎯 Indicador de Governança:</b> 
        <br>• <b>{pct_urgencia:.1f}%</b> em URGÊNCIA (0-15 dias) - Risco de decisões apressadas
        <br>• <b>{pct_aviso:.1f}%</b> com aviso prévio (15-30 dias)
        <br>• <b>{pct_bem:.1f}%</b> bem planejadas (30+ dias) - Ideal para gestão eficiente
        <br>💡 Meta recomendada: Aumentar para 70-80% com planejamento antecipado
        </div>
    """, unsafe_allow_html=True)
    
    # =============================================================================
    # 🆕 GRÁFICO ROBUSTO: ANÁLISE POR TIPO DE VIAGEM (sem colunas inexistentes)
    # =============================================================================
    
    st.subheader("🎯 Prioridades por Tipo de Viagem e Diretoria")
    
    tipo_viagem_dir = df_filtrado.groupby(['Tipo de Viagem', 'Diretoria']).size().reset_index(name='Viagens')
    tipo_viagem_dir_top = tipo_viagem_dir[tipo_viagem_dir['Viagens'] >= 2].sort_values('Viagens', ascending=False).head(15)
    
    fig_tipo_dir = px.bar(
        tipo_viagem_dir_top,
        x='Viagens',
        y='Tipo de Viagem',
        color='Diretoria',
        orientation='h',
        title='Top 15 Combinações: Tipo de Viagem × Diretoria',
        labels={'Viagens': 'Número de Viagens'}
    )
    st.plotly_chart(fig_tipo_dir, use_container_width=True)
    
    # Insight
    top_combo = tipo_viagem_dir_top.iloc[0]
    st.markdown(f"""
        <div class="insight-box">
        <b>🎯 Foco Principal:</b> A combinação "<b>{top_combo['Tipo de Viagem']}</b>" da diretoria "<b>{top_combo['Diretoria']}</b>" representa <b>{top_combo['Viagens']}</b> viagens.
        <br>💡 Oportunidade: Otimizar processos e recursos para esta categoria de alta demanda.
        </div>
    """, unsafe_allow_html=True)
    
    # =============================================================================
    # 💰 MATRIZ DE CUSTOS (TIPO DE VIAGEM x DIRETORIA)
    # =============================================================================
    
    if 'Custo' in df_filtrado.columns:
        st.subheader("💰 Padrão de Custos: Tipo de Viagem × Diretoria")
        
        custo_tipo_dir = df_filtrado.groupby(['Tipo de Viagem', 'Diretoria']).agg({
            'Custo': ['mean', 'count']
        }).reset_index()
        custo_tipo_dir.columns = ['Tipo_Viagem', 'Diretoria', 'Custo_Medio', 'Viagens']
        custo_tipo_dir = custo_tipo_dir[custo_tipo_dir['Viagens'] >= 2]
        
        fig_custo_matriz = px.scatter(
            custo_tipo_dir,
            x='Tipo de Viagem',
            y='Diretoria',
            size='Viagens',
            color='Custo_Medio',
            color_continuous_scale='RdYlGn_r',
            title='Matriz de Custos: Tipo de Viagem × Diretoria<br><sub>Tamanho = quantidade de viagens | Cor = custo médio</sub>',
            hover_data={'Custo_Medio': ':.0f', 'Viagens': True},
            labels={'Custo_Medio': 'Custo Médio (R$)'}
        )
        fig_custo_matriz.update_layout(height=550)
        st.plotly_chart(fig_custo_matriz, use_container_width=True)
        
        # Insight
        combinacao_max = custo_tipo_dir.loc[custo_tipo_dir['Custo_Medio'].idxmax()]
        
        st.markdown(f"""
            <div class="insight-box">
            <b>💼 Combinação Mais Custosa:</b> Viagens do tipo "<b>{combinacao_max['Tipo_Viagem']}</b>" da diretoria "<b>{combinacao_max['Diretoria']}</b>" custam em média <b>R$ {combinacao_max['Custo_Medio']:,.0f}</b>.
            <br>💡 Recomendação: Investigar fatores que elevam o custo (destinos, duração, especialização).
            </div>
        """, unsafe_allow_html=True)
    
    # =============================================================================
    # ANÁLISE POR DIRETORIA
    # =============================================================================
    
    st.header("🏢 Análise de Recursos por Diretoria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        viagens_diretoria = df_filtrado['Diretoria'].value_counts().reset_index()
        viagens_diretoria.columns = ['Diretoria', 'Viagens']
        
        fig_diretoria = px.bar(
            viagens_diretoria,
            x='Diretoria',
            y='Viagens',
            title='Distribuição de Viagens por Diretoria',
            color='Viagens',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_diretoria, use_container_width=True)
    
    with col2:
        duracao_diretoria = df_filtrado.groupby('Diretoria')['Duração (dias)'].mean().sort_values(ascending=False).reset_index()
        duracao_diretoria.columns = ['Diretoria', 'Duração Média']
        
        fig_dur_dir = px.bar(
            duracao_diretoria,
            x='Diretoria',
            y='Duração Média',
            title='Duração Média de Afastamento por Diretoria',
            color='Duração Média',
            color_continuous_scale='Oranges'
        )
        st.plotly_chart(fig_dur_dir, use_container_width=True)
    
    # =============================================================================
    # ANÁLISE DE TIPOS DE VIAGEM
    # =============================================================================
    
    st.header("✈️ Análise de Tipos de Viagem")
    
    col1, col2 = st.columns(2)
    
    with col1:
        distrib_tipo = df_filtrado['Tipo de Viagem'].value_counts()
        if not distrib_tipo.empty:
            fig_tipo = px.pie(
                values=distrib_tipo.values, 
                names=distrib_tipo.index,
                title='Distribuição por Tipo de Viagem',
                color_discrete_sequence=CORES_IBAMA
            )
            fig_tipo.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_tipo, use_container_width=True)
    
    with col2:
        duracao_tipo = df_filtrado.groupby('Tipo de Viagem')['Duração (dias)'].agg(['mean', 'count']).reset_index()
        if not duracao_tipo.empty:
            fig_duracao_tipo_detail = px.bar(
                duracao_tipo,
                x='Tipo de Viagem',
                y='mean',
                title='Duração Média por Tipo de Viagem',
                color='mean',
                color_continuous_scale='Blues',
                labels={'mean': 'Duração Média (dias)'}
            )
            st.plotly_chart(fig_duracao_tipo_detail, use_container_width=True)
    
    # =============================================================================
    # DADOS DETALHADOS
    # =============================================================================
    
    st.header("📋 Dados Detalhados")
    
    with st.expander("Visualizar dados processados"):
        st.dataframe(df_filtrado)
        
        st.subheader("Estatísticas Descritivas")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Duração Média", f"{df_filtrado['Duração (dias)'].mean():.1f} dias")
            st.metric("Duração Mínima", f"{df_filtrado['Duração (dias)'].min():.0f} dias")
        
        with col2:
            st.metric("Duração Máxima", f"{df_filtrado['Duração (dias)'].max():.0f} dias")
            st.metric("Antecedência Média", f"{df_filtrado['Antecedência (dias)'].mean():.1f} dias")
        
        with col3:
            st.metric("Total de Países", f"{df_com_pais['País_Inglês'].nunique()}")
            st.metric("Total de Diretorias", f"{df_filtrado['Diretoria'].nunique()}")
        
        csv = df_filtrado.to_csv(index=False)
        st.download_button(
            label="📥 Download dos dados filtrados (CSV)",
            data=csv,
            file_name=f"afastamentos_ibama_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

except Exception as e:
    st.error(f"Erro ao processar os dados: {str(e)}")
    import traceback
    st.code(traceback.format_exc())
