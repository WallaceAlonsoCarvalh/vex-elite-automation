import streamlit as st
import pandas as pd
import ccxt
import time
import numpy as np
import plotly.graph_objects as go

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

# --- 3. CSS (NÃO ALTERADO) ---
st.markdown(""" 
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
.stApp { background-color: #050505; background-image: radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%); color: #ffffff; }
h1, h2, h3, h4, h5, h6, p, label, div, span, li { color: #ffffff !important; font-family: 'Rajdhani', sans-serif; }
.stSelectbox > div > div { background-color: #111116 !important; color: #00ff88 !important; border: 1px solid #333 !important; font-weight: bold; }
ul[data-testid="stSelectboxVirtualDropdown"] { background-color: #0a0a0a !important; border: 1px solid #00ff88 !important; }
li[role="option"] { color: white !important; }
li[role="option"]:hover { background-color: #00ff88 !important; color: black !important; }
.stSelectbox svg { fill: #00ff88 !important; }
.stTextInput > div > div > input { background-color: #111 !important; color: #00ff88 !important; border: 1px solid #333 !important; border-radius: 8px; text-align: center; letter-spacing: 2px; }
.stButton > button { background: transparent !important; border: 1px solid #00ff88 !important; color: #00ff88 !important; font-family: 'Orbitron', sans-serif; text-transform: uppercase; font-weight: 900; padding: 20px; border-radius: 0px; transition: all 0.3s ease; box-shadow: 0 0 10px rgba(0, 255, 136, 0.1); }
.stButton > button:hover { background: #00ff88 !important; color: #000 !important; box-shadow: 0 0 30px rgba(0, 255, 136, 0.6); transform: scale(1.02); }
.neon-card { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); padding: 25px; border-radius: 10px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); backdrop-filter: blur(10px); }
.score-glow { font-size: 6rem; font-family: 'Orbitron', sans-serif; font-weight: 900; text-shadow: 0 0 40px currentColor; line-height: 1; margin: 20px 0; }
#MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'user_logged' not in st.session_state:
    st.session_state['user_logged'] = ""

# --- DADOS ---
def get_fast_data(symbol):
    exchanges = [ccxt.binance({'timeout':4000}), ccxt.bybit({'timeout':4000})]
    for ex in exchanges:
        try:
            ohlcv = ex.fetch_ohlcv(symbol, timeframe='1m', limit=150)
            df = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            return df
        except:
            continue
    return None

def get_trend_filter(symbol):
    try:
        ex = ccxt.binance({'timeout':4000})
        ohlcv = ex.fetch_ohlcv(symbol, timeframe='5m', limit=80)
        df5 = pd.DataFrame(ohlcv, columns=['timestamp','open','high','low','close','volume'])
        ema9 = df5['close'].ewm(span=9).mean().iloc[-1]
        ema21 = df5['close'].ewm(span=21).mean().iloc[-1]
        if ema9 > ema21:
            return "ALTA"
        elif ema9 < ema21:
            return "BAIXA"
        else:
            return "LATERAL"
    except:
        return "LATERAL"

def calculate_choppiness(df):
    high = df['high']
    low = df['low']
    close = df['close']
    tr = pd.concat([
        high - low,
        abs(high - close.shift(1)),
        abs(low - close.shift(1))
    ], axis=1).max(axis=1)
    atr = tr.rolling(14).sum()
    highh = high.rolling(14).max()
    lowl = low.rolling(14).min()
    ci = 100 * np.log10(atr / (highh - lowl)) / np.log10(14)
    return ci.iloc[-2]

def analyze_all_hypothesis(df, symbol):

    trend_m5 = get_trend_filter(symbol)

    close = df['close']
    open_ = df['open']
    high = df['high']
    low = df['low']
    vol = df['volume']

    # 🔴 vela FECHADA
    c_now = close.iloc[-2]
    o_now = open_.iloc[-2]
    h_now = high.iloc[-2]
    l_now = low.iloc[-2]

    c_prev = close.iloc[-3]
    o_prev = open_.iloc[-3]

    score = 0
    signal = "NEUTRO"
    motive = "SEM CONFLUÊNCIA"

    # Filtro lateral
    if calculate_choppiness(df) > 60:
        return "NEUTRO", 0, "MERCADO LATERAL"

    # RSI
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    rsi_now = rsi.iloc[-2]

    # Volume forte
    vol_media = vol.iloc[-25:-2].mean()
    volume_forte = vol.iloc[-2] > vol_media * 1.4

    # Médias
    ema9 = close.ewm(span=9).mean().iloc[-2]
    ema21 = close.ewm(span=21).mean().iloc[-2]
    ema50 = close.ewm(span=50).mean().iloc[-2]

    tamanho_vela = abs(c_now - o_now)
    tamanho_medio = abs(close.iloc[-15:-2] - open_.iloc[-15:-2]).mean()

    pavio_sup = h_now - max(c_now, o_now)
    pavio_inf = min(c_now, o_now) - l_now

    # CONTINUIDADE
    if trend_m5 == "ALTA":
        if c_now > ema9 > ema21 > ema50 and volume_forte and rsi_now > 50 and tamanho_vela > tamanho_medio:
            score += 50
            signal = "COMPRA"
            motive = "TENDÊNCIA FORTE"

    if trend_m5 == "BAIXA":
        if c_now < ema9 < ema21 < ema50 and volume_forte and rsi_now < 50 and tamanho_vela > tamanho_medio:
            score += 50
            signal = "VENDA"
            motive = "TENDÊNCIA FORTE"

    # ENGOLFO
    if c_now > o_now and c_prev < o_prev and c_now > o_prev and o_now < c_prev:
        if volume_forte and trend_m5 == "ALTA":
            score += 30
            signal = "COMPRA"
            motive = "ENGOLFO VALIDADO"

    if c_now < o_now and c_prev > o_prev and c_now < o_prev and o_now > c_prev:
        if volume_forte and trend_m5 == "BAIXA":
            score += 30
            signal = "VENDA"
            motive = "ENGOLFO VALIDADO"

    # BLOQUEIO CONTRA TENDÊNCIA
    if trend_m5 == "ALTA" and signal == "VENDA":
        return "NEUTRO", 0, "CONTRA TENDÊNCIA M5"

    if trend_m5 == "BAIXA" and signal == "COMPRA":
        return "NEUTRO", 0, "CONTRA TENDÊNCIA M5"

    # SCORE FINAL
    if score >= 70:
        return signal, 94.0, motive
    elif score >= 50:
        return signal, 91.0, motive
    else:
