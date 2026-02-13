import streamlit as st
import pandas as pd
import numpy as np
import datetime
import time
import requests
import streamlit.components.v1 as components

# --- 1. CONFIGURAÇÃO ---
st.set_page_config(
    page_title="VEX ELITE | TITAN PRO",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS (VISUAL IDÊNTICO AO SEU PRINT) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    
    /* Fundo Preto Absoluto */
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
    
    /* BOTÃO DE AÇÃO */
    .stButton > button {
        background: transparent !important;
        border: 2px solid #00ff88 !important;
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        text-transform: uppercase;
        padding: 20px;
        transition: 0.3s;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.1);
        width: 100%;
        font-size: 1.2rem;
    }
    .stButton > button:hover {
        background: #00ff88 !important;
        color: black !important;
        box-shadow: 0 0 40px rgba(0, 255, 136, 0.6);
        transform: scale(1.02);
    }

    /* CARDS */
    .neon-card {
        background: rgba(20, 20, 20, 0.9);
        border: 1px solid #333;
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

# --- 3. MAPEAMENTO DE ATIVOS ---
PAIRS = {
    "GBP/USD": {"tv": "FX:GBPUSD", "yf": "GBPUSD=X"},
    "EUR/USD": {"tv": "FX:EURUSD", "yf": "EURUSD=X"},
    "USD/JPY": {"tv": "FX:USDJPY", "yf": "JPY=X"},
    "USD/CHF": {"tv": "FX:USDCHF", "yf": "CHF=X"},
    "AUD/USD": {"tv": "FX:AUDUSD", "yf": "AUDUSD=X"},
    "USD/CAD": {"tv": "FX:USDCAD", "yf": "CAD=X"},
    "EUR/JPY": {"tv": "FX:EURJPY", "yf": "EURJPY=X"},
}

# --- 4. SESSÃO ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'analise' not in st.session_state:
    st.session_state['analise'] = None

CREDENCIAIS = {"wallace": "admin123", "cliente01": "pro2026"}

# --- 5. COLETOR DE DADOS "QUEBRA-BLOQUEIO" ---
def get_data_direct(symbol_key):
    """
    Usa requisição HTTP direta com cabeçalhos de navegador para evitar bloqueio.
    """
    ticker = PAIRS[symbol_key]['yf']
    # URL da API v8 do Yahoo (Mais estável)
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        data = response.json()
        
        if 'chart' in data and 'result' in data['chart']:
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            indicators = result['indicators']['quote'][0]
            
            df = pd.DataFrame({
                'timestamp': pd.to_datetime(timestamps, unit='s'),
                'open': indicators['open'],
                'high': indicators['high'],
                'low': indicators['low'],
                'close': indicators['close'],
                'volume': indicators['volume']
            })
            
            # Limpa dados vazios
            df = df.dropna()
            return df.tail(60) # Retorna últimas 60 velas
    except Exception as e:
        st.error(f"Erro de conexão API: {e}")
        return None
    return None

# --- 6. CÉREBRO TITAN (LÓGICA HFT DE 1 MINUTO) ---
def calculate_titan_signal(df):
    if df is None or len(df) < 20:
        return "NEUTRO", 50.0, "AGUARDANDO DADOS NUMÉRICOS..."

    # Dados da última vela (A que está se mexendo)
    close = df['close'].values
    high = df['high'].values
    low = df['low'].values
    open_ = df['open'].values
    
    current_price = close[-1]
    
    # --- INDICADORES ---
    # 1. EMA 9 (Tendência Rápida)
    ema9 = pd.Series(close).ewm(span=9, adjust=False).mean().iloc[-1]
    
    # 2. RSI 14 (Força Relativa)
    delta = pd.Series(close).diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs)).iloc[-1]
    
    # 3. Análise de Pavio (Rejeição)
    body_size = abs(close[-1] - open_[-1])
    upper_wick = high[-1] - max(close[-1], open_[-1])
    lower_wick = min(close[-1], open_[-1]) - low[-1]
    
    # --- LÓGICA DE DECISÃO ---
    score = 50.0
    signal = "NEUTRO"
    motive = "MERCADO LATERAL"

    # CENÁRIO DE COMPRA (CALL)
    # Preço acima da média E RSI apontando pra cima
    if current_price > ema9:
        if rsi > 50 and rsi < 85:
            # Se não tiver pavio gigante em cima barrando
            if upper_wick < (body_size * 0.5):
                score = 94.0
                signal = "COMPRA"
                motive = "FLUXO COMPRADOR CONFIRMADO"
            else:
                score = 75.0
                motive = "TENDÊNCIA DE ALTA COM REJEIÇÃO"
        elif rsi >= 85:
            score = 91.0
            signal = "COMPRA"
            motive = "MOMENTUM FORTE (ALTA)"

    # CENÁRIO DE VENDA (PUT)
    # Preço abaixo da média E RSI apontando pra baixo
    elif current_price < ema9:
        if rsi < 50 and rsi > 15:
            # Se não tiver pavio gigante em baixo barrando
            if lower_wick < (body_size * 0.5):
                score = 94.0
                signal = "VENDA"
                motive = "FLUXO VENDEDOR CONFIRMADO"
            else:
                score = 75.0
                motive = "TENDÊNCIA DE BAIXA COM REJEIÇÃO"
        elif rsi <= 15:
            score = 91.0
            signal = "VENDA"
            motive = "MOMENTUM FORTE (BAIXA)"

    return signal, score, motive

# --- 7. INTERFACE ---
def tela_login():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("""
            <div style="text-align: center; border: 2px solid #00ff88; padding: 40px; background: #000; box-shadow: 0 0 30px rgba(0,255,136,0.15);">
                <h1 style="font-family: 'Orbitron'; font-size: 3rem; margin-bottom: 0; color: #00ff88 !important;">VEX ELITE</h1>
                <p style="letter-spacing: 4px; color: white; font-size: 0.9rem; margin-bottom: 30px; font-weight: bold;">FOREX TITAN ACCESS</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        user = st.text_input("ID", placeholder="IDENTIFICAÇÃO", label_visibility="collapsed")
        st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)
        senha = st.text_input("KEY", type="password", placeholder="CHAVE DE ACESSO", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("INICIAR PROTOCOLO"):
            if user in CREDENCIAIS and senha == CREDENCIAIS[user]:
                st.session_state['logado'] = True
                st.rerun()
            else:
                st.error("ACESSO NEGADO.")

def tela_dashboard():
    # Header
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 25px;">
            <div>
                <span style="font-family: 'Orbitron'; font-size: 2rem; color: #00ff88 !important; font-weight: 900;">VEX ELITE</span>
            </div>
            <div style="text-align: right;">
                <span style="background: #00ff88; color: black; padding: 3px 12px; font-weight: 900;">ONLINE</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Controles
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.markdown("<h4 style='color: #00ff88 !important; margin-bottom: 10px;'>PAR FOREX</h4>", unsafe_allow_html=True)
        ativo = st.selectbox("", list(PAIRS.keys()), label_visibility="collapsed")
    with c3:
        st.markdown("<h4 style='color: #00ff88 !important; margin-bottom: 10px;'>IA TITAN</h4>", unsafe_allow_html=True)
        if st.button("ANALISAR AGORA"):
            with st.spinner("PROCESSANDO ALGORITMO..."):
                # Busca dados matemáticos
                df = get_data_direct(ativo)
                # Calcula sinal
                sig, score, motive = calculate_titan_signal(df)
                st.session_state['analise'] = {'ativo': ativo, 'sig': sig, 'score': score, 'motive': motive}
    st.markdown("</div>", unsafe_allow_html=True)

    # Área Principal
    col_grafico, col_dados = st.columns([2.5, 1.5])
    
    # 1. GRÁFICO TRADINGVIEW (VISUAL PERFEITO - IDENTICO AO VEX)
    with col_grafico:
        st.markdown(f"<h3 style='font-family: Orbitron; color: white;'>MERCADO REAL | {ativo}</h3>", unsafe_allow_html=True)
        
        # Símbolo para o TradingView
        tv_symbol = PAIRS[ativo]['tv']
        
        # Widget Oficial do TradingView (HTML/JS)
        # Isso garante que o usuário veja exatamente o mesmo gráfico da corretora
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
    
    # 2. PAINEL DE SINAIS (LÓGICA VEX)
    with col_dados:
        if st.session_state['analise']:
            res = st.session_state['analise']
            if res['ativo'] != ativo:
                st.warning("⚠️ CLIQUE EM ANALISAR PARA ATUALIZAR")
            
            st.markdown("<div class='neon-card' style='text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
            st.markdown("<p style='color: #aaa !important; font-size: 1rem; letter-spacing: 2px;'>PRECISÃO DO SINAL</p>", unsafe_allow_html=True)
            
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
                st.markdown("<p style='margin-top: 20px; color: white !important; font-weight: bold; animation: pulse 1s infinite; font-size: 1.2rem;'>ENTRADA IMEDIATA</p>", unsafe_allow_html=True)
            
            else:
                st.markdown("""
                    <div style="border: 2px solid #ff0055; padding: 20px; margin: 20px 0; color: #ff0055;">
                        <h2 style="margin:0; font-size: 2rem; font-weight: 900;">AGUARDE</h2>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='color: #aaa !important;'>Cenário: {res['motive']}</p>", unsafe_allow_html=True)
            
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
