import streamlit as st
import pandas as pd
import ccxt
import time
import numpy as np
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO INICIAL ---
st.set_page_config(
    page_title="VEX ELITE | SYSTEM",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CREDENCIAIS ---
USER_CREDENTIALS = {
    "wallace": "admin123",  
    "cliente01": "pro2026", 
}

# --- 3. ESTILOS CSS (DESIGN PREMIUM V2) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Plus+Jakarta+Sans:wght@400;700&display=swap');
    
    /* --- FUNDO GERAL --- */
    .stApp {
        background: radial-gradient(circle at center, #1a1a2e 0%, #0f0c29 100%);
        background-attachment: fixed;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* --- TELA DE LOGIN APRIMORADA --- */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 50px;
    }
    
    .login-card {
        background: rgba(16, 16, 24, 0.8);
        backdrop-filter: blur(25px);
        -webkit-backdrop-filter: blur(25px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-top: 1px solid rgba(0, 255, 136, 0.3); /* Detalhe verde no topo */
        border-radius: 24px;
        padding: 50px 40px;
        width: 100%;
        max-width: 420px;
        box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6), 0 0 30px rgba(0, 255, 136, 0.05);
        text-align: center;
        position: relative;
    }

    .login-icon {
        font-size: 3rem;
        margin-bottom: 10px;
        background: linear-gradient(135deg, #00C9FF 0%, #92FE9D 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .login-title {
        font-family: 'Rajdhani', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
        letter-spacing: 4px;
        margin-bottom: 5px;
        text-transform: uppercase;
    }

    .login-subtitle {
        color: #6c757d;
        font-size: 0.9rem;
        margin-bottom: 30px;
        letter-spacing: 1px;
    }

    /* --- INPUTS ESTILIZADOS --- */
    .stTextInput > div > div > input {
        background-color: #0b0b10 !important;
        color: #e0e0e0 !important;
        border: 1px solid #333 !important;
        border-radius: 12px !important;
        padding: 15px !important;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.15) !important;
        background-color: #111 !important;
    }

    /* --- BOTÃO DE LOGIN --- */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #00f260 0%, #0575E6 100%) !important;
        color: white !important;
        border: none;
        padding: 16px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        margin-top: 15px;
        transition: all 0.4s ease;
        box-shadow: 0 4px 15px rgba(5, 117, 230, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 242, 96, 0.5);
    }

    /* --- CORREÇÕES GERAIS --- */
    h1, h2, h3, p, label { color: white !important; }
    
    /* Dropdown Escuro (Correção anterior mantida) */
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #0f0c29 !important;
        border: 1px solid #444 !important;
    }
    li[role="option"]:hover { background-color: #2563eb !important; }
    .stSelectbox > div > div {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: white !important;
        border: 1px solid #555 !important;
    }
    .stSelectbox svg { fill: white !important; }

    /* Esconder menu padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

</style>
""", unsafe_allow_html=True)

# --- 4. ESTADO DA SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'user_logged' not in st.session_state:
    st.session_state['user_logged'] = ""

# --- 5. FUNÇÕES DE DADOS (CÉREBRO INTELIGENTE MANTIDO) ---
def get_fast_data(symbol):
    exchanges = [ccxt.bybit({'timeout': 3000}), ccxt.kucoin({'timeout': 3000})] 
    for ex in exchanges:
        try:
            ohlcv = ex.fetch_ohlcv(symbol, timeframe='1m', limit=100) 
            if ohlcv:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
        except: continue
    return None

def analyze_all_hypothesis(df):
    # Lógica VEX ELITE HYPER-THREADING (Não alterada)
    close = df['close']
    ema9 = close.ewm(span=9, adjust=False).mean()
    ema21 = close.ewm(span=21, adjust=False).mean()
    
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    sma20 = close.rolling(window=20).mean()
    std20 = close.rolling(window=20).std()
    upper_bb = sma20 + (std20 * 2)
    lower_bb = sma20 - (std20 * 2)
    
    last_close = close.iloc[-1]
    last_ema9 = ema9.iloc[-1]
    last_ema21 = ema21.iloc[-1]
    last_rsi = rsi.iloc[-1]
    last_upper = upper_bb.iloc[-1]
    last_lower = lower_bb.iloc[-1]
    
    score = 75.0 
    motive = "ANÁLISE NEUTRA"
    
    if last_close > last_ema9 and last_ema9 > last_ema21:
        if last_rsi > 50 and last_rsi < 70: 
            score += 15
            motive = "FLUXO DE ALTA (TENDÊNCIA)"
    elif last_close < last_ema9 and last_ema9 < last_ema21:
        if last_rsi < 50 and last_rsi > 30: 
            score += 15
            motive = "FLUXO DE BAIXA (TENDÊNCIA)"

    if last_close > last_upper: 
        score += 18 
        motive = "REVERSÃO DE TOPO (BB)"
    elif last_close < last_lower: 
        score += 18
        motive = "REVERSÃO DE FUNDO (BB)"
        
    vol_now = df['volume'].iloc[-1]
    vol_avg = df['volume'].tail(20).mean()
    if vol_now > (vol_avg * 1.5): score += 5
    
    if last_rsi > 80 or last_rsi < 20: score += 5
        
    score = min(score, 99.9)
    
    if "ALTA" in motive or "FUNDO" in motive: signal = "COMPRA"
    else: signal = "VENDA"
        
    if last_close > last_upper: signal = "VENDA"
    if last_close < last_lower: signal = "COMPRA"

    return signal, score, motive

# --- 6. TELA DE LOGIN (NOVO DESIGN) ---
def tela_login():
    # Usamos colunas para criar um "Grid" e centralizar o cartão
    col_vazia_esq, col_centro, col_vazia_dir = st.columns([1, 1.5, 1])
    
    with col_centro:
        # Início do Cartão CSS
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        # Ícone e Título
        st.markdown('<div class="login-icon">🔒</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">VEX ELITE</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">SYSTEM ACCESS | PRIVATE SERVER</div>', unsafe_allow_html=True)
        
        # Inputs (Sem labels visíveis para visual limpo)
        usuario = st.text_input("User", placeholder="ID DE USUÁRIO", label_visibility="collapsed")
        # Espaçamento manual
        st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)
        senha = st.text_input("Pass", type="password", placeholder="SENHA DE ACESSO", label_visibility="collapsed")
        
        # Botão
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        if st.button("AUTENTICAR E ENTRAR"):
            if usuario in USER_CREDENTIALS and senha == USER_CREDENTIALS[usuario]:
                st.session_state['logado'] = True
                st.session_state['user_logged'] = usuario
                st.rerun()
            else:
                st.markdown('<p style="color: #ff4b4b !important; margin-top: 10px;">⛔ Credenciais inválidas.</p>', unsafe_allow_html=True)
        
        # Rodapé do cartão
        st.markdown('<div style="margin-top: 30px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; font-size: 0.7rem; color: #555;">VEX TECHNOLOGIES © 2026</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. TELA PRINCIPAL (DASHBOARD) ---
def tela_dashboard():
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="background: linear-gradient(90deg, #FFFFFF, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 800; display: inline-block;">
                SNIPER PRO TERMINAL
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    st.info("""
    ⚠️ **INSTRUÇÃO DE OURO:** Analise faltando **10 SEGUNDOS** (xx:50s). Opere apenas acima de **90%**.
    """)

    st.markdown("---")
    
    c_sel1, c_sel2, c_sel3 = st.columns([1, 2, 1])
    with c_sel2:
        st.markdown("### SELECIONE O ATIVO:")
        ativo = st.selectbox("Selecione:", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"], label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)

    c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
    with c_btn2:
        acionar = st.button(f"🚀 ANALISAR {ativo} AGORA")

    if acionar:
        with st.spinner(f"Processando todas as hipóteses em {ativo}..."):
            df = get_fast_data(ativo)
            
            if df is not None:
                sig, precisao, motivo = analyze_all_hypothesis(df)
                
                cr1, cr2 = st.columns([2, 1])
                with cr1:
                    st.markdown('<div style="background: rgba(0,0,0,0.4); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);"><h3 style="margin-top:0;">📉 GRÁFICO EM TEMPO REAL</h3>', unsafe_allow_html=True)
                    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b')])
                    fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with cr2:
                    st.markdown('<div style="background: rgba(0,0,0,0.4); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); text-align: center; height: 100%;">', unsafe_allow_html=True)
                    
                    if precisao >= 90:
                        st.markdown("<h3>✅ ENTRADA CONFIRMADA</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h1 style='font-size: 5rem; color: #00ff88 !important; margin:0; line-height: 1;'>{precisao:.1f}%</h1>", unsafe_allow_html=True)
                        cor_sinal = "#00ff88" if sig == "COMPRA" else "#ff4b4b"
                        texto_sinal = "CALL (COMPRA)" if sig == "COMPRA" else "PUT (VENDA)"
                        st.markdown(f"<div style='background: {cor_sinal}; padding: 20px; border-radius: 10px; margin-top: 20px; box-shadow: 0 0 15px {cor_sinal}80;'><h2 style='color: black !important; margin:0; font-weight: 800;'>{texto_sinal}</h2></div>", unsafe_allow_html=True)
                        st.markdown(f"<p style='margin-top:10px; color: #aaa !important; font-size: 0.8rem;'>MOTIVO: {motivo}</p>", unsafe_allow_html=True)
                        st.markdown("<p style='margin-top:5px; color: #00ff88 !important; font-weight: bold;'>ENTRE NO SEGUNDO 58/59</p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<h3>⚠️ AGUARDE</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h1 style='font-size: 5rem; color: #ffcc00 !important; margin:0; line-height: 1;'>{precisao:.1f}%</h1>", unsafe_allow_html=True)
                        st.markdown(f"<div style='background: #333; padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #ffcc00;'><h4 style='color: #ffcc00 !important; margin:0;'>PRECISÃO BAIXA</h4><p style='font-size: 0.8rem; margin-top: 5px;'>Cenário: {motivo}</p></div>", unsafe_allow_html=True)

                    st.markdown(f"<br><p style='font-size: 1.2rem;'>Preço: <b>${df['close'].iloc[-1]:.2f}</b></p>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Erro ao obter dados. Verifique sua conexão.")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("SAIR DO SISTEMA"):
        st.session_state['logado'] = False
        st.rerun()

# --- 8. EXECUÇÃO ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
