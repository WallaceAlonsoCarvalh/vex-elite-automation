import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import time 

# --- IMPORTAÇÃO DE SEGURANÇA ---
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="VEX ELITE | PRO TERMINAL",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS (VISUAL INVESTING DARK) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
    }
    
    h1, h2, h3, p, div, span { font-family: 'Rajdhani', sans-serif !important; }
    
    /* MENU ESTILO INVESTING */
    .stSelectbox > div > div {
        background-color: #1e1e1e !important;
        color: #ffffff !important;
        border: 1px solid #444 !important;
    }
    div[data-baseweb="popover"] { background-color: #1e1e1e !important; }
    li[role="option"] { color: white !important; background-color: #1e1e1e !important; }
    li[role="option"]:hover { background-color: #2196F3 !important; color: white !important; }
    .stSelectbox svg { fill: white !important; }
    
    /* BOTÃO DE AÇÃO */
    .stButton > button {
        background: #2196F3 !important; /* Azul Investing */
        color: white !important;
        font-family: 'Roboto', sans-serif;
        font-weight: 700;
        border: none;
        padding: 15px;
        text-transform: uppercase;
        border-radius: 4px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        background: #1976D2 !important;
        box-shadow: 0 0 15px rgba(33, 150, 243, 0.4);
    }

    /* CARD DE RESULTADOS */
    .data-card {
        background: #1e1e1e;
        border-left: 4px solid #2196F3;
        padding: 20px;
        border-radius: 4px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    
    .big-score {
        font-family: 'Roboto';
        font-size: 4.5rem;
        font-weight: 900;
        line-height: 1;
    }
    
    /* Esconde elementos nativos */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. SESSÃO E LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

CREDENCIAIS = {
    "wallace": "admin123",
    "cliente01": "pro2026"
}

# --- 4. COLETOR DE DADOS REAIS (SEM SIMULAÇÃO) ---
# Cache de 30s para evitar que o gráfico mude a cada clique (Estabilidade)
@st.cache_data(ttl=30, show_spinner=False) 
def get_real_market_data(pair):
    """
    Busca dados EXCLUSIVAMENTE do Yahoo Finance (Base Global).
    Se falhar, retorna None (não gera gráfico falso).
    """
    if not YF_AVAILABLE:
        return None, "ERRO: BIBLIOTECA FALTANDO"

    # Mapeamento para Tickers Oficiais do Yahoo (Padrão Mundial)
    symbol_map = {
        "EUR/USD": "EURUSD=X", 
        "GBP/USD": "GBPUSD=X", 
        "USD/JPY": "JPY=X",
        "USD/CHF": "CHF=X", 
        "AUD/USD": "AUDUSD=X", 
        "USD/CAD": "CAD=X",
        "NZD/USD": "NZDUSD=X"
    }
    
    ticker = symbol_map.get(pair, "EURUSD=X")
    
    try:
        # Baixa dados reais de 1 minuto
        # 'period=1d' pega o dia de hoje
        # 'interval=1m' pega velas de 1 minuto
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        
        if df.empty:
            return None, "MERCADO FECHADO OU SEM DADOS"
            
        df = df.reset_index()
        
        # Padronização de Colunas (Yahoo as vezes muda maiuscula/minuscula)
        df.columns = df.columns.str.lower()
        if 'datetime' in df.columns: df = df.rename(columns={'datetime': 'timestamp'})
        if 'date' in df.columns: df = df.rename(columns={'date': 'timestamp'})
        
        # Validação extra
        if 'close' not in df.columns:
            return None, "ERRO NO FORMATO DE DADOS"

        # Pega as últimas 50 velas para o gráfico ficar limpo igual corretora
        return df.tail(50), "ONLINE • REAL DATA"
        
    except Exception as e:
        return None, "FALHA DE CONEXÃO COM SERVIDOR"

# --- 5. LÓGICA VEX DE FLUXO (PIPS) ---
def analyze_market_structure(df):
    if df is None or df.empty: return "NEUTRO", 0.0, "---"

    # Converte para numpy array para performance
    close = df['close'].values
    open_ = df['open'].values
    high = df['high'].values
    low = df['low'].values
    
    # Vela Atual (Última)
    c = close[-1]; o = open_[-1]; h = high[-1]; l = low[-1]
    
    # Cálculo de Corpo e Pavio
    body_size = abs(c - o)
    total_range = h - l
    if total_range == 0: total_range = 0.00001 # Evita divisão por zero
    
    upper_wick = h - max(c, o)
    lower_wick = min(c, o) - l
    
    # Indicadores Técnicos
    # Média Móvel Exponencial (EMA) de 9 períodos
    ema9 = pd.Series(close).ewm(span=9, adjust=False).mean().iloc[-1]
    
    # RSI (Índice de Força Relativa)
    delta = pd.Series(close).diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    if np.isnan(rsi): rsi = 50
    
    score = 50.0
    signal = "NEUTRO"
    motive = "AGUARDANDO DEFINIÇÃO"

    # --- LÓGICA DE DECISÃO (BASEADA EM FLUXO E FORÇA) ---
    
    # CENÁRIO DE COMPRA (BULLISH)
    # Preço acima da média + Vela Verde + RSI apontando pra cima (mas não saturado)
    if c > ema9 and c > o:
        # Se a vela tem corpo forte (mais que 50% do tamanho total)
        if body_size > (total_range * 0.5):
            if rsi > 50 and rsi < 85:
                score = 94.5
                signal = "COMPRA"
                motive = "FLUXO: VELA DE FORÇA COMPRADORA"
            elif rsi >= 85:
                # RSI muito alto pode ser exaustão, reduzimos a nota um pouco
                score = 88.0
                signal = "COMPRA"
                motive = "ALERTA: FORÇA COMPRADORA EXTREMA"
    
    # CENÁRIO DE VENDA (BEARISH)
    # Preço abaixo da média + Vela Vermelha
    elif c < ema9 and c < o:
        # Corpo forte
        if body_size > (total_range * 0.5):
            if rsi < 50 and rsi > 15:
                score = 94.5
                signal = "VENDA"
                motive = "FLUXO: VELA DE FORÇA VENDEDORA"
            elif rsi <= 15:
                score = 88.0
                signal = "VENDA"
                motive = "ALERTA: FORÇA VENDEDORA EXTREMA"

    return signal, score, motive

# --- 6. INTERFACE DE LOGIN ---
def tela_login():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("""
            <div style="text-align:center; padding: 40px; background: #1e1e1e; border-radius: 10px; border-top: 5px solid #2196F3;">
                <h1 style="color:white; margin:0;">VEX ELITE</h1>
                <p style="color:#aaa; font-size: 0.8rem; letter-spacing: 2px;">FOREX INTELLIGENCE v13.0</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        user = st.text_input("ID DE ACESSO", label_visibility="collapsed", placeholder="Usuário")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        pwd = st.text_input("SENHA", type="password", label_visibility="collapsed", placeholder="Senha")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("CONECTAR AO SERVIDOR"):
            if user in CREDENCIAIS and pwd == CREDENCIAIS[user]:
                st.session_state['logado'] = True
                st.rerun()
            else:
                st.error("Credenciais não reconhecidas.")

# --- 7. DASHBOARD PRINCIPAL ---
def tela_dashboard():
    # Barra Superior
    st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #333; padding-bottom:15px; margin-bottom:20px;">
            <div>
                <span style="font-size:1.8rem; font-weight:900; color:white;">VEX</span>
                <span style="font-size:1.8rem; font-weight:400; color:#2196F3;">FOREX</span>
            </div>
            <div style="display:flex; gap:10px; align-items:center;">
                <span style="font-size:0.8rem; color:#aaa;">DATA FEED:</span>
                <span style="background:#2196F3; color:white; padding:4px 8px; border-radius:4px; font-weight:bold; font-size:0.8rem;">YAHOO FINANCE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Painel de Controle
    c1, c2 = st.columns([3, 1])
    with c1:
        ativo = st.selectbox("SELECIONE O PAR DE MOEDAS", 
                             ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD", "NZD/USD"])
    with c2:
        st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True) # Espaçador
        analisar = st.button("GERAR ANÁLISE")

    # Área de Resultados
    if analisar:
        with st.spinner("SINCRONIZANDO DADOS REAIS..."):
            # 1. Pega dados (Cacheado por 30s)
            df, status = get_real_market_data(ativo)
            
            if df is not None:
                # 2. Analisa
                sig, score, motive = analyze_market_structure(df)
                
                # Layout Colunas
                g_col, i_col = st.columns([2, 1.2])
                
                # --- COLUNA DO GRÁFICO ---
                with g_col:
                    st.markdown(f"""
                        <div class="data-card">
                            <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                                <span style="font-weight:bold; font-size:1.2rem;">{ativo}</span>
                                <span style="color:#2196F3; font-weight:bold;">{status}</span>
                            </div>
                    """, unsafe_allow_html=True)
                    
                    # Gráfico Profissional (Estilo Investing)
                    fig = go.Figure(data=[go.Candlestick(
                        x=df['timestamp'],
                        open=df['open'], high=df['high'],
                        low=df['low'], close=df['close'],
                        increasing_line_color='#26a69a', # Verde Investing
                        decreasing_line_color='#ef5350'  # Vermelho Investing
                    )])
                    
                    fig.update_layout(
                        template="plotly_dark",
                        height=400,
                        xaxis_rangeslider_visible=False,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=10, r=10, t=10, b=10),
                        xaxis=dict(showgrid=False),
                        yaxis=dict(showgrid=True, gridcolor='#333')
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # --- COLUNA DA INTELIGÊNCIA ---
                with i_col:
                    st.markdown('<div class="data-card" style="height: 100%; text-align: center;">', unsafe_allow_html=True)
                    st.markdown('<p style="color:#aaa; font-weight:bold;">PROBABILIDADE</p>', unsafe_allow_html=True)
                    
                    # Definição de Cores do Score
                    cor_score = "#26a69a" if score >= 90 else "#ffcc00"
                    if score < 60: cor_score = "#ef5350"
                    
                    st.markdown(f'<div class="big-score" style="color:{cor_score}">{score:.1f}%</div>', unsafe_allow_html=True)
                    
                    st.markdown("---")
                    
                    if score >= 90:
                        sinal_texto = "COMPRA" if sig == "COMPRA" else "VENDA"
                        bg_sinal = "#26a69a" if sig == "COMPRA" else "#ef5350"
                        
                        st.markdown(f"""
                            <div style="background: {bg_sinal}; padding: 15px; border-radius: 5px; color: white;">
                                <h2 style="margin:0; font-weight:900;">{sinal_texto}</h2>
                            </div>
                            <p style="margin-top:15px; color: white;"><b>MOTIVO:</b> {motive}</p>
                            <p style="color: #aaa; font-size: 0.8rem;">Entrada imediata (M1)</p>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown("""
                            <div style="border: 2px solid #ffcc00; padding: 15px; border-radius: 5px; color: #ffcc00;">
                                <h3 style="margin:0;">AGUARDE</h3>
                            </div>
                            <p style="margin-top:15px; color: #aaa;">Mercado sem direção clara.</p>
                        """, unsafe_allow_html=True)
                        
                    st.markdown(f"<p style='margin-top:20px; font-size:1.5rem; font-weight:bold;'>${df['close'].iloc[-1]:.5f}</p>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            else:
                st.error("⚠️ NÃO FOI POSSÍVEL CARREGAR DADOS REAIS.")
                st.info("Verifique se a biblioteca 'yfinance' está instalada no servidor ou tente outro par.")

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("DESCONECTAR"):
        st.session_state['logado'] = False
        st.rerun()

# --- 8. EXECUÇÃO ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
