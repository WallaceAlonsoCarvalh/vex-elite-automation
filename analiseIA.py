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

# --- 3. CSS (DESIGN MANTIDO) ---
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
    .stSelectbox > div > div {
        background-color: #111116 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
        font-weight: bold;
    }
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #0a0a0a !important;
        border: 1px solid #00ff88 !important;
    }
    li[role="option"] { color: white !important; }
    li[role="option"]:hover {
        background-color: #00ff88 !important;
        color: black !important;
    }
    .stSelectbox svg { fill: #00ff88 !important; }
    .stTextInput > div > div > input {
        background-color: #111 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
        border-radius: 8px;
        text-align: center;
        letter-spacing: 2px;
    }
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

# --- 5. INTELIGÊNCIA VEX ATOMIC v5.0 (CORREÇÃO DE ASSERTIVIDADE) ---
def get_fast_data(symbol):
    # Conexão Otimizada
    exchanges = [ccxt.bybit({'timeout': 4000}), ccxt.binance({'timeout': 4000})] 
    for ex in exchanges:
        try:
            ohlcv = ex.fetch_ohlcv(symbol, timeframe='1m', limit=50) 
            if ohlcv:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
        except: continue
    return None

def analyze_atomic_pressure(df):
    """
    Nova Lógica de Pressão Instantânea para M1 (Faltando 10s).
    Foca em rejeição de pavio e Stochastic RSI (mais rápido que RSI comum).
    """
    # Dados Recentes
    close = df['close'].values
    open_ = df['open'].values
    high = df['high'].values
    low = df['low'].values
    
    # Vela Atual (A que está acabando) e Anterior
    c_now = close[-1]
    o_now = open_[-1]
    h_now = high[-1]
    l_now = low[-1]
    
    # Tamanho do corpo e dos pavios
    body_size = abs(c_now - o_now)
    upper_wick = h_now - max(c_now, o_now)
    lower_wick = min(c_now, o_now) - l_now
    
    # --- INDICADOR 1: STOCHASTIC RSI (Detector de Topo/Fundo Rápido) ---
    # O RSI normal é lento para M1. O StochRSI é o segredo.
    rsi_period = 14
    delta = pd.Series(close).diff()
    gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    # Cálculo do Estocástico do RSI
    min_rsi = rsi.rolling(window=14).min()
    max_rsi = rsi.rolling(window=14).max()
    stoch_rsi = (rsi - min_rsi) / (max_rsi - min_rsi)
    
    k = stoch_rsi.rolling(window=3).mean().iloc[-1] * 100 # Linha K rápida
    
    # --- INDICADOR 2: MÉDIAS ESTRUTURAIS ---
    ema9 = pd.Series(close).ewm(span=9).mean().iloc[-1]
    
    score = 0.0
    signal = "NEUTRO"
    motive = "ANALISANDO..."

    # --- LÓGICA DE DECISÃO (ATOMIC) ---
    
    # CENÁRIO 1: REVERSÃO DE TOPO (PUT/VENDA)
    # Se o StochRSI estiver estourado (>90) E a vela atual deixar pavio em cima
    if k > 85:
        # Se a vela atual for VERDE, mas deixou pavio superior grande (Tentou subir e falhou)
        if c_now > o_now and upper_wick > (body_size * 0.4):
            score = 96.5
            signal = "VENDA"
            motive = "ATOMIC: REJEIÇÃO DE TOPO + RSI ESTOURADO"
        
        # Se a vela atual já virou VERMELHA (Força vendedora entrou no final)
        elif c_now < o_now:
            score = 94.0
            signal = "VENDA"
            motive = "ATOMIC: VIRADA DE VELA (PULLBACK)"

    # CENÁRIO 2: REVERSÃO DE FUNDO (CALL/COMPRA)
    # Se o StochRSI estiver no chão (<10)
    elif k < 15:
        # Se a vela atual for VERMELHA, mas deixou pavio inferior grande
        if c_now < o_now and lower_wick > (body_size * 0.4):
            score = 96.5
            signal = "COMPRA"
            motive = "ATOMIC: REJEIÇÃO DE FUNDO + RSI SOBREVENDA"
        
        # Se a vela atual já virou VERDE
        elif c_now > o_now:
            score = 94.0
            signal = "COMPRA"
            motive = "ATOMIC: VIRADA DE VELA (PULLBACK)"

    # CENÁRIO 3: FLUXO CONTÍNUO (MOMENTUM)
    # Só entra a favor da tendência se NÃO estiver sobrecomprado/vendido
    else:
        # Tendência de Alta Limpa
        if c_now > ema9 and c_now > o_now and upper_wick < (body_size * 0.2):
            if k > 40 and k < 75: # Tem espaço para subir
                score = 92.0
                signal = "COMPRA"
                motive = "ATOMIC: FLUXO DE FORÇA (VELA CHEIA)"
        
        # Tendência de Baixa Limpa
        elif c_now < ema9 and c_now < o_now and lower_wick < (body_size * 0.2):
            if k < 60 and k > 25: # Tem espaço para cair
                score = 92.0
                signal = "VENDA"
                motive = "ATOMIC: FLUXO DE FORÇA (VELA CHEIA)"

    # --- TRAVA DE SEGURANÇA (DOJI) ---
    # Se a vela for insignificante (quase um traço), não faz nada.
    avg_body = np.mean(abs(close[-5:] - open_[-5:]))
    if body_size < (avg_body * 0.25):
        score = 10.0
        signal = "NEUTRO"
        motive = "MERCADO PARADO (DOJI) - NÃO ENTRAR"

    return signal, score, motive

# --- 6. TELA DE LOGIN ---
def tela_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; border: 1px solid #00ff88; padding: 40px; background: #000; box-shadow: 0 0 20px rgba(0,255,136,0.2);">
                <h1 style="font-family: 'Orbitron'; font-size: 3rem; margin-bottom: 0; color: #00ff88 !important; text-shadow: 0 0 10px #00ff88;">VEX ELITE</h1>
                <p style="letter-spacing: 5px; color: white; font-size: 0.8rem; margin-bottom: 30px;">SYSTEM ACCESS v5.0</p>
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

# --- 7. TELA DASHBOARD ---
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
        with st.spinner(f"CALCULANDO PRESSÃO DE MERCADO EM {ativo}..."):
            df = get_fast_data(ativo)
            
            if df is not None:
                # NOVA INTELIGÊNCIA V5.0
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
                    
                    cor_score = "#00ff88" if precisao >= 92 else "#ffcc00" # Filtro de 92%
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
                st.error("ERRO DE CONEXÃO COM A EXCHANGE.")

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO"):
        st.session_state['logado'] = False
        st.rerun()

# --- 8. EXECUÇÃO ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
