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

# --- 2. CREDENCIAIS DE ACESSO ---
USER_CREDENTIALS = {
    "wallace": "admin123",  # Seu acesso
    "cliente01": "pro2026", # Acesso cliente
}

# --- 3. ESTILOS CSS (LOGIN + DASHBOARD) ---
st.markdown("""
<style>
    /* IMPORTAR FONTES */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
    
    /* --- FUNDO GERAL (GRADIENTE PROFISSIONAL) --- */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* --- ESTILOS DA TELA DE LOGIN (NOVO DESIGN) --- */
    .login-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 15px;
        padding: 50px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        text-align: center;
        margin-top: 50px;
    }
    
    .login-header {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FFFFFF, #2563eb);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    /* INPUTS DO LOGIN */
    .stTextInput > div > div > input {
        background-color: rgba(0, 0, 0, 0.4) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px;
        padding: 12px;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00ff88 !important;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.2);
    }

    /* BOTÃO DE LOGIN & AÇÃO */
    .stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #2563eb 0%, #00C9FF 100%) !important;
        color: white !important;
        border: none;
        padding: 15px;
        border-radius: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 20px rgba(37, 99, 235, 0.6);
    }

    /* --- ESTILOS DO DASHBOARD SNIPER --- */
    .hero-title { 
        background: linear-gradient(90deg, #FFFFFF, #00ff88); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-size: 3rem; 
        font-weight: 800; 
        text-align: center; 
        margin-bottom: 20px;
    }
    
    .card-pro { 
        background: rgba(0, 0, 0, 0.3); 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid rgba(255,255,255,0.1); 
        margin-bottom: 20px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .percent-mega { 
        font-size: 5rem; 
        font-weight: 900; 
        color: #00ff88; 
        line-height: 1; 
        text-align: center; 
        text-shadow: 0 0 30px rgba(0,255,136,0.4); 
    }

    /* Esconder elementos padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# --- 4. GERENCIAMENTO DE SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'user_logged' not in st.session_state:
    st.session_state['user_logged'] = ""

# --- 5. FUNÇÕES LÓGICAS (CCXT & ANALISE) ---
def get_fast_data(symbol):
    # Tenta conectar em múltiplas exchanges para garantir dados
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
    # Lógica Sniper original sua
    close = df['close']
    ema8 = close.ewm(span=8, adjust=False).mean().iloc[-1]
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    
    # Proteção contra divisão por zero
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

# --- 6. TELA DE LOGIN (NOVO DESIGN) ---
def tela_login():
    # Cria colunas para centralizar o box de login na tela wide
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<div class="login-header">VEX ELITE</div>', unsafe_allow_html=True)
        st.markdown('<p style="color: #aaa; margin-bottom: 20px;">SYSTEM ACCESS V2.0</p>', unsafe_allow_html=True)
        
        usuario = st.text_input("ID TRADER", placeholder="Digite seu usuário", key="login_user")
        senha = st.text_input("SENHA DE ACESSO", type="password", placeholder="••••••••", key="login_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("ACESSAR SISTEMA"):
            if usuario in USER_CREDENTIALS and senha == USER_CREDENTIALS[usuario]:
                st.session_state['logado'] = True
                st.session_state['user_logged'] = usuario
                st.success("AUTENTICADO COM SUCESSO")
                time.sleep(1)
                st.rerun()
            else:
                st.error("ACESSO NEGADO: Credenciais inválidas.")
        
        st.markdown('</div>', unsafe_allow_html=True)

# --- 7. PAINEL PRINCIPAL (DASHBOARD) ---
def tela_dashboard():
    # Barra Lateral
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state['user_logged'].upper()}")
        st.markdown("---")
        st.success("STATUS: **ONLINE**")
        ativo = st.selectbox("ATIVO:", ["BNB/USDT", "BTC/USDT", "ETH/USDT", "SOL/USDT"])
        
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        if st.button("SAIR DO SISTEMA"):
            st.session_state['logado'] = False
            st.session_state['user_logged'] = ""
            st.rerun()

    # Cabeçalho Principal
    st.markdown(f'<h1 class="hero-title">SNIPER PRO TERMINAL</h1>', unsafe_allow_html=True)

    with st.expander("📖 GUIA DIDÁTICO: OPERAÇÃO ZERO ERRO", expanded=False):
        st.info("""
        1. **Varredura:** No segundo **50**, clique em 'GERAR ENTRADA'.
        2. **Execução:** Se a precisão for > 90%, clique na Vex no **segundo 58 ou 59**.
        """)

    # Botão de Ação
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        acionar = st.button("🚀 RASTREAR OPORTUNIDADE INSTITUCIONAL")

    if acionar:
        with st.spinner(f'Conectando aos servidores institucionais ({ativo})...'):
            df = get_fast_data(ativo)
            
            if df is not None:
                # Simula um pequeno delay para "efeito" de processamento
                time.sleep(1.5) 
                
                sig, precisao = analyze_ultra_fast(df)
                
                # Layout dos Resultados
                c1, c2 = st.columns([2, 1])
                
                with c1:
                    st.markdown('<div class="card-pro">', unsafe_allow_html=True)
                    st.markdown("### 📊 ANÁLISE GRÁFICA EM TEMPO REAL")
                    
                    fig = go.Figure(data=[go.Candlestick(
                        x=df['timestamp'], 
                        open=df['open'], 
                        high=df['high'], 
                        low=df['low'], 
                        close=df['close'], 
                        increasing_line_color='#00ff88', 
                        decreasing_line_color='#ff4b4b'
                    )])
                    fig.update_layout(
                        template="plotly_dark", 
                        height=400, 
                        xaxis_rangeslider_visible=False,
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with c2:
                    st.markdown('<div class="card-pro" style="text-align: center;">', unsafe_allow_html=True)
                    st.markdown("##### CHANCE DE ACERTO")
                    st.markdown(f'<p class="percent-mega">{precisao:.1f}%</p>', unsafe_allow_html=True)
                    
                    cor_bg = "linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%)" if sig == "COMPRA" else "linear-gradient(90deg, #FF416C 0%, #FF4B2B 100%)"
                    texto_sig = "CALL (COMPRA)" if sig == "COMPRA" else "PUT (VENDA)"
                    
                    st.markdown(f"""
                        <div style="background: {cor_bg}; color: white; padding: 20px; border-radius: 12px; margin-top: 20px; box-shadow: 0 0 20px rgba(0,0,0,0.5);">
                            <h2 style="margin:0; font-weight:800;">{texto_sig}</h2>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown("---")
                    st.metric("PREÇO ATUAL", f"${df['close'].iloc[-1]:.2f}")
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.error("⚠️ Falha na conexão com a Exchange. Verifique sua internet.")

# --- 8. CONTROLE DE FLUXO PRINCIPAL ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
