import streamlit as st
import pandas as pd
import ccxt
import time
import numpy as np
import plotly.graph_objects as go
import requests

# --- PROTEÇÃO CONTRA ERRO DE IMPORTAÇÃO (ANTI-CRASH) ---
# Se o yfinance não estiver instalado, o sistema NÃO VAI CAIR.
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(
    page_title="VEX ELITE | TERMINAL",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CREDENCIAIS ---
USER_CREDENTIALS = {
    "wallace": "admin123",  
    "cliente01": "pro2026", 
}

# --- 3. CSS (DESIGN CORRIGIDO: MENU E CORES) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        color: #ffffff;
    }
    
    h1, h2, h3, h4, h5, h6, p, label, div, span, li {
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif;
    }
    
    /* --- CORREÇÃO DO MENU DROPDOWN (PRETO E VERDE) --- */
    /* A caixa fechada onde clica */
    div[data-baseweb="select"] > div {
        background-color: #111116 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
    }
    
    /* A lista que abre (Popover) - Forçando fundo preto */
    div[data-baseweb="popover"] {
        background-color: #050505 !important;
        border: 1px solid #00ff88 !important;
    }
    
    /* Os itens da lista */
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #050505 !important;
    }
    
    li[role="option"] {
        background-color: #050505 !important;
        color: white !important;
    }
    
    /* Quando passa o mouse (Hover) */
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #00ff88 !important;
        color: black !important;
        font-weight: bold;
    }
    
    /* Ícone Seta */
    .stSelectbox svg { fill: #00ff88 !important; }
    
    /* --- INPUTS --- */
    .stTextInput > div > div > input {
        background-color: #111 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
        border-radius: 8px;
        text-align: center;
        letter-spacing: 2px;
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
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        backdrop-filter: blur(10px);
    }
    
    .score-glow {
        font-size: 6rem;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        text-shadow: 0 0 40px currentColor;
        line-height: 1;
        margin: 20px 0;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 4. SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'user_logged' not in st.session_state:
    st.session_state['user_logged'] = ""

# --- 5. SISTEMA BLINDADO DE DADOS (COM MULTI-EXCHANGE) ---
def get_blindado_data(symbol):
    clean_symbol = symbol.replace("/", "").upper()
    yf_symbol = f"{symbol.split('/')[0]}-USD"
    
    # 1. API BINANCE DIRETA (Mais rápida)
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={clean_symbol}&interval=1m&limit=60"
        # Cabeçalho de navegador para evitar bloqueio 403
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        
        response = requests.get(url, headers=headers, timeout=3)
        if response.status_code == 200:
            data = response.json()
            if len(data) > 0:
                df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'])
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype(float)
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
    except Exception:
        pass # Falha silenciosa

    # 2. CCXT BINANCE (Backup Padrão)
    try:
        ex = ccxt.binance({'timeout': 3000, 'enableRateLimit': True})
        ohlcv = ex.fetch_ohlcv(symbol, timeframe='1m', limit=60)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        pass

    # 3. CCXT KUCOIN (Alternativa se Binance cair)
    try:
        ex = ccxt.kucoin({'timeout': 3000, 'enableRateLimit': True})
        # Kucoin pode usar simbolos diferentes, tenta direto
        ohlcv = ex.fetch_ohlcv(symbol, timeframe='1m', limit=60)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        pass

    # 4. YAHOO FINANCE (Último recurso, só se instalado)
    if YFINANCE_AVAILABLE:
        try:
            df = yf.download(yf_symbol, period="1d", interval="1m", progress=False)
            if not df.empty:
                df = df.reset_index()
                df.columns = df.columns.str.lower()
                if 'datetime' in df.columns: df = df.rename(columns={'datetime': 'timestamp'})
                if 'date' in df.columns: df = df.rename(columns={'date': 'timestamp'})
                return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        except:
            pass

    return None

# --- 6. INTELIGÊNCIA VEX ATOMIC v6.1 (LÓGICA HFT MANTIDA) ---
def analyze_atomic_pressure(df):
    if df is None or df.empty:
        return "NEUTRO", 0.0, "AGUARDANDO DADOS..."

    close = df['close'].values
    open_ = df['open'].values
    high = df['high'].values
    low = df['low'].values
    
    # Vela Atual (Faltando 10s)
    c_now = close[-1]
    o_now = open_[-1]
    h_now = high[-1]
    l_now = low[-1]
    
    body_size = abs(c_now - o_now)
    upper_wick = h_now - max(c_now, o_now)
    lower_wick = min(c_now, o_now) - l_now
    total_size = h_now - l_now
    
    # --- STOCHASTIC RSI ---
    rsi_period = 14
    delta = pd.Series(close).diff()
    gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi = rsi.fillna(50)
    
    min_rsi = rsi.rolling(window=14).min()
    max_rsi = rsi.rolling(window=14).max()
    denominator = max_rsi - min_rsi
    denominator = denominator.replace(0, 1) 
    stoch_rsi = (rsi - min_rsi) / denominator
    k = stoch_rsi.rolling(window=3).mean().iloc[-1] * 100 
    
    # EMA9
    ema9 = pd.Series(close).ewm(span=9).mean().iloc[-1]
    
    score = 0.0
    signal = "NEUTRO"
    motive = "ANALISANDO..."

    # --- LÓGICA DE DECISÃO ---
    
    # 1. VENDA (REJEIÇÃO DE TOPO)
    if k > 85:
        if upper_wick > (body_size * 0.8): 
            score = 98.5
            signal = "VENDA"
            motive = "ATOMIC: REJEIÇÃO EXTREMA DE TOPO"
        elif c_now < o_now: 
            score = 94.0
            signal = "VENDA"
            motive = "ATOMIC: VIRADA DE VELA (CORREÇÃO)"

    # 2. COMPRA (REJEIÇÃO DE FUNDO)
    elif k < 15:
        if lower_wick > (body_size * 0.8):
            score = 98.5
            signal = "COMPRA"
            motive = "ATOMIC: REJEIÇÃO EXTREMA DE FUNDO"
        elif c_now > o_now:
            score = 94.0
            signal = "COMPRA"
            motive = "ATOMIC: VIRADA DE VELA (CORREÇÃO)"

    # 3. CONTINUIDADE
    else:
        if c_now > ema9 and c_now > o_now and upper_wick < (body_size * 0.3):
             if k > 35 and k < 75:
                score = 92.0
                signal = "COMPRA"
                motive = "FLUXO: IMPULSÃO DE ALTA LIMPA"
        
        elif c_now < ema9 and c_now < o_now and lower_wick < (body_size * 0.3):
            if k > 25 and k < 65:
                score = 92.0
                signal = "VENDA"
                motive = "FLUXO: IMPULSÃO DE BAIXA LIMPA"

    # TRAVA DE SEGURANÇA (DOJI)
    if total_size == 0 or body_size < (total_size * 0.15):
        score = 15.0
        signal = "NEUTRO"
        motive = "MERCADO TRAVADO (DOJI)"

    return signal, score, motive

# --- 7. TELA DE LOGIN ---
def tela_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; border: 1px solid #00ff88; padding: 40px; background: #000; box-shadow: 0 0 20px rgba(0,255,136,0.2);">
                <h1 style="font-family: 'Orbitron'; font-size: 3rem; margin-bottom: 0; color: #00ff88 !important; text-shadow: 0 0 10px #00ff88;">VEX ELITE</h1>
                <p style="letter-spacing: 5px; color: white; font-size: 0.8rem; margin-bottom: 30px;">SYSTEM ACCESS v6.1 (BLINDADO)</p>
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
                st.session_state['user_logged'] = usuario
                st.rerun()
            else:
                st.error("ACESSO NEGADO.")

# --- 8. TELA DASHBOARD ---
def tela_dashboard():
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px;">
            <div>
                <span style="font-family: 'Orbitron'; font-size: 1.5rem; color: #00ff88 !important;">VEX ELITE</span>
                <span style="background: #00ff88; color: black !important; padding: 2px 8px; font-weight: bold; font-size: 0.7rem; margin-left: 10px;">ONLINE</span>
            </div>
            <div style="text-align: right;">
                <span style="color: #aaa !important; font-size: 0.9rem;">OPERADOR:</span>
    """, unsafe_allow_html=True)
    st.markdown(f"<span style='font-family: Orbitron; font-size: 1.2rem; color: white !important;'>{st.session_state['user_logged'].upper()}</span></div>", unsafe_allow_html=True)
    
    st.markdown("<div class='neon-card' style='margin-bottom: 20px;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.markdown("<h4 style='margin-bottom: 5px; color: #00ff88 !important;'>ATIVO ALVO</h4>", unsafe_allow_html=True)
        ativo = st.selectbox("", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"], label_visibility="collapsed")
    with c3:
        st.markdown("<h4 style='margin-bottom: 5px; color: #00ff88 !important;'>AÇÃO</h4>", unsafe_allow_html=True)
        acionar = st.button("VARREDURA ATÔMICA")
    st.markdown("</div>", unsafe_allow_html=True)

    if acionar:
        with st.spinner(f"SINCRONIZANDO DADOS BLINDADOS DE {ativo}..."):
            df = get_blindado_data(ativo)
            
            if df is not None:
                sig, precisao, motivo = analyze_atomic_pressure(df)
                
                col_grafico, col_dados = st.columns([2.5, 1.5])
                
                with col_grafico:
                    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='font-family: Orbitron;'>GRÁFICO M1 | {ativo}</h3>", unsafe_allow_html=True)
                    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00ff88', decreasing_line_color='#ff0055')])
                    fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10), font=dict(family="Rajdhani", color="white"))
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with col_dados:
                    st.markdown("<div class='neon-card' style='text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
                    st.markdown("<p style='color: #aaa !important; font-size: 0.9rem;'>PROBABILIDADE INSTANTÂNEA</p>", unsafe_allow_html=True)
                    
                    cor_score = "#00ff88" if precisao >= 92 else "#ffcc00"
                    if precisao < 60: cor_score = "#ff0055"

                    st.markdown(f"<div class='score-glow' style='color: {cor_score} !important;'>{precisao:.1f}%</div>", unsafe_allow_html=True)
                    
                    if precisao >= 92: 
                        acao_texto = "COMPRA" if sig == "COMPRA" else "VENDA"
                        cor_bg = "linear-gradient(45deg, #00ff88, #00cc6a)" if sig == "COMPRA" else "linear-gradient(45deg, #ff0055, #cc0044)"
                        
                        st.markdown(f"""
                            <div style="background: {cor_bg}; padding: 15px; border-radius: 5px; margin: 10px 0; box-shadow: 0 0 20px {cor_score};">
                                <h1 style="margin:0; font-size: 2.5rem; color: black !important; font-weight: 900;">{acao_texto}</h1>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"<div style='border: 1px solid #333; padding: 10px; margin-top: 10px;'><span style='color: #00ff88 !important;'>MOTIVO:</span> {motivo}</div>", unsafe_allow_html=True)
                        st.markdown("<p style='margin-top: 15px; color: white !important; font-weight: bold; animation: pulse 1s infinite;'>ENTRE IMEDIATAMENTE</p>", unsafe_allow_html=True)
                    
                    else:
                        st.markdown("""
                            <div style="border: 2px solid #ff0055; padding: 15px; margin: 10px 0; color: #ff0055;">
                                <h2 style="margin:0; color: #ff0055 !important;">NÃO ENTRAR</h2>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #aaa !important;'>Cenário: {motivo}</p>", unsafe_allow_html=True)
                        st.markdown("<p style='font-size: 0.8rem; color: #ff0055 !important;'>AGUARDE UMA OPORTUNIDADE CLARA.</p>", unsafe_allow_html=True)
                    
                    st.markdown(f"<div style='margin-top: auto; padding-top: 20px; font-size: 1.5rem;'>${df['close'].iloc[-1]:.2f}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                # Agora com 3 tentativas, é quase impossível ver esta mensagem
                st.error("ERRO DE REDE: Todas as conexões (Binance/Kucoin) falharam. Verifique sua internet.")

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO"):
        st.session_state['logado'] = False
        st.rerun()

# --- 8. EXECUÇÃO ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
