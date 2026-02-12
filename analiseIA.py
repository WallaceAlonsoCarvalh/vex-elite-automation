import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import requests
import datetime
import time

# --- 1. CONFIGURAÇÃO E CREDENCIAIS (TOPO ABSOLUTO) ---
# Isso resolve o erro "NameError" do login
st.set_page_config(
    page_title="VEX ELITE | FLOW TERMINAL",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Definição de usuários (Global)
USER_CREDENTIALS = {
    "wallace": "admin123",  
    "cliente01": "pro2026", 
}

# --- 2. CSS CORRIGIDO (MENU VISÍVEL + DESIGN CYBER) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    
    /* Fundo Geral */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        color: #ffffff;
    }
    
    /* Textos Gerais */
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    /* --- CORREÇÃO DO MENU DROPDOWN (V9.0) --- */
    /* Caixa de seleção fechada */
    .stSelectbox > div > div {
        background-color: #000000 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
    }
    
    /* Texto dentro da caixa */
    .stSelectbox div[data-testid="stMarkdownContainer"] p {
        color: #00ff88 !important;
        font-weight: bold;
    }

    /* Lista suspensa (Onde estava branco) */
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #000000 !important;
        border: 1px solid #00ff88 !important;
    }
    
    /* Itens da lista */
    li[role="option"] {
        background-color: #000000 !important;
        color: #ffffff !important; /* Texto Branco */
    }
    
    /* Mouse passando por cima */
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #00ff88 !important;
        color: #000000 !important; /* Texto Preto no fundo Verde */
    }
    
    /* Seta do menu */
    .stSelectbox svg { fill: #00ff88 !important; }
    
    /* --- INPUTS --- */
    .stTextInput > div > div > input {
        background-color: #111 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
        border-radius: 8px;
        text-align: center;
    }
    
    /* --- BOTÕES --- */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #00ff88 !important;
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        font-weight: 900;
        padding: 20px;
        border-radius: 0px;
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.1);
        width: 100%;
    }
    .stButton > button:hover {
        background: #00ff88 !important;
        color: #000 !important;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.6);
        transform: scale(1.02);
    }
    
    /* CARDS */
    .neon-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 10px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }
    
    .score-glow {
        font-size: 6rem;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        text-shadow: 0 0 40px currentColor;
        line-height: 1;
        margin: 20px 0;
    }
    
    /* Esconder elementos padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. GERENCIAMENTO DE ESTADO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'analise_ativa' not in st.session_state:
    st.session_state['analise_ativa'] = None

# --- 4. COLETOR DE DADOS (PRIORIDADE BYBIT -> BINANCE -> COINGECKO) ---
def get_universal_data(symbol):
    clean_symbol = symbol.replace("/", "").upper()
    
    # 1. BYBIT (Mais estável para robôs)
    try:
        url = f"https://api.bybit.com/v5/market/kline?category=spot&symbol={clean_symbol}&interval=1&limit=60"
        response = requests.get(url, timeout=3)
        data = response.json()
        if 'result' in data and 'list' in data['result']:
            # Bybit retorna invertido (mais recente primeiro)
            df = pd.DataFrame(data['result']['list'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'turnover'])
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype(float)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df = df.sort_values('timestamp') # Ordenar corretamente
            return df
    except: pass

    # 2. BINANCE (Backup)
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={clean_symbol}&interval=1m&limit=60"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'x', 'x', 'x', 'x', 'x', 'x'])
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype(float)
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
    except: pass

    # 3. COINGECKO (Último recurso - lento mas funciona)
    try:
        cg_id = "bitcoin" if "BTC" in symbol else "ethereum" if "ETH" in symbol else "solana" if "SOL" in symbol else "binancecoin" if "BNB" in symbol else "ripple"
        url = f"https://api.coingecko.com/api/v3/coins/{cg_id}/ohlc?vs_currency=usd&days=1"
        response = requests.get(url, timeout=4)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
            df['volume'] = 1000 # Fake volume pois a API free não dá volume as vezes
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df.tail(60)
    except: pass

    return None

# --- 5. LÓGICA DE FLUXO (TREND FOLLOWER - 82%+) ---
def analyze_trend_flow(df):
    if df is None or df.empty:
        return "NEUTRO", 0.0, "ERRO: SEM DADOS"

    close = df['close'].values
    open_ = df['open'].values
    high = df['high'].values
    low = df['low'].values
    
    # Vela Atual
    c_now = close[-1]
    o_now = open_[-1]
    
    # Dimensões
    body_size = abs(c_now - o_now)
    total_size = high[-1] - low[-1]
    upper_wick = high[-1] - max(c_now, o_now)
    lower_wick = min(c_now, o_now) - low[-1]
    
    # Indicadores
    ema9 = pd.Series(close).ewm(span=9).mean().iloc[-1]
    
    # RSI
    rsi_period = 14
    delta = pd.Series(close).diff()
    gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    rsi = 50 if np.isnan(rsi) else rsi
    
    score = 0.0
    signal = "NEUTRO"
    motive = "ANALISANDO FLUXO..."

    # LÓGICA DE FLUXO (V7.0 MANTIDA)
    # Compra
    if c_now > ema9 and c_now > o_now:
        if body_size > (total_size * 0.5):
            if upper_wick < (body_size * 0.4):
                if rsi > 50 and rsi < 88:
                    score = 96.5; signal = "COMPRA"; motive = "FLUXO: VELA DE FORÇA (M1)"
                elif rsi >= 88:
                    score = 93.0; signal = "COMPRA"; motive = "FLUXO: MOMENTUM EXPLOSIVO"

    # Venda
    elif c_now < ema9 and c_now < o_now:
        if body_size > (total_size * 0.5):
            if lower_wick < (body_size * 0.4):
                if rsi < 50 and rsi > 12:
                    score = 96.5; signal = "VENDA"; motive = "FLUXO: VELA DE FORÇA (M1)"
                elif rsi <= 12:
                    score = 93.0; signal = "VENDA"; motive = "FLUXO: MOMENTUM EXPLOSIVO"

    if total_size == 0 or body_size < (total_size * 0.2):
        score = 20.0; signal = "NEUTRO"; motive = "MERCADO LENTO (SEM VOLUME)"

    return signal, score, motive

# --- 6. TELAS ---
def tela_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; border: 1px solid #00ff88; padding: 40px; background: #000; box-shadow: 0 0 20px rgba(0,255,136,0.2);">
                <h1 style="font-family: 'Orbitron'; font-size: 3rem; margin-bottom: 0; color: #00ff88 !important; text-shadow: 0 0 10px #00ff88;">VEX ELITE</h1>
                <p style="letter-spacing: 5px; color: white; font-size: 0.8rem; margin-bottom: 30px;">SYSTEM ACCESS v9.0</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        usuario = st.text_input("ID", placeholder="IDENTIFICAÇÃO", label_visibility="collapsed")
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        senha = st.text_input("KEY", type="password", placeholder="CHAVE DE ACESSO", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("INICIAR PROTOCOLO"):
            if usuario in USER_CREDENTIALS and senha == USER_CREDENTIALS[usuario]:
                st.session_state['logado'] = True
                st.rerun()
            else:
                st.error("ACESSO NEGADO.")

def tela_dashboard():
    # Header
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px;">
            <div><span style="font-family: 'Orbitron'; font-size: 1.5rem; color: #00ff88 !important;">VEX ELITE</span></div>
            <div><span style="background: #00ff88; color: black !important; padding: 2px 8px; font-weight: bold;">ONLINE</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Controle
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.markdown("<h4 style='color: #00ff88 !important;'>ATIVO ALVO</h4>", unsafe_allow_html=True)
        ativo = st.selectbox("", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"], label_visibility="collapsed")
    with c3:
        st.markdown("<h4 style='color: #00ff88 !important;'>AÇÃO</h4>", unsafe_allow_html=True)
        # O botão atualiza o estado
        if st.button("ANALISAR FLUXO (M1)"):
            with st.spinner(f"VARRENDO DADOS DE {ativo}..."):
                df = get_universal_data(ativo)
                if df is not None:
                    sig, precisao, motive = analyze_trend_flow(df)
                    st.session_state['analise_ativa'] = {
                        'df': df, 'sig': sig, 'precisao': precisao, 
                        'motive': motive, 'ativo': ativo,
                        'time': datetime.datetime.now().strftime("%H:%M:%S")
                    }
                else:
                    st.error(f"FALHA DE CONEXÃO: Tente novamente em 3 segundos.")
    st.markdown("</div>", unsafe_allow_html=True)

    # Resultado
    if st.session_state['analise_ativa']:
        dados = st.session_state['analise_ativa']
        
        # Aviso de ativo diferente
        if dados['ativo'] != ativo:
            st.warning(f"⚠️ Mostrando dados anteriores de {dados['ativo']}. Clique no botão para atualizar.")
        
        col_grafico, col_dados = st.columns([2.5, 1.5])
        
        with col_grafico:
            st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
            st.markdown(f"<div style='display:flex; justify-content:space-between;'><h3>GRÁFICO {dados['ativo']}</h3> <span style='color:#aaa'>{dados['time']}</span></div>", unsafe_allow_html=True)
            fig = go.Figure(data=[go.Candlestick(x=dados['df']['timestamp'], open=dados['df']['open'], high=dados['df']['high'], low=dados['df']['low'], close=dados['df']['close'], increasing_line_color='#00ff88', decreasing_line_color='#ff0055')])
            fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10), font=dict(family="Rajdhani", color="white"))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col_dados:
            st.markdown("<div class='neon-card' style='text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
            st.markdown("<p style='color: #aaa !important;'>FORÇA DA TENDÊNCIA</p>", unsafe_allow_html=True)
            
            cor_score = "#00ff88" if dados['precisao'] >= 92 else "#ffcc00"
            if dados['precisao'] < 60: cor_score = "#ff0055"

            st.markdown(f"<div class='score-glow' style='color: {cor_score} !important;'>{dados['precisao']:.1f}%</div>", unsafe_allow_html=True)
            
            if dados['precisao'] >= 92: 
                acao_texto = "COMPRA" if dados['sig'] == "COMPRA" else "VENDA"
                cor_bg = "linear-gradient(45deg, #00ff88, #00cc6a)" if dados['sig'] == "COMPRA" else "linear-gradient(45deg, #ff0055, #cc0044)"
                st.markdown(f"<div style='background: {cor_bg}; padding: 15px; border-radius: 5px; margin: 10px 0; box-shadow: 0 0 20px {cor_score};'><h1 style='margin:0; font-size: 2.5rem; color: black !important; font-weight: 900;'>{acao_texto}</h1></div>", unsafe_allow_html=True)
                st.markdown(f"<div style='border: 1px solid #333; padding: 10px; margin-top: 10px;'><span style='color: #00ff88 !important;'>MOTIVO:</span> {dados['motive']}</div>", unsafe_allow_html=True)
                st.markdown("<p style='margin-top: 15px; color: white !important; font-weight: bold; animation: pulse 1s infinite;'>SIGA O FLUXO IMEDIATAMENTE</p>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='border: 2px solid #ff0055; padding: 15px; margin: 10px 0; color: #ff0055;'><h2 style='margin:0; color: #ff0055 !important;'>NÃO ENTRAR</h2></div>", unsafe_allow_html=True)
                st.markdown(f"<p style='color: #aaa !important;'>Cenário: {dados['motive']}</p>", unsafe_allow_html=True)
            
            st.markdown(f"<div style='margin-top: auto; padding-top: 20px; font-size: 1.5rem;'>${dados['df']['close'].iloc[-1]:.2f}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO"):
        st.session_state['logado'] = False
        st.rerun()

# --- 7. EXECUÇÃO ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
