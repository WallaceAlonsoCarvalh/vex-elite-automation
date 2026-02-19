import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(
    page_title="VEX ELITE | GLOBAL TITAN",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS (VISUAL DARK NEON - OTIMIZADO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    
    .stApp {
        background-color: #000000;
        color: #ffffff;
    }
    
    h1, h2, h3, p, div, span, label { font-family: 'Rajdhani', sans-serif !important; }
    
    /* MENU DROPDOWN */
    .stSelectbox > div > div {
        background-color: #0d0d0d !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
    }
    div[data-baseweb="popover"] { background-color: #0d0d0d !important; }
    li[role="option"] { color: white !important; background-color: #0d0d0d !important; }
    li[role="option"]:hover { background-color: #00ff88 !important; color: black !important; font-weight: bold; }
    .stSelectbox svg { fill: #00ff88 !important; }
    
    /* BOTÃO DE AÇÃO - EFEITO NEON */
    .stButton > button {
        background: transparent !important;
        border: 2px solid #00ff88 !important;
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        text-transform: uppercase;
        padding: 25px;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 0 10px rgba(0, 255, 136, 0.2);
        width: 100%;
        font-size: 1.3rem;
    }
    .stButton > button:hover {
        background: #00ff88 !important;
        color: black !important;
        box-shadow: 0 0 50px rgba(0, 255, 136, 0.8);
        transform: scale(1.01);
    }
    .stButton > button:active {
        transform: scale(0.98);
    }

    /* CARDS */
    .neon-card {
        background: rgba(15, 15, 15, 0.95);
        border: 1px solid #222;
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
    }
    
    .score-glow {
        font-family: 'Orbitron';
        font-size: 5rem;
        font-weight: 900;
        text-shadow: 0 0 30px currentColor;
        line-height: 1;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. MAPEAMENTO (FOREX E CRIPTO) ---
# Adicionado suporte robusto para criptomoedas padrão
PAIRS = {
    # FOREX
    "EUR/USD": {"tv": "FX:EURUSD", "yf": "EURUSD=X"},
    "GBP/USD": {"tv": "FX:GBPUSD", "yf": "GBPUSD=X"},
    "USD/JPY": {"tv": "FX:USDJPY", "yf": "JPY=X"},
    "USD/CHF": {"tv": "FX:USDCHF", "yf": "CHF=X"},
    "AUD/USD": {"tv": "FX:AUDUSD", "yf": "AUDUSD=X"},
    "USD/CAD": {"tv": "FX:USDCAD", "yf": "CAD=X"},
    "EUR/JPY": {"tv": "FX:EURJPY", "yf": "EURJPY=X"},
    
    # CRIPTO (CRYPTON)
    "BTC/USDT": {"tv": "BINANCE:BTCUSDT", "yf": "BTC-USD"},
    "ETH/USDT": {"tv": "BINANCE:ETHUSDT", "yf": "ETH-USD"},
    "BNB/USDT": {"tv": "BINANCE:BNBUSDT", "yf": "BNB-USD"},
    "SOL/USDT": {"tv": "BINANCE:SOLUSDT", "yf": "SOL-USD"},
    "XRP/USDT": {"tv": "BINANCE:XRPUSDT", "yf": "XRP-USD"},
}

# --- 4. SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'analise' not in st.session_state:
    st.session_state['analise'] = None

CREDENCIAIS = {"wallace": "admin123", "cliente01": "pro2026"}

# --- 5. COLETOR DE DADOS OTIMIZADO (FAST-FETCH) ---
def get_data_fast(symbol_key):
    """
    Usa a API Query1 do Yahoo (JSON leve) para baixar dados instantaneamente.
    Pega apenas o necessário para não travar. Funciona para Cripto e Forex.
    """
    ticker = PAIRS[symbol_key]['yf']
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=3)
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart']:
            result = data['chart']['result'][0]
            timestamp = result['timestamp']
            quote = result['indicators']['quote'][0]
            
            df = pd.DataFrame({
                'timestamp': pd.to_datetime(timestamp, unit='s'),
                'open': quote['open'],
                'high': quote['high'],
                'low': quote['low'],
                'close': quote['close'],
                'volume': quote.get('volume', [0]*len(quote['close']))
            })
            
            # Limpeza rápida
            df = df.dropna()
            return df.tail(50) # Últimas 50 velas bastam para a análise
    except:
        return None
    return None

# --- 6. CÉREBRO TITAN 2.0 (LÓGICA HÍBRIDA) ---
def calculate_titan_speed(df):
    if df is None or len(df) < 20:
        return "NEUTRO", 50.0, "AGUARDANDO DADOS..."

    # Converte para array numpy (Cálculo Instantâneo)
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    
    # 1. Bandas de Bollinger (Volatilidade)
    sma20 = pd.Series(close).rolling(20).mean().iloc[-1]
    std20 = pd.Series(close).rolling(20).std().iloc[-1]
    upper_bb = sma20 + (2 * std20)
    lower_bb = sma20 - (2 * std20)
    
    # 2. RSI (Força)
    delta = pd.Series(close).diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    if np.isnan(rsi): rsi = 50
    
    # 3. EMA 9 (Tendência Rápida)
    ema9 = pd.Series(close).ewm(span=9).mean().iloc[-1]
    
    price = close[-1]
    
    score = 50.0
    signal = "NEUTRO"
    motive = "MERCADO INDECISO"

    # --- LÓGICA HÍBRIDA (TENDÊNCIA + REVERSÃO) ---
    
    # CENÁRIO 1: FORÇA COMPRADORA (FLUXO)
    if price > ema9:
        if rsi > 50 and rsi < 80:
            score = 94.0
            signal = "COMPRA"
            motive = "TITAN: FLUXO DE ALTA LIMPO"
        elif price > upper_bb and rsi > 70: 
            # Estourou a banda com força (Momentum)
            score = 91.0
            signal = "COMPRA"
            motive = "TITAN: EXPLOSÃO DE ALTA (MOMENTUM)"
            
    # CENÁRIO 2: FORÇA VENDEDORA (FLUXO)
    elif price < ema9:
        if rsi < 50 and rsi > 20:
            score = 94.0
            signal = "VENDA"
            motive = "TITAN: FLUXO DE BAIXA LIMPO"
        elif price < lower_bb and rsi < 30:
            # Estourou banda pra baixo
            score = 91.0
            signal = "VENDA"
            motive = "TITAN: EXPLOSÃO DE BAIXA (MOMENTUM)"

    # CENÁRIO 3: REVERSÃO EM BANDA (LATERALIZAÇÃO EXTREMA)
    if rsi > 85 and price >= upper_bb:
        score = 88.0
        signal = "VENDA"
        motive = "TITAN: EXAUSTÃO DE COMPRA (REVERSÃO)"
    
    if rsi < 15 and price <= lower_bb:
        score = 88.0
        signal = "COMPRA"
        motive = "TITAN: EXAUSTÃO DE VENDA (REVERSÃO)"

    return signal, score, motive

# --- 7. TELAS ---
def tela_login():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("""
            <div style="text-align: center; border: 2px solid #00ff88; padding: 40px; background: #000; box-shadow: 0 0 30px rgba(0,255,136,0.15);">
                <h1 style="font-family: 'Orbitron'; font-size: 3rem; margin-bottom: 0; color: #00ff88 !important;">VEX ELITE</h1>
                <p style="letter-spacing: 4px; color: white; font-size: 0.9rem; margin-bottom: 30px; font-weight: bold;">GLOBAL TITAN ACCESS</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        user = st.text_input("ID", placeholder="IDENTIFICAÇÃO", label_visibility="collapsed")
        st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)
        senha = st.text_input("KEY", type="password", placeholder="CHAVE DE ACESSO", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("INICIAR SISTEMA"):
            if user in CREDENCIAIS and senha == CREDENCIAIS[user]:
                st.session_state['logado'] = True
                st.rerun()
            else:
                st.error("ACESSO NEGADO.")

def tela_dashboard():
    # Cabeçalho
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 25px;">
            <div>
                <span style="font-family: 'Orbitron'; font-size: 2rem; color: #00ff88 !important; font-weight: 900;">VEX ELITE</span>
            </div>
            <div style="text-align: right;">
                <span style="background: #00ff88; color: black; padding: 3px 12px; font-weight: 900;">ONLINE (V18.0)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Controles
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.markdown("<h4 style='color: #00ff88 !important; margin-bottom: 10px;'>PAR (FOREX / CRIPTO)</h4>", unsafe_allow_html=True)
        ativo = st.selectbox("", list(PAIRS.keys()), label_visibility="collapsed")
    with c3:
        st.markdown("<h4 style='color: #00ff88 !important; margin-bottom: 10px;'>IA TITAN SPEED</h4>", unsafe_allow_html=True)
        if st.button("ANALISAR AGORA (INSTANTÂNEO)"):
            df = get_data_fast(ativo)
            sig, score, motive = calculate_titan_speed(df)
            st.session_state['analise'] = {'ativo': ativo, 'sig': sig, 'score': score, 'motive': motive}
    st.markdown("</div>", unsafe_allow_html=True)

    # Área Principal
    col_grafico, col_dados = st.columns([2.5, 1.5])
    
    # 1. GRÁFICO TRADINGVIEW (VISUAL OFICIAL ADAPTÁVEL)
    with col_grafico:
        st.markdown(f"<h3 style='font-family: Orbitron; color: white;'>MERCADO REAL | {ativo}</h3>", unsafe_allow_html=True)
        tv_symbol = PAIRS[ativo]['tv']
        html_code = f"""
        <div class="tradingview-widget-container">
          <div id="tradingview_chart"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget(
          {{
          "width": "100%",
          "height": 500,
          "symbol": "{tv_symbol}",
          "interval": "1",
          "timezone": "America/Sao_Paulo",
          "theme": "dark",
          "style": "1",
          "locale": "br",
          "toolbar_bg": "#f1f3f6",
          "enable_publishing": false,
          "hide_top_toolbar": true,
          "save_image": false,
          "container_id": "tradingview_chart"
          }});
          </script>
        </div>
        """
        components.html(html_code, height=510)
    
    # 2. PAINEL DE SINAIS
    with col_dados:
        if st.session_state['analise']:
            res = st.session_state['analise']
            
            if res['ativo'] != ativo:
                st.warning("⚠️ SINAL DESATUALIZADO. CLIQUE NOVAMENTE PARA ATUALIZAR O ATIVO.")
            
            st.markdown("<div class='neon-card' style='text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
            st.markdown("<p style='color: #aaa !important; font-size: 1rem; letter-spacing: 2px;'>PRECISÃO DA ENTRADA</p>", unsafe_allow_html=True)
            
            cor_score = "#00ff88" if res['score'] >= 90 else "#ffcc00"
            if res['score'] < 60: cor_score = "#ff0055"

            st.markdown(f"<div class='score-glow' style='color: {cor_score} !important;'>{res['score']:.1f}%</div>", unsafe_allow_html=True)
            
            if res['score'] >= 90:
                acao_texto = res['sig']
                cor_bg = "linear-gradient(45deg, #00ff88, #00cc6a)" if acao_texto == "COMPRA" else "linear-gradient(45deg, #ff0055, #cc0044)"
                
                st.markdown(f"""
                    <div style="background: {cor_bg}; padding: 20px; border-radius: 5px; margin: 20px 0; box-shadow: 0 0 30px {cor_score};">
                        <h1 style="margin:0; font-size: 3.5rem; color: black !important; font-weight: 900; letter-spacing: 3px;">{acao_texto}</h1>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"<div style='border: 1px solid #333; padding: 15px; margin-top: 10px; background: rgba(0,0,0,0.5);'><span style='color: #00ff88 !important; font-weight: bold;'>MOTIVO:</span> {res['motive']}</div>", unsafe_allow_html=True)
                st.markdown("<p style='margin-top: 20px; color: white !important; font-weight: bold; animation: pulse 1s infinite; font-size: 1.2rem;'>ENTRADA IMEDIATA (M1)</p>", unsafe_allow_html=True)
            
            else:
                st.markdown("""
                    <div style="border: 2px solid #ff0055; padding: 20px; margin: 20px 0; color: #ff0055;">
                        <h2 style="margin:0; font-size: 2rem; font-weight: 900;">AGUARDE</h2>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='color: #aaa !important;'>Cenário: {res['motive']}</p>", unsafe_allow_html=True)
                if res['score'] == 50.0:
                    st.markdown("<p style='font-size: 0.8rem; color: #ff0055;'>Tentando reconectar aos dados ou mercado fechado...</p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='neon-card' style='text-align: center; height: 100%; display: flex; align-items: center; justify-content: center;'><h3 style='color: #555;'>AGUARDANDO ANÁLISE...</h3></div>", unsafe_allow_html=True)

    st.markdown("<br><br><br>", unsafe_allow_html=True)
    if st.button("ENCERRAR SESSÃO"):
        st.session_state['logado'] = False
        st.rerun()

# --- 8. EXECUÇÃO ---
if st.session_state['logado']:
    tela_dashboard()
else:
    tela_login()
