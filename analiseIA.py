import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import time 
import random

# --- TENTATIVA DE IMPORTAR YFINANCE (PADRÃO OURO PARA FOREX) ---
try:
    import yfinance as yf
    DATA_SOURCE = "YFINANCE"
except ImportError:
    DATA_SOURCE = "SIMULATION"

# --- 1. CONFIGURAÇÃO (FOREX MODE) ---
st.set_page_config(
    page_title="VEX ELITE | FOREX TERMINAL",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS (VISUAL DARK NEON CORRIGIDO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(at 50% 0%, #1a1a2e 0%, #000000 100%);
        color: white;
    }
    
    h1, h2, h3, p, div, span { font-family: 'Rajdhani', sans-serif !important; }
    
    /* MENU DROPDOWN (CORRIGIDO PARA VISIBILIDADE TOTAL) */
    .stSelectbox > div > div {
        background-color: #000000 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #000000 !important;
        border: 1px solid #00ff88 !important;
    }
    li[role="option"] {
        background-color: #000000 !important;
        color: white !important;
    }
    li[role="option"]:hover {
        background-color: #00ff88 !important;
        color: black !important;
        font-weight: bold;
    }
    .stSelectbox svg { fill: #00ff88 !important; }
    
    /* BOTÕES */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #00ff88 !important;
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        text-transform: uppercase;
        padding: 20px;
        transition: 0.3s;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.1);
    }
    .stButton > button:hover {
        background: #00ff88 !important;
        color: black !important;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.6);
    }

    /* INPUTS */
    .stTextInput input {
        background-color: #111 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
        text-align: center;
    }
    
    .neon-card {
        background: rgba(255,255,255,0.02);
        border: 1px solid #333;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    .score-glow {
        font-family: 'Orbitron';
        font-size: 5rem;
        font-weight: 900;
        text-shadow: 0 0 30px currentColor;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. ESTADO DA SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'analise_forex' not in st.session_state:
    st.session_state['analise_forex'] = None

# CREDENCIAIS FIXAS
CREDENCIAIS = {
    "wallace": "admin123",
    "cliente01": "pro2026"
}

# --- 4. COLETOR DE DADOS FOREX ---
def get_forex_data(pair):
    """
    Busca dados de Forex.
    Mapeia: EUR/USD -> EURUSD=X (Padrão Yahoo)
    """
    symbol_map = {
        "EUR/USD": "EURUSD=X",
        "GBP/USD": "GBPUSD=X",
        "USD/JPY": "JPY=X",
        "USD/BRL": "BRL=X",
        "EUR/JPY": "EURJPY=X",
        "GBP/JPY": "GBPJPY=X",
        "AUD/USD": "AUDUSD=X",
        "USD/CAD": "CAD=X"
    }
    
    ticker = symbol_map.get(pair, "EURUSD=X")
    
    # MODO REAL (YFINANCE)
    if DATA_SOURCE == "YFINANCE":
        try:
            # Tenta baixar dados reais
            df = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not df.empty:
                df = df.reset_index()
                # Padronizar colunas
                df.columns = df.columns.str.lower()
                if 'datetime' in df.columns: df = df.rename(columns={'datetime': 'timestamp'})
                if 'date' in df.columns: df = df.rename(columns={'date': 'timestamp'})
                # Garante fuso horário local aproximado
                df['timestamp'] = df['timestamp'].dt.tz_localize(None) 
                return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']], "MERCADO REAL (ONLINE)"
        exceptException:
            pass # Falhou, vai pro simulador

    # MODO SIMULAÇÃO (PREVINE ERROS VERMELHOS)
    # Gera um gráfico matemático realista para não travar o app se a API falhar
    dates = pd.date_range(end=datetime.datetime.now(), periods=60, freq='1min')
    base_price = 1.0800 if "EUR" in pair else 150.00 if "JPY" in pair else 1.2600
    
    np.random.seed(int(time.time()))
    returns = np.random.normal(0, 0.0002, 60)
    price = base_price * (1 + returns).cumprod()
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': price,
        'close': price * (1 + np.random.normal(0, 0.0001, 60)),
        'high': price * 1.0002,
        'low': price * 0.9998,
        'volume': np.random.randint(100, 1000, 60)
    })
    return df, "SIMULAÇÃO (CONEXÃO INSTÁVEL)"

# --- 5. CÉREBRO VEX-FOREX (LÓGICA DE PIPS) ---
def analyze_forex_logic(df):
    if df is None or df.empty:
        return "NEUTRO", 0.0, "SEM DADOS"

    # Preparação
    close = df['close'].values
    open_ = df['open'].values
    high = df['high'].values
    low = df['low'].values
    
    c_now = close[-1]
    o_now = open_[-1]
    
    # Tamanho em Pontos (Forex é sutil)
    body = abs(c_now - o_now)
    total_range = high[-1] - low[-1]
    
    # Médias (Tendência)
    ema9 = pd.Series(close).ewm(span=9).mean().iloc[-1]
    
    # RSI (Força)
    delta = pd.Series(close).diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    rsi = 50 if np.isnan(rsi) else rsi
    
    score = 0.0
    signal = "NEUTRO"
    motive = "ANALISANDO..."

    # --- LÓGICA DE FLUXO FOREX ---
    # Forex respeita muito tendência de curto prazo (M1)
    
    # COMPRA (CALL)
    if c_now > ema9 and c_now > o_now: # Acima da média + Vela Verde
        # Se o corpo for saudável (> 50% da vela)
        if body > (total_range * 0.5):
            if rsi > 45 and rsi < 80: # RSI saudável
                score = 95.0
                signal = "COMPRA"
                motive = "FOREX: FLUXO DE ALTA (MOMENTUM)"
            elif rsi >= 80:
                score = 91.0
                signal = "COMPRA"
                motive = "FOREX: FORÇA EXTREMA DE COMPRA"

    # VENDA (PUT)
    elif c_now < ema9 and c_now < o_now: # Abaixo da média + Vela Vermelha
        if body > (total_range * 0.5):
            if rsi < 55 and rsi > 20: # RSI saudável
                score = 95.0
                signal = "VENDA"
                motive = "FOREX: FLUXO DE BAIXA (MOMENTUM)"
            elif rsi <= 20:
                score = 91.0
                signal = "VENDA"
                motive = "FOREX: FORÇA EXTREMA DE VENDA"

    # Falsos Rompimentos (Pavio Grande)
    upper_wick = high[-1] - max(c_now, o_now)
    lower_wick = min(c_now, o_now) - low[-1]
    
    if upper_wick > (body * 2): # Pavio superior 2x maior que corpo
        score = 88.0
        signal = "VENDA"
        motive = "REJEIÇÃO DE TOPO (PAVIO)"
        
    if lower_wick > (body * 2): # Pavio inferior 2x maior que corpo
        score = 88.0
        signal = "COMPRA"
        motive = "REJEIÇÃO DE FUNDO (PAVIO)"

    # Trava de Segurança
    if total_range == 0:
        score = 0.0
        signal = "NEUTRO"
        motive = "MERCADO PARADO"

    return signal, score, motive

# --- 6. TELAS ---
def tela_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("""
            <div style="text-align: center; border: 1px solid #00ff88; padding: 40px; background: #000; box-shadow: 0 0 20px rgba(0,255,136,0.2);">
                <h1 style="font-family: 'Orbitron'; font-size: 3rem; margin-bottom: 0; color: #00ff88 !important;">VEX ELITE</h1>
                <p style="letter-spacing: 5px; color: white; font-size: 0.8rem; margin-bottom: 30px;">FOREX ACCESS</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        user = st.text_input("ID", placeholder="USUÁRIO", label_visibility="collapsed")
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        pwd = st.text_input("KEY", type="password", placeholder="SENHA", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ACESSAR SISTEMA"):
            if user in CREDENCIAIS and pwd == CREDENCIAIS[user]:
                st.session_state['logado'] = True
                st.rerun()
            else:
                st.error("DADOS INVÁLIDOS")

def tela_dashboard():
    # Header
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 20px;">
            <div><span style="font-family: 'Orbitron'; font-size: 1.5rem; color: #00ff88 !important;">VEX ELITE</span> <span style="color:#aaa; font-size:0.8rem;">| FOREX TERMINAL</span></div>
            <div><span style="background: #00ff88; color: black !important; padding: 2px 8px; font-weight: bold;">CONECTADO</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    # Controles
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("<h4 style='color: #00ff88;'>PAR DE MOEDAS</h4>", unsafe_allow_html=True)
        ativo = st.selectbox("", ["EUR/USD", "GBP/USD", "USD/JPY", "USD/BRL", "EUR/JPY", "GBP/JPY", "AUD/USD", "USD/CAD"], label_visibility="collapsed")
    with c2:
        st.markdown("<h4 style='color: #00ff88;'>EXECUÇÃO</h4>", unsafe_allow_html=True)
        if st.button("ANALISAR AGORA"):
            with st.spinner("CALCULANDO PIPS E TENDÊNCIA..."):
                df, status = get_forex_data(ativo)
                sig, score, motive = analyze_forex_logic(df)
                st.session_state['analise_forex'] = {
                    'df': df, 'sig': sig, 'score': score, 'motive': motive, 'ativo': ativo, 'status': status,
                    'hora': datetime.datetime.now().strftime("%H:%M:%S")
                }
    st.markdown("</div>", unsafe_allow_html=True)

    # Resultados
    if st.session_state['analise_forex']:
        res = st.session_state['analise_forex']
        
        # Alerta se mudou o ativo sem clicar
        if res['ativo'] != ativo:
            st.info(f"Clique em ANALISAR AGORA para atualizar de {res['ativo']} para {ativo}.")
        
        g_col, d_col = st.columns([2, 1])
        
        with g_col:
            st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
            st.markdown(f"<div style='display:flex; justify-content:space-between'><h3>GRÁFICO {res['ativo']}</h3> <span style='color:#aaa; font-size:0.8rem'>{res['status']} | {res['hora']}</span></div>", unsafe_allow_html=True)
            
            fig = go.Figure(data=[go.Candlestick(x=res['df']['timestamp'], open=res['df']['open'], high=res['df']['high'], low=res['df']['low'], close=res['df']['close'], increasing_line_color='#00ff88', decreasing_line_color='#ff0055')])
            fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
        with d_col:
            st.markdown("<div class='neon-card' style='text-align:center; height:100%; display:flex; flex-direction:column; justify-content:center;'>", unsafe_allow_html=True)
            st.markdown("<p style='color:#aaa'>FORÇA DA TENDÊNCIA</p>", unsafe_allow_html=True)
            
            cor = "#00ff88" if res['score'] >= 90 else "#ffcc00"
            if res['score'] < 60: cor = "#ff0055"
            
            st.markdown(f"<div class='score-glow' style='color:{cor} !important'>{res['score']:.1f}%</div>", unsafe_allow_html=True)
            
            if res['score'] >= 90:
                sinal = res['sig']
                bg = "linear-gradient(45deg, #00ff88, #00cc6a)" if sinal == "COMPRA" else "linear-gradient(45deg, #ff0055, #cc0044)"
                st.markdown(f"<div style='background:{bg}; padding:15px; border-radius:5px; margin:10px 0; color:black; font-weight:900; font-size:2rem;'>{sinal}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='border:1px solid #333; padding:10px; margin-top:10px;'><span style='color:#00ff88'>MOTIVO:</span> {res['motive']}</div>", unsafe_allow_html=True)
                st.markdown("<p style='margin-top:10px; font-weight:bold; animation: pulse 1s infinite;'>ENTRADA CONFIRMADA</p>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='border:1px solid #ffcc00; color:#ffcc00; padding:10px; margin:10px 0; font-weight:bold;'>AGUARDE</div>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:0.8rem; color:#aaa'>{res['motive']}</p>", unsafe_allow_html=True)
                
            st.markdown(f"<div style='margin-top:auto; font-size:1.5rem; padding-top:20px;'>{res['df']['close'].iloc[-1]:.5f}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("SAIR"):
        st.session_state['logado'] = False
        st.rerun()

# --- 7. START ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
