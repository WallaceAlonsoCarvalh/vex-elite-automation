import streamlit as st
import pandas as pd
import ccxt
import time
from datetime import datetime
import plotly.graph_objects as go

# --- CONFIGURAÇÃO ---
st.set_page_config(page_title="VEX ELITE | AUTOMATION", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
    html, body, [data-testid="stAppViewContainer"] { background-color: #020205; font-family: 'Plus Jakarta Sans', sans-serif; color: white; }
    .hero-title { background: linear-gradient(90deg, #FFFFFF, #71717a); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 800; text-align: center; }
    .warning-box { background-color: rgba(255, 165, 0, 0.1); border: 1px solid orange; color: orange; padding: 15px; border-radius: 12px; text-align: center; font-weight: bold; margin-bottom: 25px; }
    .stButton>button { width: 100%; background-color: #2563eb !important; color: white !important; border-radius: 12px; padding: 25px; font-size: 1.5rem !important; font-weight: 800; }
    .accuracy-display { text-align: center; background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); margin: 15px 0; }
    .percent-number { font-size: 4.5rem; font-weight: 900; color: #00ff88; }
    </style>
    """, unsafe_allow_html=True)

# --- BUSCA DE DADOS OTIMIZADA ---
def get_live_data(symbol):
    try:
        # Criamos a conexão com timeout maior para evitar travamentos
        exchange = ccxt.binance({'timeout': 20000, 'enableRateLimit': True})
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=60)
        if not ohlcv: return None
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except Exception as e:
        st.error(f"Erro na API: {e}")
        return None

def analyze_market(df):
    close = df['close']
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
    ema8 = close.ewm(span=8).mean().iloc[-1]
    vol_now = df['volume'].iloc[-1]
    vol_avg = df['volume'].rolling(20).mean().iloc[-1]
    
    chance = 65.0
    if (rsi < 35) or (rsi > 65): chance += 15
    if vol_now > vol_avg: chance += 15
    chance = min(chance, 99.8)
    
    signal = "COMPRA" if close.iloc[-1] > ema8 else "VENDA"
    return signal, rsi, chance

# --- INTERFACE ---
st.markdown('<h1 class="hero-title">VEX ELITE AUTOMATION</h1>', unsafe_allow_html=True)
st.markdown('<div class="warning-box">⚠️ RECOMENDAÇÃO: ENTRADAS ABAIXO DE 90% POSSUEM RISCO ELEVADO.</div>', unsafe_allow_html=True)

ativo = st.sidebar.selectbox("ESCOLHA O ATIVO:", ["BNB/USDT", "BTC/USDT", "ETH/USDT", "SOL/USDT"])

if st.button("🚀 GERAR ENTRADA PARA PRÓXIMA VELA"):
    with st.spinner('Escaneando mercado...'):
        df = get_live_data(ativo)
        
        if df is not None:
            col1, col2 = st.columns([2, 1])
            with col1:
                fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b')])
                fig.update_layout(template="plotly_dark", height=500, xaxis_rangeslider_visible=False, margin=dict(l=0,r=0,t=0,b=0))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                sig, rsi_val, percentual = analyze_market(df)
                st.metric("PREÇO ATUAL", f"${df['close'].iloc[-1]:.2f}")
                st.markdown(f'<div class="accuracy-display"><p style="color:#888;">CHANCE DE ACERTO</p><p class="percent-number">{percentual:.1f}%</p><p style="color:#3b82f6; font-weight:800;">PRÓXIMA VELA</p></div>', unsafe_allow_html=True)
                
                cor_bg = "#00ff88" if sig == "COMPRA" else "#ff4b4b"
                cor_txt = "black" if sig == "COMPRA" else "white"
                st.markdown(f'<div style="background:{cor_bg}; color:{cor_txt}; padding:30px; border-radius:15px; text-align:center;"><h2 style="margin:0;">{"▲" if sig == "COMPRA" else "▼"} {sig}</h2></div>', unsafe_allow_html=True)
        else:
            st.warning("A corretora demorou a responder. Clique novamente em 5 segundos.")

st.markdown('<p style="text-align:center; color:#333; margin-top:80px;">VEX ELITE © 2026</p>', unsafe_allow_html=True)
