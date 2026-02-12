import streamlit as st
import pandas as pd
import ccxt
import time
import numpy as np
import plotly.graph_objects as go
import requests

# --- TENTATIVA DE IMPORTAÇÃO SEGURA (PARA NÃO DAR TELA VERMELHA) ---
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

# --- 3. CSS (DESIGN CORRIGIDO PARA O MENU) ---
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
    
    /* --- CORREÇÃO DEFINITIVA DO MENU DROPDOWN --- */
    /* A caixa fechada */
    .stSelectbox div[data-baseweb="select"] > div {
        background-color: #111116 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
    }
    
    /* A lista aberta (Onde estava branco) */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #050505 !important; /* Fundo Preto */
        border: 1px solid #00ff88 !important;
    }
    
    /* As opções da lista */
    li[role="option"] {
        color: white !important; /* Texto Branco */
        background-color: #050505 !important;
    }
    
    /* Quando passa o mouse na opção */
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #00ff88 !important; /* Fundo Verde */
        color: black !important; /* Texto Preto */
        font-weight: bold;
    }
    
    .stSelectbox svg { fill: #00ff88 !important; }
    
    /* INPUTS */
    .stTextInput > div > div > input {
        background-color: #111 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
        border-radius: 8px;
        text-align: center;
        letter-spacing: 2px;
    }
    
    /* BOTÕES */
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

# --- 5. SISTEMA DE DADOS BLINDADO (COM PROTEÇÃO DE ERRO) ---
def get_blindado_data(symbol):
    clean_symbol = symbol.replace("/", "").upper()
    yf_symbol = f"{symbol.split('/')[0]}-USD"
    
    # 1. API BINANCE DIRETA (Prioridade Máxima - Rápida e sem bloqueio comum)
    try:
        url = f"https://api.binance.com/api/v3/klines?symbol={clean_symbol}&interval=1m&limit=60"
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=2)
        if response.status_code == 200:
            data = response.json()
            df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'qav', 'num_trades', 'taker_base_vol', 'taker_quote_vol', 'ignore'])
            df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].astype(float)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
    except: pass

    # 2. CCXT (Backup Padrão)
    try:
        ex = ccxt.binance()
        ohlcv = ex.fetch_ohlcv(symbol, timeframe='1m', limit=60)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except: pass

    # 3. YAHOO FINANCE (Backup Final - Só se tiver instalado)
    if YFINANCE_AVAILABLE:
        try:
            df = yf.download(yf_symbol, period="1d", interval="1m", progress=False)
            if not df.empty:
                df = df.reset_index()
                df.columns = df.columns.str.lower()
                if 'datetime' in df.columns: df = df.rename(columns
