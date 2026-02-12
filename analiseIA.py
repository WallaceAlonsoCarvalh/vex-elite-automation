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

# --- 3. CSS "CYBER-FUTURE" (DESIGN MANTIDO 100%) ---
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

    /* --- CORREÇÃO DE VISIBILIDADE --- */
    h1, h2, h3, h4, h5, h6, p, label, div, span, li {
        color: #ffffff !important;
        font-family: 'Rajdhani', sans-serif;
    }

    /* --- BARRA DE SELEÇÃO (CRIPTO) --- */
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

    /* --- CARDS --- */
    .neon-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 25px;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        backdrop-filter: blur(10px);
    }

    /* --- SCORE --- */
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

# --- 5. INTELIGÊNCIA VEX-HFT v4.0 (SUPER CÉREBRO) ---
def get_fast_data(symbol):
    # Conexão Otimizada
    exchanges = [ccxt.bybit({'timeout': 4000}), ccxt.kucoin({'timeout': 4000}), ccxt.binance({'timeout': 4000})] 
    for ex in exchanges:
        try:
            # Busca 120 velas para cálculo profundo de volatilidade
            ohlcv = ex.fetch_ohlcv(symbol, timeframe='1m', limit=120) 
            if ohlcv:
                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
                return df
        except: continue
    return None

def calculate_choppiness(df):
    # Índice de "Choque" (Mercado Lateral/Bêbado)
    # Se estiver alto, NÃO OPERA.
    high = df['high']
    low = df['low']
    close = df['close']
    
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis=1, join='inner').max(axis=1)
    atr = tr.rolling(1).mean()
    
    highh = high.rolling(14).max()
    lowl = low.rolling(14).min()
    
    ci = 100 * np.log10(atr.rolling(14).sum() / (highh - lowl)) / np.log10(14)
    return ci.iloc[-1]

def analyze_all_hypothesis(df):
    """
    Lógica VEX-HFT v4.0:
    Analisa Volume, Padrões de Candle, Fluxo e Ruído.
    """
    # 1. Preparação dos Dados
    close = df['close'].values
    open_ = df['open'].values
    high = df['high'].values
    low = df['low'].values
    vol = df['volume'].values
    
    # Índices da última vela e penúltima
    c_now = close[-1]
    o_now = open_[-1]
    c_prev = close[-2]
    o_prev = open_[-2]
    
    # 2. Verifica "Mercado Bêbado" (Choppiness Index)
    # Se o mercado não tiver direção, cancela tudo.
    chop = calculate_choppiness(df)
    if chop > 61.8: # Mercado Travado/Lateral Extremo
        return "NEUTRO", 0.0, "MERCADO SEM DIREÇÃO (RISCO ALTO)"

    # --- CÁLCULO DE SCORE DE PROBABILIDADE ---
    score = 0
    signal = "NEUTRO"
    motive = "AGUARDANDO OPORTUNIDADE"

    # --- HIPÓTESE 1: REVERSÃO POR EXAUSTÃO (A mais assertiva) ---
    # Vela atual é muito grande e esticada (longe da média)
    ema20 = pd.Series(close).ewm(span=20).mean().iloc[-1]
    distancia_media = abs(c_now - ema20)
    tamanho_vela = abs(c_now - o_now)
    tamanho_medio = np.mean(abs(close[-10:] - open_[-10:])) # Média das últimas 10
    
    # Se a vela é 3x maior que a média e está longe da EMA20 = Exaustão
    if tamanho_vela > (tamanho_medio * 2.5):
        # Checar Pavio (Rejeição)
        pavio_sup = high[-1] - max(c_now, o_now)
        pavio_inf = min(c_now, o_now) - low[-1]
        
        # Vela Verde Gigante + Pavio em cima = VAI CAIR
        if c_now > o_now and pavio_sup > (tamanho_vela * 0.3):
            score = 98.5
            signal = "VENDA"
            motive = "EXAUSTÃO DE COMPRA (REJEIÇÃO DE TOPO)"
        
        # Vela Vermelha Gigante + Pavio em baixo = VAI SUBIR
        elif c_now < o_now and pavio_inf > (tamanho_vela * 0.3):
            score = 98.5
            signal = "COMPRA"
            motive = "EXAUSTÃO DE VENDA (REJEIÇÃO DE FUNDO)"

    # --- HIPÓTESE 2: CONTINUIDADE DE FLUXO (ENGOLFO) ---
    # Se não for exaustão, pode ser força
    elif score < 90:
        # Engolfo de Alta (Vela verde engole a vermelha anterior)
        if c_now > o_now and c_prev < o_prev and c_now > o_prev and o_now < c_prev:
             # Confirmação com Volume
            if vol[-1] > vol[-2]:
                score = 94.0
                signal = "COMPRA"
                motive = "PADRÃO: ENGOLFO DE ALTA + VOLUME"
        
        # Engolfo de Baixa (Vela vermelha engole a verde anterior)
        elif c_now < o_now and c_prev > o_prev and c_now < o_prev and o_now > c_prev:
            if vol[-1] > vol[-2]:
                score = 94.0
                signal = "VENDA"
                motive = "PADRÃO: ENGOLFO DE BAIXA + VOLUME"

    # --- HIPÓTESE 3: PROTEÇÃO DE TENDÊNCIA (MÉDIAS) ---
    # Se nenhuma das anteriores bater forte, usa tendência macro
    if score < 90:
        ema9 = pd.Series(close).ewm(span=9).mean().iloc[-1]
        ema50 = pd.Series(close).ewm(span=50).mean().iloc[-1]
        
        # Tendência Clara de Alta
        if c_now > ema9 and ema9 > ema50:
             # RSI (Relative Strength Index) Simples
            delta = pd.Series(close).diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            if rsi > 40 and rsi < 65: # Zona segura de compra
                score = 91.5
                signal = "COMPRA"
                motive = "FLUXO DE TENDÊNCIA (EMA CROSS)"
        
        # Tendência Clara de Baixa
        elif c_now < ema9 and ema9 < ema50:
            delta = pd.Series(close).diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            
            if rsi < 60 and rsi > 35: # Zona segura de venda
                score = 91.5
                signal = "VENDA"
                motive = "FLUXO DE TENDÊNCIA (EMA CROSS)"

    # --- FILTRO FINAL DE SEGURANÇA (O "ANTI-LOSS") ---
    # Se a vela atual for muito pequena (Doji), anula tudo. Mercado indeciso.
    if tamanho_vela < (tamanho_medio * 0.3):
        score = 45.0
        signal = "NEUTRO"
        motive = "MERCADO INDECISO (DOJI) - NÃO OPERE"

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
    # --- HEADER ---
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

    # --- RESULTADOS ---
    if acionar:
        with st.spinner(f"EXECUTANDO ALGORITMO HFT EM {ativo}..."):
            df = get_fast_data(ativo)
            
            if df is not None:
                # Análise VEX-HFT
                sig, precisao, motivo = analyze_all_hypothesis(df)
                
                col_grafico, col_dados = st.columns([2.5, 1.5])
                
                # GRÁFICO
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
                
                # DADOS
                with col_dados:
                    st.markdown("<div class='neon-card' style='text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
                    
                    st.markdown("<p style='color: #aaa !important; font-size: 0.9rem;'>PROBABILIDADE DE ACERTO</p>", unsafe_allow_html=True)
                    
                    cor_score = "#00ff88" if precisao >= 91 else "#ffcc00" # Filtro mais rigoroso
                    if precisao < 60: cor_score = "#ff0055"

                    st.markdown(f"<div class='score-glow' style='color: {cor_score} !important;'>{precisao:.1f}%</div>", unsafe_allow_html=True)
                    
                    if precisao >= 91: # Só libera acima de 91
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
                            <div style="border: 2px solid #ff0055; padding: 15px; margin: 10px 0; color: #ff0055;">
                                <h2 style="margin:0; color: #ff0055 !important;">NÃO ENTRAR</h2>
                            </div>
                        """, unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #aaa !important;'>Cenário: {motivo}</p>", unsafe_allow_html=True)
                        st.markdown("<p style='font-size: 0.8rem; color: #ff0055 !important;'>RISCO CALCULADO ALTO. AGUARDE.</p>", unsafe_allow_html=True)
                    
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
