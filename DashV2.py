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
    </style>
    <h1 class="main-header">🌍 Dashboard de Afastamentos 2025 - IBAMA</h1>
""", unsafe_allow_html=True)

# Carregar os dados
@st.cache_data
def load_data():
    file_path = r"C:\Users\49821553800\Desktop\Dash\Planilha\DATA Afastamentos 2025.xlsx"
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
    
    # =============================================================================
    # PROCESSAMENTO DE PAÍSES - VERSÃO NOVA E ROBUSTA
    # =============================================================================
    
    # Limpeza inicial de países
    df['País'] = df['País'].astype(str).str.strip()
    
    # Mapeamento direto - aplicar com case-insensitive
    def mapear_pais(pais_input):
        if pd.isna(pais_input) or str(pais_input).lower() in ['nan', 'none', 'null', '']:
            return None
        
        pais_input_str = str(pais_input).strip()
        
        # Busca exata primeiro
        if pais_input_str in COUNTRY_MAPPING:
            return COUNTRY_MAPPING[pais_input_str]
        
        # Busca case-insensitive
        for pais_pt, pais_en in COUNTRY_MAPPING.items():
            if pais_pt.lower() == pais_input_str.lower():
                return pais_en
        
        return None
    
    df['País_Inglês'] = df['País'].apply(mapear_pais)
    
    # Guardar país original em português para referência
    df['País_PT'] = df['País'].apply(
        lambda x: next((k for k, v in COUNTRY_MAPPING.items() if v == df[df['País'] == x]['País_Inglês'].iloc[0] if pd.notna(df[df['País'] == x]['País_Inglês'].iloc[0])), None) 
        if pd.notna(x) else None
    )
    
    # Preenchimento alternativo
    for idx, row in df.iterrows():
        if pd.isna(df.loc[idx, 'País_PT']) and pd.notna(df.loc[idx, 'País_Inglês']):
            for k, v in COUNTRY_MAPPING.items():
                if v == df.loc[idx, 'País_Inglês']:
                    df.loc[idx, 'País_PT'] = k
                    break
    
    if debug_mode:
        st.sidebar.write("🔍 Debug - Países em inglês únicos:", sorted(df['País_Inglês'].dropna().unique()))
        st.sidebar.write("📊 Contagem:", df['País_Inglês'].value_counts())
    
    # =============================================================================
    # TRATAMENTO DE OUTROS CAMPOS
    # =============================================================================
    
    df['Diretoria'] = df['Diretoria'].fillna('Não Informado')
    df['Tipo de Viagem'] = df['Tipo de Viagem'].fillna('Não Informado')
    df['Gênero'] = df['Gênero'].fillna('Não Informado')
    df['Mês_Início'] = df['Início do Afastamento'].dt.month_name()
    df['Trimestre'] = 'T' + df['Início do Afastamento'].dt.quarter.astype(str)
    
    # Ordem dos meses
    meses_ordem = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    
    # =============================================================================
    # SIDEBAR COM FILTROS
    # =============================================================================
    
    st.sidebar.header("🔧 Filtros")
    
    # Preparar opções para filtros
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
    
    # Aplicar filtros
    df_filtrado = df.copy()
    
    if tipo_selecionado != 'Todos':
        df_filtrado = df_filtrado[df_filtrado['Tipo de Viagem'] == tipo_selecionado]
    
    if diretoria_selecionada != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['Diretoria'] == diretoria_selecionada]
    
    # =============================================================================
    # AGREGAÇÕES PARA OS MAPAS - NOVA ABORDAGEM
    # =============================================================================
    
    # Filtrar apenas linhas com país válido (mapeado com sucesso)
    df_com_pais = df_filtrado[df_filtrado['País_Inglês'].notna()].copy()
    
    # Aggregação por país em inglês
    viagens_por_pais = df_com_pais.groupby('País_Inglês').agg({
        'País': 'count',
        'Servidor': 'nunique',
        'Duração (dias)': 'mean'
    }).reset_index()
    viagens_por_pais.columns = ['País', 'Total_Viagens', 'Servidores_Unicos', 'Duração_Media']
    
    # Adicionar código ISO para o choropleth
    viagens_por_pais['ISO_Code'] = viagens_por_pais['País'].map(ISO_MAPPING)
    
    # Contagem de viagens por mês
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
    
    # Calcular métricas
    total_viagens = df_filtrado.shape[0]
    total_servidores = df_filtrado['Servidor'].nunique()
    duracao_media = df_filtrado['Duração (dias)'].mean()
    antecedencia_media = df_filtrado['Antecedência (dias)'].mean()
    total_paises = df_com_pais['País_Inglês'].nunique()
    
    # ✅ CONVERSÃO SEGURA DE CUSTO
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
    
    # Métricas adicionais interessantes
    st.header("📈 Métricas Adicionais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #FF6B6B, #C92A2A);">
                <h3>{antecedencia_media:.0f}</h3>
                <p>Antecedência Média (dias)</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        viagens_por_servidor = total_viagens / total_servidores if total_servidores > 0 else 0
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #4ECDC4, #1FA39C);">
                <h3>{viagens_por_servidor:.1f}</h3>
                <p>Viagens por Servidor</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        max_viagens_mes = viagens_por_mes['Viagens'].max() if not viagens_por_mes.empty else 0
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #FFD93D, #FF9F43);">
                <h3>{max_viagens_mes:.0f}</h3>
                <p>Pico de Viagens (1 mês)</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        duracao_total = df_filtrado['Duração (dias)'].sum()
        st.markdown(f"""
            <div class="metric-card" style="background: linear-gradient(135deg, #A8E6CF, #56CCF2);">
                <h3>{duracao_total:.0f}</h3>
                <p>Total de Dias de Afastamento</p>
            </div>
        """, unsafe_allow_html=True)
    
    # =============================================================================
    # MAPA MUNDI COM CHOROPLETH
    # =============================================================================
    
    st.header("🗺️ Mapa Mundi - Países Visitados")
    
    if not viagens_por_pais.empty and not viagens_por_pais['ISO_Code'].isna().all():
        try:
            # Criar mapa coroplético
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
                    bgcolor='rgba(200, 220, 240, 0.3)'
                ),
                height=600,
                hovermode='closest',
                coloraxis_colorbar=dict(
                    title="Número de<br>Viagens",
                    titleside="right",
                    tickmode="linear",
                    tick0=0
                )
            )
            
            st.plotly_chart(fig_mapa_mundi, use_container_width=True)
            
            st.info("💡 Dica: Passe o mouse sobre os países para ver detalhes das viagens, clique e arraste para rotacionar o mapa!")
            
        except Exception as e:
            st.warning(f"⚠️ Erro ao gerar mapa mundi: {str(e)}")
    else:
        st.warning("⚠️ Não foi possível gerar o mapa mundi. Verifique os dados de países.")
    
    # =============================================================================
    # MAPAS INTERATIVOS - ANÁLISE DETALHADA
    # =============================================================================
    
    st.header("🌍 Análise Detalhada por País")
    
    if not viagens_por_pais.empty:
        # Criar mapa com barras horizontais
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
        
        # Mapa de scatter com coordenadas (alternativa visual)
        st.subheader("📍 Análise de Viagens vs Duração Média")
        
        try:
            # Criar visualização alternativa com todos os países
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
        except:
            st.info("Gráfico de scatter indisponível")
        
        # Tabela de países
        st.subheader("📋 Detalhes Completos por País")
        
        df_paises_display = viagens_por_pais.sort_values('Total_Viagens', ascending=False).copy()
        df_paises_display = df_paises_display.drop('ISO_Code', axis=1)
        df_paises_display.columns = ['País', 'Total de Viagens', 'Servidores Únicos', 'Duração Média (dias)']
        df_paises_display['Total de Viagens'] = df_paises_display['Total de Viagens'].astype(int)
        df_paises_display['Servidores Únicos'] = df_paises_display['Servidores Únicos'].astype(int)
        df_paises_display['Duração Média (dias)'] = df_paises_display['Duração Média (dias)'].round(1)
        
        st.dataframe(df_paises_display, use_container_width=True)
    else:
        st.warning("⚠️ Nenhum país identificado nos dados filtrados. Verifique os dados de origem.")
    
    # =============================================================================
    # ANÁLISE TEMPORAL
    # =============================================================================
    
    st.header("📈 Análise Temporal")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Gráfico de viagens por mês
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
    
    with col2:
        # Viagens por trimestre
        viagens_trimestre = df_filtrado.groupby('Trimestre').size().reset_index(name='Viagens')
        if not viagens_trimestre.empty:
            fig_trimestre = px.line(
                viagens_trimestre,
                x='Trimestre',
                y='Viagens',
                title='Viagens por Trimestre',
                markers=True,
                line_shape='spline'
            )
            fig_trimestre.update_traces(line=dict(color=CORES_IBAMA[0], width=3))
            st.plotly_chart(fig_trimestre, use_container_width=True)
        else:
            st.info("Não há dados por trimestre")
    
    # =============================================================================
    # ANÁLISE DE GÊNERO E RANKINGS
    # =============================================================================
    
    st.header("👥 Análise de Gênero e Rankings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por gênero
        distrib_genero = df_filtrado['Gênero'].value_counts()
        if not distrib_genero.empty:
            fig_genero = px.pie(
                values=distrib_genero.values, 
                names=distrib_genero.index,
                title='Distribuição por Gênero',
                color_discrete_sequence=CORES_IBAMA
            )
            fig_genero.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_genero, use_container_width=True)
        else:
            st.info("Não há dados de gênero para exibir")
    
    with col2:
        # Ranking de servidores
        servidores_count = df_filtrado['Servidor'].value_counts().head(10).reset_index()
        servidores_count.columns = ['Servidor', 'Viagens']
        
        if not servidores_count.empty:
            fig_servidores = px.bar(
                servidores_count,
                x='Viagens',
                y='Servidor',
                orientation='h',
                title='Top 10 Servidores (por número de viagens)',
                color='Viagens',
                color_continuous_scale='Plasma'
            )
            st.plotly_chart(fig_servidores, use_container_width=True)
        else:
            st.info("Não há dados para o ranking de servidores")
    
    # =============================================================================
    # ANÁLISE DE TIPOS DE VIAGEM
    # =============================================================================
    
    st.header("✈️ Análise de Tipos de Viagem")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição por tipo de viagem
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
        else:
            st.info("Não há dados de tipo de viagem")
    
    with col2:
        # Duração média por tipo de viagem
        duracao_tipo = df_filtrado.groupby('Tipo de Viagem')['Duração (dias)'].agg(['mean', 'count']).reset_index()
        if not duracao_tipo.empty:
            fig_duracao_tipo = px.bar(
                duracao_tipo,
                x='Tipo de Viagem',
                y='mean',
                title='Duração Média por Tipo de Viagem',
                color='mean',
                color_continuous_scale='Blues',
                labels={'mean': 'Duração Média (dias)'}
            )
            st.plotly_chart(fig_duracao_tipo, use_container_width=True)
        else:
            st.info("Não há dados de duração por tipo")
    
    # =============================================================================
    # DADOS DETALHADOS
    # =============================================================================
    
    st.header("📋 Dados Detalhados")
    
    with st.expander("Visualizar dados processados"):
        st.dataframe(df_filtrado)
        
        # Estatísticas descritivas
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
        
        # Opção de download
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
