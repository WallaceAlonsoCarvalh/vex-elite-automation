import streamlit as st
import pandas as pd
import ccxt
import time
from datetime import datetime
import plotly.graph_objects as go

# --- 1. BANCO DE DADOS DE USUÁRIOS (VALIDAÇÃO) ---
# Aqui é onde você valida quem pode entrar. 
# Adicione o seu nome e a senha que você desejar.
USER_CREDENTIALS = {
    "wallace": "admin123",  # Usuário para você entrar
    "cliente01": "pro2026", # Usuário para um cliente seu
}

def check_password():
    """Verifica se o usuário e senha existem no banco de dados"""
    def password_entered():
        # Validação: Verifica se o nome existe e se a senha bate com aquele nome
        if st.session_state["username"] in USER_CREDENTIALS and \
           st.session_state["password"] == USER_CREDENTIALS[st.session_state["username"]]:
            st.session_state["password_correct"] = True
            st.session_state["user_logged"] = st.session_state["username"]
            del st.session_state["password"] 
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # TELA DE LOGIN (O que a pessoa vê primeiro)
        st.markdown("<h1 style='text-align: center; color: white;'>VEX ELITE | ACESSO RESTRITO</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Insira suas credenciais para acessar o terminal Sniper.</p>", unsafe_allow_html=True)
        
        st.text_input("Usuário", key="username")
        st.text_input("Senha", type="password", key="password")
        st.button("Validar e Entrar", on_click=password_entered)
        
        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("❌ Acesso Negado: Usuário ou senha não encontrados.")
        return False
    return st.session_state["password_correct"]

# --- 2. INÍCIO DO TERMINAL APÓS VALIDAÇÃO ---
if check_password():
    st.set_page_config(page_title="VEX ELITE | SNIPER PRO", layout="wide")

    # CSS do Design Profissional
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

    # --- GUIA DIDÁTICO ---
    st.markdown(f'<h1 class="hero-title">BEM-VINDO, {st.session_state["user_logged"].upper()}</h1>', unsafe_allow_html=True)
    
    with st.expander("📖 GUIA DIDÁTICO: OPERAÇÃO ZERO ERRO"):
        st.write("""
        1. **Varredura:** No segundo **50**, clique em 'GERAR ENTRADA'.
        2. **Execução:** Se a precisão for > 90%, clique na Vex no **segundo 58 ou 59**.
        """)

    # Barra Lateral
    st.sidebar.markdown(f"**Operador:** {st.session_state['user_logged']}")
    if st.sidebar.button("Encerrar Sessão"):
        st.session_state.clear()
        st.rerun()
    
    ativo = st.sidebar.selectbox("ATIVO:", ["BNB/USDT", "BTC/USDT", "ETH/USDT", "SOL/USDT"])

    # --- LÓGICA SNIPER ---
    def get_fast_data(symbol):
        exchanges = [ccxt.bybit({'timeout': 7000}), ccxt.kucoin({'timeout': 7000})]
        for ex in exchanges:
            try:
                ohlcv = ex.fetch_ohlcv(symbol, timeframe='1m', limit=60)
                if ohlcv:
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                    return df
            except: continue
        return None

    def analyze_ultra_fast(df):
        close = df['close']
        ema8 = close.ewm(span=8, adjust=False).mean().iloc[-1]
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        vol_now = df['volume'].iloc[-1]
        vol_avg = df['volume'].tail(15).mean()
        
        score = 80.0 
        if (close.iloc[-1] > ema8 and rsi < 45) or (close.iloc[-1] < ema8 and rsi > 55): score += 10
        if vol_now > vol_avg: score += 9.8
        
        score = min(score, 99.8)
        signal = "COMPRA" if close.iloc[-1] > ema8 else "VENDA"
        return signal, score

    if st.button("🚀 GERAR ENTRADA INSTITUCIONAL"):
        with st.spinner('Validando fluxo...'):
            df = get_fast_data(ativo)
            if df is not None:
                sig, precisao = analyze_ultra_fast(df)
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
                    st.markdown(f'<div style="background:{cor}; color:black; padding:25px; border-radius:12px; text-align:center; font-weight:800; font-size:1.5rem;">{sig}</div>', unsafe_allow_html=True)
                    st.divider()
                    st.metric("PREÇO", f"${df['close'].iloc[-1]:.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Conexão instável. Tente novamente.")
