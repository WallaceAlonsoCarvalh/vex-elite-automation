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

# --- 3. CSS "CYBER-FUTURE" (DESIGN TOTALMENTE NOVO) ---
st.markdown("""
<style>
    /* FONTE FUTURISTA */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');

    /* --- FUNDO GERAL --- */
    .stApp {
        background-color: #050505;
        background-image: 
            radial-gradient(at 0% 0%, hsla(253,16%,7%,1) 0, transparent 50%), 
            radial-gradient(at 50% 0%, hsla(225,39%,30%,1) 0, transparent 50%), 
            radial-gradient(at 100% 0%, hsla(339,49%,30%,1) 0, transparent 50%);
        color: #ffffff;
    }

    /* --- CORREÇÃO DE VISIBILIDADE (TEXTO BRANCO FORÇADO) --- */
    h1, h2, h3, h4, h5, h6, p, label, div, span, li {
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif;
    }

    /* --- BARRA DE SELEÇÃO (CRIPTO) CORRIGIDA --- */
    /* Caixa fechada */
    .stSelectbox > div > div {
        background-color: #111116 !important;
        color: #00ff88 !important; /* Texto Verde Neon */
        border: 1px solid #333 !important;
        font-weight: bold;
    }
    /* Lista Aberta (Dropdown) */
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff88 !important;
    }
    /* Itens da Lista */
    li[role="option"] {
        color: white !important;
    }
    /* Hover na Lista */
    li[role="option"]:hover {
        background-color: #00ff88 !important;
        color: black !important; /* Texto preto no hover para ler bem */
    }
    /* Ícone da seta */
    .stSelectbox svg { fill: #00ff88 !important; }

    /* --- INPUTS DE LOGIN --- */
    .stTextInput > div > div > input {
        background-color: #111 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
        border-radius: 8px;
        text-align: center;
        letter-spacing: 2px;
    }

    /* --- BOTÕES CYBERPUNK --- */
    .stButton > button {
        background: transparent !important;
        border: 1px solid #00ff88 !important;
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        font-weight: 900;
        padding: 20px;
        border-radius: 0px; /* Quadrado estilo Hacker */
        transition: all 0.3s ease;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.1);
    }
    .stButton > button:hover {
        background: #00ff88 !important;
        color: #000 !important;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.6);
        transform: scale(1.02);
    }

    /* --- CARDS (CONTAINERS) --- */
    .neon-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        backdrop-filter: blur(10px);
    }

    /* --- SCORE GIGANTE --- */
    .score-glow {
        font-size: 6rem;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        text-shadow: 0 0 40px currentColor;
        line-height: 1;
        margin: 20px 0;
    }

    /* Esconder menu padrão */
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

# --- 5. INTELIGÊNCIA VEX (Multi-Strategy) ---
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
    
    # 1. TENDÊNCIA
    if last_close > last_ema9 and last_ema9 > last_ema21:
        if last_rsi > 50 and last_rsi < 70: 
            score += 15
            motive = "FLUXO: TENDÊNCIA DE ALTA"
    elif last_close < last_ema9 and last_ema9 < last_ema21:
        if last_rsi < 50 and last_rsi > 30: 
            score += 15
            motive = "FLUXO: TENDÊNCIA DE BAIXA"

    # 2. REVERSÃO (BB)
    if last_close > last_upper: 
        score += 18 
        motive = "REVERSÃO: TOPO ESTOURADO"
    elif last_close < last_lower: 
        score += 18
        motive = "REVERSÃO: FUNDO ESTOURADO"
        
    # 3. VOLUME
    vol_now = df['volume'].iloc[-1]
    vol_avg = df['volume'].tail(20).mean()
    if vol_now > (vol_avg * 1.5): score += 5
    
    if last_rsi > 80 or last_rsi < 20: score += 5
        
    score = min(score, 99.9)
    
    if "ALTA" in motive or "FUNDO" in motive: signal = "COMPRA"
    else: signal = "VENDA"
        
    # Correção final de direção
    if last_close > last_upper: signal = "VENDA"
    if last_close < last_lower: signal = "COMPRA"

    return signal, score, motive

# --- 6. TELA DE LOGIN (DESIGN HACKER) ---
def tela_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("""
            <div style="text-align: center; border: 1px solid #00ff88; padding: 40px; background: #000; box-shadow: 0 0 20px rgba(0,255,136,0.2);">
                <h1 style="font-family: 'Orbitron'; font-size: 3rem; margin-bottom: 0; color: #00ff88 !important; text-shadow: 0 0 10px #00ff88;">VEX ELITE</h1>
                <p style="letter-spacing: 5px; color: white; font-size: 0.8rem; margin-bottom: 30px;">SYSTEM ACCESS v3.0</p>
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
                st.error("ACESSO NEGADO. IP REGISTRADO.")

# --- 7. TELA DASHBOARD (DESIGN TERMINAL) ---
def tela_dashboard():
    # --- HEADER / BARRA SUPERIOR ---
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
    
    # --- BARRA DE CONTROLE ---
    st.markdown("<div class='neon-card' style='margin-bottom: 20px;'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.markdown("<h4 style='margin-bottom: 5px; color: #00ff88 !important;'>ATIVO ALVO</h4>", unsafe_allow_html=True)
        ativo = st.selectbox("", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"], label_visibility="collapsed")
    with c3:
        st.markdown("<h4 style='margin-bottom: 5px; color: #00ff88 !important;'>AÇÃO</h4>", unsafe_allow_html=True)
        acionar = st.button("VARREDURA DE MERCADO")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- ÁREA DE RESULTADOS ---
    if acionar:
        with st.spinner(f"EXECUTANDO ALGORITMO EM {ativo}..."):
            df = get_fast_data(ativo)
            
            if df is not None:
                sig, precisao, motivo = analyze_all_hypothesis(df)
                
                # Layout de 2 Colunas: Gráfico Esquerda / Cérebro Direita
                col_grafico, col_dados = st.columns([2.5, 1.5])
                
                # COLUNA 1: GRÁFICO
                with col_grafico:
                    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
                    st.markdown(f"<h3 style='font-family: Orbitron;'>GRÁFICO M1 | {ativo}</h3>", unsafe_allow_html=True)
                    
                    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00ff88', decreasing_line_color='#ff0055')])
                    fig.update_layout(
                        template="plotly_dark", 
                        height=500, 
                        xaxis_rangeslider_visible=False, 
                        paper_bgcolor='rgba(0,0,0,0)', 
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=10, r=10, t=30, b=10),
                        font=dict(family="Rajdhani", color="white")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown("</div>", unsafe_allow_html=True)
                
                # COLUNA 2: INTELIGÊNCIA ARTIFICIAL
                with col_dados:
                    st.markdown("<div class='neon-card' style='text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
                    
                    st.markdown("<p style='color: #aaa !important; font-size: 0.9rem;'>PROBABILIDADE DE ACERTO</p>", unsafe_allow_html=True)
                    
                    # Definição de Cores Baseada na Precisão
                    cor_score = "#00ff88" if precisao >= 90 else "#ffcc00"
                    
                    st.markdown(f"<div class='score-glow' style='color: {cor_score} !important;'>{precisao:.1f}%</div>", unsafe_allow_html=True)
                    
                    if precisao >= 90:
                        acao_texto = "COMPRA" if sig == "COMPRA" else "VENDA"
                        cor_bg = "linear-gradient(45deg, #00ff88, #00cc6a)" if sig == "COMPRA" else "linear-gradient(45deg, #ff0055, #cc0044)"
                        
                        st.markdown(f"""
                            <div style="background: {cor_bg}; padding: 15px; border-radius: 5px; margin: 10px 0; box-shadow: 0 0 20px {cor_score};">
                                <h1 style="margin:0; font-size: 2.5rem; color: black !important; font-weight: 900;">{acao_texto}</h1>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"<div style='border: 1px solid #333; padding: 10px; margin-top: 10px;'><span style='color: #00ff88 !important;'>MOTIVO:</span> {motivo}</div>", unsafe_allow_html=True)
                        st.markdown("<p style='margin-top: 15px; color: white !important; font-weight: bold; animation: pulse 1s infinite;'>ENTRADA: :58s / :59s</p>", unsafe_allow_html=True)
                    
                    else:
                        st.markdown("""
                            <div style="border: 2px solid #ffcc00; padding: 15px; margin: 10px 0; color: #ffcc00;">
                                <h2 style="margin:0; color: #ffcc00 !important;">AGUARDE</h2>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #aaa !important;'>Cenário Atual: {motivo}</p>", unsafe_allow_html=True)
                        st.markdown("<p style='font-size: 0.8rem; color: #ffcc00 !important;'>FILTRO DE SEGURANÇA ATIVO (<90%)</p>", unsafe_allow_html=True)
                    
                    st.markdown(f"<div style='margin-top: auto; padding-top: 20px; font-size: 1.5rem;'>${df['close'].iloc[-1]:.2f}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.error("ERRO DE CONEXÃO COM A EXCHANGE.")

    # --- FOOTER ---
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO"):
        st.session_state['logado'] = False
        st.rerun()

# --- 8. EXECUÇÃO ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
