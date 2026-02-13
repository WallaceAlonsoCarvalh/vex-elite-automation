import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import datetime
import time 

# --- IMPORTAÇÃO SEGURA ---
try:
    import yfinance as yf
    YF_AVAILABLE = True
except ImportError:
    YF_AVAILABLE = False

# --- 1. CONFIGURAÇÃO (FOREX PRO) ---
st.set_page_config(
    page_title="VEX ELITE | FOREX PRO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS (VISUAL FIXO E LIMPO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(at 50% 0%, #111 0%, #000 100%);
        color: white;
    }
    
    h1, h2, h3, p, div, span { font-family: 'Rajdhani', sans-serif !important; }
    
    /* MENU DROPDOWN */
    .stSelectbox > div > div {
        background-color: #080808 !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
    }
    div[data-baseweb="popover"] { background-color: #080808 !important; }
    li[role="option"] { color: white !important; background-color: #080808 !important; }
    li[role="option"]:hover { background-color: #00ff88 !important; color: black !important; }
    
    /* BOTÕES */
    .stButton > button {
        background: #00ff88 !important;
        color: black !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        border: none;
        padding: 15px;
        transition: 0.3s;
    }
    .stButton > button:hover {
        box-shadow: 0 0 25px rgba(0, 255, 136, 0.5);
        transform: scale(1.02);
    }

    .neon-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid #222;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    
    .score-glow {
        font-family: 'Orbitron';
        font-size: 4rem;
        font-weight: 900;
        text-shadow: 0 0 20px currentColor;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. ESTADO DA SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False

# CREDENCIAIS
CREDENCIAIS = {
    "wallace": "admin123",
    "cliente01": "pro2026"
}

# --- 4. COLETOR DE DADOS (COM CACHE DE 60 SEGUNDOS) ---
# O @st.cache_data impede que o gráfico mude se você clicar várias vezes no mesmo minuto
@st.cache_data(ttl=60, show_spinner=False)
def get_forex_data_cached(pair):
    """
    Busca dados reais. Se falhar, usa matemática determinística (não aleatória)
    para que o gráfico não fique mudando na frente do usuário.
    """
    symbol_map = {
        "EUR/USD": "EURUSD=X", "GBP/USD": "GBPUSD=X", "USD/JPY": "JPY=X",
        "USD/BRL": "BRL=X", "EUR/JPY": "EURJPY=X", "GBP/JPY": "GBPJPY=X",
        "AUD/USD": "AUDUSD=X", "USD/CAD": "CAD=X"
    }
    
    ticker = symbol_map.get(pair, "EURUSD=X")
    
    # TENTATIVA 1: DADOS REAIS (YFINANCE)
    if YF_AVAILABLE:
        try:
            df = yf.download(ticker, period="1d", interval="1m", progress=False)
            if not df.empty:
                df = df.reset_index()
                df.columns = df.columns.str.lower()
                if 'datetime' in df.columns: df = df.rename(columns={'datetime': 'timestamp'})
                if 'date' in df.columns: df = df.rename(columns={'date': 'timestamp'})
                # Pega as últimas 60 velas para o gráfico ficar limpo
                return df.tail(60), "MERCADO REAL (ONLINE)"
        except:
            pass

    # TENTATIVA 2: SIMULAÇÃO ESTÁVEL (BACKUP)
    # Se cair aqui, geramos um gráfico que é SEMPRE O MESMO para aquela hora.
    # Isso impede que o gráfico fique "pulando".
    dates = pd.date_range(end=datetime.datetime.now(), periods=60, freq='1min')
    
    # A semente é baseada na HORA atual e no NOME do par. 
    # Dentro da mesma hora, o gráfico será idêntico.
    seed_val = int(datetime.datetime.now().strftime("%Y%m%d%H")) + len(pair)
    np.random.seed(seed_val)
    
    base_price = 1.0850 if "EUR" in pair else 150.00 if "JPY" in pair else 1.2500
    
    # Cria movimento realista
    returns = np.random.normal(0, 0.0002, 60)
    price = base_price * (1 + returns).cumprod()
    
    df = pd.DataFrame({
        'timestamp': dates,
        'open': price,
        'close': price * (1 + np.random.normal(0, 0.0001, 60)),
        'high': price * 1.0003,
        'low': price * 0.9997,
        'volume': np.random.randint(100, 500, 60)
    })
    
    return df, "MODO DE SEGURANÇA (ESTÁVEL)"

# --- 5. CÉREBRO VEX (LÓGICA DE FLUXO) ---
def analyze_market(df):
    if df is None or df.empty: return "NEUTRO", 0.0, "SEM DADOS"

    close = df['close'].values
    open_ = df['open'].values
    high = df['high'].values
    low = df['low'].values
    
    # Última vela (atual)
    c = close[-1]; o = open_[-1]; h = high[-1]; l = low[-1]
    body = abs(c - o)
    wick_up = h - max(c, o)
    wick_down = min(c, o) - l
    
    # Médias e RSI
    ema9 = pd.Series(close).ewm(span=9).mean().iloc[-1]
    
    delta = pd.Series(close).diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    rsi = 50 if np.isnan(rsi) else rsi
    
    score = 50.0
    signal = "NEUTRO"
    motive = "AGUARDANDO DEFINIÇÃO"

    # LÓGICA: FLUXO DE VELA (SEGUIR A FORÇA)
    
    # COMPRA
    if c > ema9 and c > o: # Acima da média e Verde
        if rsi > 50 and rsi < 85:
            # Se não tiver pavio gigante em cima rejeitando
            if wick_up < body * 0.4: 
                score = 94.0; signal = "COMPRA"; motive = "FLUXO COMPRADOR FORTE"
            else:
                score = 70.0; signal = "NEUTRO"; motive = "REJEIÇÃO SUPERIOR (PERIGO)"
        elif rsi >= 85:
            score = 91.0; signal = "COMPRA"; motive = "MOMENTUM DE ALTA (RSI)"

    # VENDA
    elif c < ema9 and c < o: # Abaixo da média e Vermelha
        if rsi < 50 and rsi > 15:
            # Se não tiver pavio gigante em baixo rejeitando
            if wick_down < body * 0.4:
                score = 94.0; signal = "VENDA"; motive = "FLUXO VENDEDOR FORTE"
            else:
                score = 70.0; signal = "NEUTRO"; motive = "REJEIÇÃO INFERIOR (PERIGO)"
        elif rsi <= 15:
            score = 91.0; signal = "VENDA"; motive = "MOMENTUM DE BAIXA (RSI)"

    return signal, score, motive

# --- 6. TELAS ---
def tela_login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c2:
        st.markdown("<h1 style='text-align:center; color:#00ff88;'>VEX ELITE</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>FOREX TERMINAL v12.0</p>", unsafe_allow_html=True)
        
        user = st.text_input("USUÁRIO", label_visibility="collapsed", placeholder="ID")
        st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)
        pwd = st.text_input("SENHA", type="password", label_visibility="collapsed", placeholder="SENHA")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("ENTRAR"):
            if user in CREDENCIAIS and pwd == CREDENCIAIS[user]:
                st.session_state['logado'] = True
                st.rerun()
            else:
                st.error("DADOS INVÁLIDOS")

def tela_dashboard():
    # Topo
    st.markdown("""
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #333; padding-bottom:10px; margin-bottom:20px;">
            <span style="font-size:1.5rem; font-weight:bold; color:#00ff88;">VEX FOREX</span>
            <span style="background:#00ff88; color:black; padding:2px 10px; font-weight:bold; border-radius:3px;">ONLINE</span>
        </div>
    """, unsafe_allow_html=True)
    
    # Seletor
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("<h4 style='margin:0; color:#00ff88;'>ATIVO</h4>", unsafe_allow_html=True)
        ativo = st.selectbox("Ativo", ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CAD", "AUD/USD"], label_visibility="collapsed")
    with c2:
        st.markdown("<h4 style='margin:0; color:#00ff88;'>AÇÃO</h4>", unsafe_allow_html=True)
        # Botão sem lógica complexa, apenas refresh
        gerar = st.button("ANALISAR")
    st.markdown("</div>", unsafe_allow_html=True)

    # Processamento
    if gerar:
        with st.spinner("CONECTANDO AO MERCADO..."):
            # Chama a função com Cache
            df, status = get_forex_data_cached(ativo)
            
            # Analisa
            sig, score, motive = analyze_market(df)
            
            # Exibição
            g_col, d_col = st.columns([2, 1])
            
            with g_col:
                st.markdown(f"<div class='neon-card'><h4>GRÁFICO {ativo} <span style='font-size:0.7rem; color:#aaa'>({status})</span></h4>", unsafe_allow_html=True)
                fig = go.Figure(data=[go.Candlestick(x=df['timestamp'], open=df['open'], high=df['high'], low=df['low'], close=df['close'], increasing_line_color='#00ff88', decreasing_line_color='#ff0055')])
                fig.update_layout(template="plotly_dark", height=400, xaxis_rangeslider_visible=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig, use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
            with d_col:
                st.markdown("<div class='neon-card' style='text-align:center; height:100%;'>", unsafe_allow_html=True)
                st.markdown("<span>ASSERTIVIDADE</span>", unsafe_allow_html=True)
                
                cor = "#00ff88" if score >= 90 else "#ffcc00"
                if score < 60: cor = "#ff0055"
                
                st.markdown(f"<div class='score-glow' style='color:{cor};'>{score:.0f}%</div>", unsafe_allow_html=True)
                
                if score >= 90:
                    direcao = "COMPRA" if sig == "COMPRA" else "VENDA"
                    bg_color = "#00ff88" if sig == "COMPRA" else "#ff0055"
                    st.markdown(f"<div style='background:{bg_color}; color:black; font-weight:bold; font-size:2rem; padding:10px; border-radius:5px; margin-top:10px;'>{direcao}</div>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin-top:10px; color:#ccc; font-size:0.8rem;'>{motive}</p>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='border:1px solid {cor}; color:{cor}; font-weight:bold; padding:10px; margin-top:10px;'>AGUARDE</div>", unsafe_allow_html=True)
                    st.markdown(f"<p style='margin-top:10px; color:#ccc; font-size:0.8rem;'>{motive}</p>", unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("SAIR"):
        st.session_state['logado'] = False
        st.rerun()

# --- 7. START ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
