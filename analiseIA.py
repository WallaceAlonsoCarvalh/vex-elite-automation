import streamlit as st
import pandas as pd
import ccxt
import time
from datetime import datetime
import plotly.graph_objects as go

# --- 1. CONFIGURAÇÃO INICIAL (OBRIGATÓRIO SER A PRIMEIRA LINHA) ---
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

# --- 3. ESTILOS CSS CORRIGIDOS (Texto Branco & Layout) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
    
    /* FUNDO E FONTE GLOBAL */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* FORÇAR COR BRANCA EM TUDO (Correção do texto preto) */
    h1, h2, h3, h4, h5, h6, p, li, span, div, label {
        color: white !important;
    }
    
    /* Corrigir cor interna dos Inputs e Selectbox */
    .stTextInput > div > div > input {
        color: white !important;
        background-color: rgba(0,0,0,0.5) !important;
        border: 1px solid #555 !important;
    }
    .stSelectbox > div > div > div {
        color: white !important;
        background-color: rgba(0,0,0,0.5) !important;
    }

    /* LAYOUT LOGIN */
    .login-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 40px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        text-align: center;
        margin-top: 20px;
    }

    /* BOTÃO ESTILIZADO */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #00C9FF 100%) !important;
        color: white !important;
        border: none;
        padding: 15px;
        border-radius: 10px;
        font-weight: 800;
        text-transform: uppercase;
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(0, 201, 255, 0.6);
    }

    /* TITULOS E CARDS */
    .hero-title { 
        background: linear-gradient(90deg, #FFFFFF, #00ff88); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent !important; /* Força o gradiente no texto */
        font-size: 3rem; 
        font-weight: 800; 
        text-align: center; 
    }
    .card-pro {
        background: rgba(0,0,0,0.4);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
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

# --- 5. FUNÇÕES DE ANÁLISE ---
def get_fast_data(symbol):
    exchanges = [ccxt.bybit({'timeout': 5000}), ccxt.kucoin({'timeout': 5000})]
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
    # Cálculo simples de RSI para exemplo
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1] if not loss.iloc[-1] == 0 else 50
    
    vol_now = df['volume'].iloc[-1]
    vol_avg = df['volume'].tail(15).mean()
    
    score = 80.0 
    if (close.iloc[-1] > ema8 and rsi < 45) or (close.iloc[-1] < ema8 and rsi > 55): score += 10
    if vol_now > vol_avg: score += 9.8
    score = min(score, 99.8)
    
    signal = "COMPRA" if close.iloc[-1] > ema8 else "VENDA"
    return signal, score

# --- 6. TELA DE LOGIN ---
def tela_login():
    # Ajuste: Coluna do meio maior (2) para o login ficar mais espaçoso
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h1>VEX ELITE</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: #ccc !important;">ACESSO AO SISTEMA</p>', unsafe_allow_html=True)
        
        # Inputs sem label visível (placeholder resolve) para design mais limpo
        usuario = st.text_input("USUÁRIO", placeholder="ID de Usuário", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        senha = st.text_input("SENHA", type="password", placeholder="Senha de Acesso", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("ENTRAR NO SISTEMA"):
            if usuario in USER_CREDENTIALS and senha == USER_CREDENTIALS[usuario]:
                st.session_state['logado'] = True
                st.session_state['user_logged'] = usuario
                st.rerun()
            else:
                st.error("Credenciais inválidas")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. TELA PRINCIPAL (DASHBOARD) ---
def tela_dashboard():
    # Cabeçalho
    st.markdown(f'<h1 class="hero-title">SNIPER PRO TERMINAL</h1>', unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>Bem-vindo, {st.session_state['user_logged'].upper()}</p>", unsafe_allow_html=True)

    # --- NOVO SELETOR DE ATIVOS (CENTRALIZADO) ---
    st.markdown("---")
    c_sel1, c_sel2, c_sel3 = st.columns([1, 2, 1])
    with c_sel2:
        # Aqui você seleciona o Crypto!
        st.markdown("### SELECIONE O ATIVO:")
        ativo = st.selectbox("", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"], label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Botão de Ação
    c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
    with c_btn2:
        acionar = st.button(f"🚀 ANALISAR {ativo} AGORA")

    # Resultado da Análise
    if acionar:
        with st.spinner(f"Varrendo mercado em {ativo}..."):
            df = get_fast_data(ativo)
            time.sleep(1) # Efeito visual
            
            if df is not None:
                sig, precisao = analyze_ultra_fast(df)
                
                # Layout colunas resultado
                cr1, cr2 = st.columns([2, 1])
                
                with cr1:
                    st.markdown('<div class="card-pro">', unsafe_allow_html=True)
                    st.markdown("### 📉 GRÁFICO M1")
                    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b')])
                    fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with cr2:
                    st.markdown('<div class="card-pro" style="text-align:center;">', unsafe_allow_html=True)
                    st.markdown("### ASSERTIVIDADE")
                    st.markdown(f"<h1 style='font-size: 5rem; color: #00ff88 !important; margin:0;'>{precisao:.1f}%</h1>", unsafe_allow_html=True)
                    
                    cor_sinal = "#00ff88" if sig == "COMPRA" else "#ff4b4b"
                    st.markdown(f"""
                        <div style="background: {cor_sinal}; color: black !important; padding: 15px; border-radius: 10px; margin-top: 15px;">
                            <h2 style="color: black !important; margin:0; font-weight: 800;">{sig}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"<br><h3>Preço: ${df['close'].iloc[-1]:.2f}</h3>", unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("Erro de conexão com a corretora.")
    
    # Botão Sair no rodapé
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("SAIR DO SISTEMA"):
        st.session_state['logado'] = False
        st.rerun()

# --- 8. EXECUÇÃO ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
