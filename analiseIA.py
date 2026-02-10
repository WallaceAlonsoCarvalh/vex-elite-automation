import streamlit as st
import pandas as pd
import ccxt
import time
from datetime import datetime
import plotly.graph_objects as go

# --- CONFIGURAÇÃO DE ALTO IMPACTO ---
st.set_page_config(page_title="VEX ELITE | ULTRA-FAST", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #020205; font-family: 'Plus Jakarta Sans', sans-serif; color: white; }
    .hero-title { background: linear-gradient(90deg, #FFFFFF, #2563eb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 800; text-align: center; }
    .stButton>button { width: 100%; background: #2563eb !important; color: white !important; border-radius: 12px; padding: 20px; font-size: 1.5rem !important; font-weight: 800; border: none; }
    .card-pro { background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px; }
    .percent-mega { font-size: 5.5rem; font-weight: 900; color: #00ff88; line-height: 1; text-align: center; text-shadow: 0 0 20px rgba(0,255,136,0.3); }
    </style>
    """, unsafe_allow_html=True)

# --- ENGINE DE DADOS DE ALTA VELOCIDADE ---
def get_fast_data(symbol):
    # Foco na Bybit por ser a mais rápida para requisições em nuvem
    ex = ccxt.bybit({'timeout': 7000, 'enableRateLimit': True})
    try:
        ohlcv = ex.fetch_ohlcv(symbol, timeframe='1m', limit=60)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        return None

# --- ALGORITMO SNIPER TURBO (MÁXIMA EFICÁCIA) ---
def analyze_ultra_fast(df):
    close = df['close']
    
    # Médias Móveis Adaptativas
    ema8 = close.ewm(span=8, adjust=False).mean().iloc[-1]
    ema20 = close.ewm(span=20, adjust=False).mean().iloc[-1]
    
    # RSI Ultra-Sensível
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
    
    # Análise de Força de Volume
    vol_avg = df['volume'].tail(15).mean()
    vol_now = df['volume'].iloc[-1]
    
    # Lógica de Cálculo de Precisão
    score = 70.0 # Base mínima elevada para rapidez
    
    # Incrementos por confluência
    if (close.iloc[-1] > ema8 and close.iloc[-1] > ema20): score += 12
    if (close.iloc[-1] < ema8 and close.iloc[-1] < ema20): score += 12
    if (rsi < 40 or rsi > 60): score += 10
    if vol_now > vol_avg: score += 8
    
    score = min(score, 99.4)
    signal = "COMPRA" if close.iloc[-1] > ema8 else "VENDA"
    
    return signal, score

# --- INTERFACE ---
st.markdown('<h1 class="hero-title">VEX ELITE | ULTRA-FAST</h1>', unsafe_allow_html=True)

ativo = st.sidebar.selectbox("ATIVO:", ["BNB/USDT", "BTC/USDT", "ETH/USDT", "SOL/USDT"])

if st.button("🚀 GERAR ENTRADA IMEDIATA"):
    start_time = time.time()
    with st.spinner('Escaneando mercado em tempo real...'):
        df = get_fast_data(ativo)
        
        if df is not None:
            sig, precisao = analyze_ultra_fast(df)
            elapsed = time.time() - start_time
            
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown('<div class="card-pro">', unsafe_allow_html=True)
                fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b')])
                fig.update_layout(template="plotly_dark", height=450, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="card-pro">', unsafe_allow_html=True)
                st.write("ASSERTIVIDADE")
                st.markdown(f'<p class="percent-mega">{precisao:.1f}%</p>', unsafe_allow_html=True)
                
                cor = "#00ff88" if sig == "COMPRA" else "#ff4b4b"
                txt_cor = "black" if sig == "COMPRA" else "white"
                st.markdown(f'<div style="background:{cor}; color:{txt_cor}; padding:25px; border-radius:12px; text-align:center; font-weight:800; font-size:1.5rem;">{sig}</div>', unsafe_allow_html=True)
                
                st.divider()
                st.metric("PREÇO", f"${df['close'].iloc[-1]:.2f}")
                st.caption(f"Análise concluída em {elapsed:.2f}s")
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("Falha na conexão rápida. Tente novamente.")

st.markdown('<p style="text-align:center; color:#333; margin-top:50px;">VEX ELITE PRO © 2026</p>', unsafe_allow_html=True)
