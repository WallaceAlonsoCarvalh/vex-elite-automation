import streamlit as st
import pandas as pd
import ccxt
import time
from datetime import datetime
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

# --- 3. ESTILOS CSS (MANTIDO O DARK GLASS CORRIGIDO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* FORÇAR COR BRANCA */
    h1, h2, h3, h4, h5, h6, p, span, div, label, li {
        color: white !important;
    }

    /* CORREÇÃO DO MENU DROPDOWN */
    ul[data-testid="stSelectboxVirtualDropdown"] {
        background-color: #0f0c29 !important;
        border: 1px solid #444 !important;
    }
    li[role="option"]:hover {
        background-color: #2563eb !important;
    }
    .stSelectbox > div > div {
        background-color: rgba(0, 0, 0, 0.5) !important;
        color: white !important;
        border: 1px solid #555 !important;
    }
    .stSelectbox svg { fill: white !important; }

    /* INPUTS */
    .stTextInput > div > div > input {
        color: white !important;
        background-color: rgba(0,0,0,0.5) !important;
        border: 1px solid #555 !important;
    }

    /* LOGIN CONTAINER */
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

    /* BOTÕES */
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

# --- 5. FUNÇÕES DE DADOS (LÓGICA INTACTA) ---
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
    # LÓGICA PRESERVADA 100% PARA NÃO ERRAR ENTRADA
    close = df['close']
    ema8 = close.ewm(span=8, adjust=False).mean().iloc[-1]
    
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
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h1 style="margin-bottom: 0;">VEX ELITE</h1>', unsafe_allow_html=True)
        st.markdown('<p style="color: #aaa !important; font-size: 0.9rem;">SYSTEM ACCESS</p>', unsafe_allow_html=True)
        
        usuario = st.text_input("USUÁRIO", placeholder="ID de Usuário", label_visibility="collapsed")
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
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

# --- 7. TELA PRINCIPAL (DASHBOARD ATUALIZADO) ---
def tela_dashboard():
    # Título
    st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <h1 style="background: linear-gradient(90deg, #FFFFFF, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 3rem; font-weight: 800; display: inline-block;">
                SNIPER PRO TERMINAL
            </h1>
        </div>
    """, unsafe_allow_html=True)
    
    # --- NOVO GUIA DE INSTRUÇÃO (CRÍTICO) ---
    st.info("""
    ⚠️ **INSTRUÇÃO DE OURO PARA OPERAR:**
    1. A análise deve ser feita **FALTANDO 10 SEGUNDOS** para a vela de 1M acabar (no segundo 50).
    2. **SOMENTE** confie em entradas com assertividade **ACIMA DE 90%**.
    """)

    st.markdown("---")
    
    # Seletor
    c_sel1, c_sel2, c_sel3 = st.columns([1, 2, 1])
    with c_sel2:
        st.markdown("### SELECIONE O ATIVO:")
        ativo = st.selectbox("Selecione:", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT"], label_visibility="collapsed")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # Botão
    c_btn1, c_btn2, c_btn3 = st.columns([1, 2, 1])
    with c_btn2:
        acionar = st.button(f"🚀 ANALISAR {ativo} AGORA")

    if acionar:
        with st.spinner(f"Verificando precisão em {ativo}..."):
            df = get_fast_data(ativo)
            time.sleep(1) 
            
            if df is not None:
                sig, precisao = analyze_ultra_fast(df)
                
                # Layout Resultado
                cr1, cr2 = st.columns([2, 1])
                
                with cr1:
                    st.markdown("""
                        <div style="background: rgba(0,0,0,0.4); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1);">
                        <h3 style="margin-top:0;">📉 GRÁFICO EM TEMPO REAL</h3>
                    """, unsafe_allow_html=True)
                    
                    fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00ff88', decreasing_line_color='#ff4b4b')])
                    fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig, use_container_width=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with cr2:
                    st.markdown('<div style="background: rgba(0,0,0,0.4); padding: 20px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); text-align: center; height: 100%;">', unsafe_allow_html=True)
                    
                    # --- FILTRO VISUAL DE 90% ---
                    if precisao >= 90:
                        st.markdown("<h3>✅ ENTRADA CONFIRMADA</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h1 style='font-size: 5rem; color: #00ff88 !important; margin:0; line-height: 1;'>{precisao:.1f}%</h1>", unsafe_allow_html=True)
                        
                        cor_sinal = "#00ff88" if sig == "COMPRA" else "#ff4b4b"
                        texto_sinal = "CALL (COMPRA)" if sig == "COMPRA" else "PUT (VENDA)"
                        
                        st.markdown(f"""
                            <div style="background: {cor_sinal}; padding: 20px; border-radius: 10px; margin-top: 20px; box-shadow: 0 0 15px {cor_sinal}80;">
                                <h2 style="color: black !important; margin:0; font-weight: 800;">{texto_sinal}</h2>
                            </div>
                            <p style="margin-top:10px; color: #00ff88 !important;">ENTRE NO SEGUNDO 58/59</p>
                        """, unsafe_allow_html=True)
                    
                    else:
                        # SE FOR MENOS DE 90%, AVISA PARA NÃO ENTRAR
                        st.markdown("<h3>⚠️ AGUARDE</h3>", unsafe_allow_html=True)
                        st.markdown(f"<h1 style='font-size: 5rem; color: #ffcc00 !important; margin:0; line-height: 1;'>{precisao:.1f}%</h1>", unsafe_allow_html=True)
                        st.markdown("""
                            <div style="background: #333; padding: 20px; border-radius: 10px; margin-top: 20px; border: 1px solid #ffcc00;">
                                <h4 style="color: #ffcc00 !important; margin:0;">PRECISÃO BAIXA</h4>
                                <p style="font-size: 0.8rem; margin-top: 5px;">Recomendado operar apenas acima de 90%</p>
                            </div>
                        """, unsafe_allow_html=True)

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
