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
    # TRATAMENTO DE OUTROS CAMPOS
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
    # MÉTRICAS AVANÇADAS - REDUZIDAS
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
        except:
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
    # 🎯 NOVOS GRÁFICOS DE GOVERNANÇA E INSIGHTS ESTRATÉGICOS
    # =============================================================================
    
    st.header("🎯 Análise de Governança e Eficiência")
    
    # 1. ÍNDICE DE CONCENTRAÇÃO (Pareto 80/20)
    st.subheader("📊 Índice de Concentração de Viagens (Análise de Pareto)")
    
    viagens_servidor = df_filtrado['Servidor'].value_counts().reset_index()
    viagens_servidor.columns = ['Servidor', 'Viagens']
    viagens_servidor['Viagens_Acumulada'] = viagens_servidor['Viagens'].cumsum()
    viagens_servidor['Percentual_Acumulado'] = (viagens_servidor['Viagens_Acumulada'] / viagens_servidor['Viagens'].sum() * 100)
    
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=list(range(1, len(viagens_servidor.head(20))+1)),
        y=viagens_servidor.head(20)['Viagens'],
        name='Viagens por Servidor',
        marker_color='#0066CC'
    ))
    fig_pareto.add_trace(go.Scatter(
        x=list(range(1, len(viagens_servidor.head(20))+1)),
        y=viagens_servidor.head(20)['Percentual_Acumulado'],
        name='% Acumulado',
        yaxis='y2',
        line=dict(color='#FF6B6B', width=3),
        mode='lines+markers'
    ))
    fig_pareto.update_layout(
        title='Análise de Pareto: Concentração de Viagens por Servidor (Top 20)<br><sub>Identifica 20% dos servidores responsáveis por ~80% das viagens</sub>',
        xaxis_title='Ranking de Servidores',
        yaxis_title='Número de Viagens',
        yaxis2=dict(title='% Acumulado', overlaying='y', side='right'),
        height=500,
        hovermode='closest'
    )
    st.plotly_chart(fig_pareto, use_container_width=True)
    
    # Insight Pareto
    pct_80 = viagens_servidor[viagens_servidor['Percentual_Acumulado'] <= 80].shape[0]
    pct_20 = len(viagens_servidor)
    st.markdown(f"""
        <div class="insight-box">
        <b>💡 Insight de Governança:</b> Aproximadamente <b>{pct_80} servidores ({pct_80/pct_20*100:.1f}%)</b> são responsáveis por <b>~80% das viagens</b>. 
        Isso sugere oportunidades de:
        <br>✓ Centralizar expertise em gestão de viagens
        <br>✓ Otimizar processos para estes servidores chave
        <br>✓ Analisar motivos de concentração (especialização vs falta de distribuição)
        </div>
    """, unsafe_allow_html=True)
    
    # =============================================================================
    # 2. PLANEJAMENTO POR DIRETORIA (Antecedência Média)
    # =============================================================================
    
    st.subheader("📅 Taxa de Planejamento por Diretoria")
    
    col1, col2 = st.columns(2)
    
    with col1:
        planejamento_diretoria = df_filtrado.groupby('Diretoria').agg({
            'Antecedência (dias)': 'mean',
            'Servidor': 'count'
        }).reset_index()
        planejamento_diretoria.columns = ['Diretoria', 'Antecedência_Media', 'Total_Viagens']
        planejamento_diretoria = planejamento_diretoria.sort_values('Antecedência_Media', ascending=False)
        
        fig_antec = px.bar(
            planejamento_diretoria,
            x='Diretoria',
            y='Antecedência_Media',
            color='Antecedência_Media',
            color_continuous_scale='RdYlGn',
            title='Antecedência Média de Planejamento por Diretoria',
            labels={'Antecedência_Media': 'Dias de Antecedência'}
        )
        fig_antec.add_hline(y=30, line_dash="dash", line_color="red", 
                           annotation_text="Meta: 30 dias", annotation_position="right")
        st.plotly_chart(fig_antec, use_container_width=True)
    
    with col2:
        pct_bem_planejado_dir = df_filtrado.groupby('Diretoria')['Bem_Planejado'].apply(
            lambda x: (x.sum() / len(x) * 100) if len(x) > 0 else 0
        ).reset_index()
        pct_bem_planejado_dir.columns = ['Diretoria', 'Percentual_Bem_Planejado']
        pct_bem_planejado_dir = pct_bem_planejado_dir.sort_values('Percentual_Bem_Planejado', ascending=False)
        
        fig_pct = px.bar(
            pct_bem_planejado_dir,
            x='Diretoria',
            y='Percentual_Bem_Planejado',
            color='Percentual_Bem_Planejado',
            color_continuous_scale='Greens',
            title='% de Viagens Bem Planejadas (Antecedência ≥ 30 dias)',
            labels={'Percentual_Bem_Planejado': '% Bem Planejado'}
        )
        fig_pct.add_hline(y=80, line_dash="dash", line_color="blue", 
                         annotation_text="Meta: 80%", annotation_position="right")
        st.plotly_chart(fig_pct, use_container_width=True)
    
    # =============================================================================
    # 3. CORRELAÇÃO: ANTECEDÊNCIA vs DURAÇÃO
    # =============================================================================
    
    st.subheader("🔗 Correlação: Antecedência de Planejamento vs Duração da Viagem")
    
    fig_corr = px.scatter(
        df_filtrado,
        x='Antecedência (dias)',
        y='Duração (dias)',
        size='Custo' if 'Custo' in df_filtrado.columns else None,
        color='Bem_Planejado',
        hover_data=['Servidor', 'Diretoria'],
        title='Análise: Viagens Bem Planejadas tendem a ser mais longas ou curtas?',
        labels={'Bem_Planejado': 'Bem Planejado (30+ dias)'}
    )
    fig_corr.update_layout(height=500)
    st.plotly_chart(fig_corr, use_container_width=True)
    
    corr_antec_duracao = df_filtrado[['Antecedência (dias)', 'Duração (dias)']].corr().iloc[0, 1]
    st.markdown(f"""
        <div class="insight-box">
        <b>💡 Correlação Identificada:</b> Coeficiente de correlação: <b>{corr_antec_duracao:.2f}</b>
        <br>{'✓ Viagens bem planejadas tendem a ser mais longas/curtas' if abs(corr_antec_duracao) > 0.3 else '✓ Sem correlação significativa encontrada'}
        </div>
    """, unsafe_allow_html=True)
    
    # =============================================================================
    # 4. EFICIÊNCIA: CUSTO POR TIPO DE VIAGEM
    # =============================================================================
    
    if 'Custo' in df_filtrado.columns:
        st.subheader("💰 Eficiência de Custo por Tipo de Viagem")
        
        col1, col2 = st.columns(2)
        
        with col1:
            custo_tipo = df_filtrado.groupby('Tipo de Viagem').agg({
                'Custo': ['mean', 'sum', 'count']
            }).reset_index()
            custo_tipo.columns = ['Tipo_Viagem', 'Custo_Medio', 'Custo_Total', 'Qtd']
            
            fig_custo_tipo = px.bar(
                custo_tipo.sort_values('Custo_Medio', ascending=False),
                x='Tipo_Viagem',
                y='Custo_Medio',
                color='Custo_Medio',
                color_continuous_scale='Reds',
                title='Custo Médio por Tipo de Viagem',
                labels={'Custo_Medio': 'Custo Médio (R$)'}
            )
            st.plotly_chart(fig_custo_tipo, use_container_width=True)
        
        with col2:
            duracao_custo_tipo = df_filtrado.groupby('Tipo de Viagem').agg({
                'Duração (dias)': 'mean',
                'Custo': 'mean'
            }).reset_index()
            duracao_custo_tipo['Custo_Por_Dia'] = duracao_custo_tipo['Custo'] / duracao_custo_tipo['Duração (dias)']
            
            fig_roi = px.bar(
                duracao_custo_tipo.sort_values('Custo_Por_Dia', ascending=False),
                x='Tipo de Viagem',
                y='Custo_Por_Dia',
                color='Custo_Por_Dia',
                color_continuous_scale='Oranges',
                title='Custo por Dia de Duração (Eficiência)',
                labels={'Custo_Por_Dia': 'R$ por Dia'}
            )
            st.plotly_chart(fig_roi, use_container_width=True)
    
    # =============================================================================
    # 5. MATRIZ DIRETORIA x PAÍS (Análise de Focos Estratégicos)
    # =============================================================================
    
    st.subheader("🎯 Matriz Estratégica: Diretorias vs Países")
    
    matriz_dir_pais = df_com_pais.groupby(['Diretoria', 'País_Inglês']).size().reset_index(name='Viagens')
    matriz_pivot = matriz_dir_pais.pivot(index='Diretoria', columns='País_Inglês', values='Viagens').fillna(0)
    
    # Mostrar apenas top 15 países
    top_paises = df_com_pais['País_Inglês'].value_counts().head(15).index
    matriz_pivot_top = matriz_pivot[top_paises]
    
    fig_heatmap = px.imshow(
        matriz_pivot_top,
        labels=dict(x="País", y="Diretoria", color="Viagens"),
        title='Mapa de Calor: Distribuição de Viagens (Diretoria x País Top 15)',
        color_continuous_scale='YlOrRd',
        height=500
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)
    
    # =============================================================================
    # 6. DISTRIBUIÇÃO POR GÊNERO (Equity Analysis)
    # =============================================================================
    
    st.subheader("👥 Análise de Equidade: Distribuição de Viagens por Gênero")
    
    col1, col2 = st.columns(2)
    
    with col1:
        genero_viagens = df_filtrado['Gênero'].value_counts().reset_index()
        genero_viagens.columns = ['Gênero', 'Viagens']
        
        fig_genero = px.pie(
            genero_viagens,
            values='Viagens',
            names='Gênero',
            title='Distribuição de Viagens por Gênero',
            color_discrete_sequence=CORES_IBAMA
        )
        fig_genero.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_genero, use_container_width=True)
    
    with col2:
        custo_genero = df_filtrado.groupby('Gênero').agg({
            'Custo': 'mean',
            'Duração (dias)': 'mean',
            'Servidor': 'count'
        }).reset_index()
        custo_genero.columns = ['Gênero', 'Custo_Medio', 'Duracao_Media', 'Viagens']
        
        fig_custo_gen = px.bar(
            custo_genero,
            x='Gênero',
            y=['Custo_Medio', 'Duracao_Media'],
            title='Custo Médio e Duração por Gênero',
            barmode='group',
            labels={'value': 'Valor', 'variable': 'Métrica'}
        )
        st.plotly_chart(fig_custo_gen, use_container_width=True)
    
    # =============================================================================
    # 7. ANÁLISE POR DIRETORIA (Recursos e Alocação)
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
    # 8. TENDÊNCIA TEMPORAL DE CUSTO ACUMULADO
    # =============================================================================
    
    if 'Custo' in df_filtrado.columns:
        st.subheader("📈 Tendência Temporal: Custo Acumulado ao Longo do Período")
        
        df_temporal = df_filtrado.copy()
        df_temporal = df_temporal.sort_values('Data entrada na DAI')
        df_temporal['Custo_Acumulado'] = df_temporal['Custo'].cumsum()
        df_temporal['Data'] = df_temporal['Data entrada na DAI'].dt.date
        
        fig_tendencia = px.line(
            df_temporal.drop_duplicates(subset=['Data entrada na DAI']).sort_values('Data entrada na DAI'),
            x='Data entrada na DAI',
            y='Custo_Acumulado',
            title='Evolução do Custo Acumulado ao Longo do Período',
            markers=True,
            line_shape='spline'
        )
        fig_tendencia.update_layout(height=450, hovermode='x unified')
        st.plotly_chart(fig_tendencia, use_container_width=True)
    
    # =============================================================================
    # 9. DISTRIBUIÇÃO DE CUSTOS POR SERVIDOR (TOP 15)
    # =============================================================================
    
    if 'Custo' in df_filtrado.columns:
        st.subheader("👤 Análise de Custos: Top 15 Servidores com Maior Alocação")
        
        custo_servidor = df_filtrado.groupby('Servidor').agg({
            'Custo': ['sum', 'mean', 'count']
        }).reset_index()
        custo_servidor.columns = ['Servidor', 'Custo_Total', 'Custo_Medio', 'Viagens']
        custo_servidor = custo_servidor.sort_values('Custo_Total', ascending=False).head(15)
        
        fig_custo_serv = px.bar(
            custo_servidor,
            x='Custo_Total',
            y='Servidor',
            orientation='h',
            color='Custo_Medio',
            color_continuous_scale='Reds',
            title='Top 15 Servidores por Custo Total',
            hover_data={'Viagens': True}
        )
        st.plotly_chart(fig_custo_serv, use_container_width=True)
    
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
