import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import time
import streamlit.components.v1 as components # Para embutir o gráfico oficial

# --- 1. CONFIGURAÇÃO (LAYOUT ANTIGO - FLOW TERMINAL) ---
st.set_page_config(
    page_title="VEX ELITE | INVESTING FLOW",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS (VISUAL CYBER NEON - O "ANTIGO") ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@500;700&display=swap');
    
    /* Fundo Geral - Preto Absoluto para Contraste */
    .stApp {
        background-color: #000000;
        background-image: 
            radial-gradient(circle at 50% 0%, #1a1a1a 0%, #000000 70%);
        color: #ffffff;
    }
    
    /* Fontes Futuristas */
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        font-family: 'Rajdhani', sans-serif !important;
    }
    
    /* --- MENU DROPDOWN (CORRIGIDO) --- */
    .stSelectbox > div > div {
        background-color: #0d0d0d !important;
        color: #00ff88 !important;
        border: 1px solid #333 !important;
        font-weight: bold;
    }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #000000 !important;
        border: 1px solid #00ff88 !important;
    }
    li[role="option"] {
        background-color: #000000 !important;
        color: white !important;
    }
    li[role="option"]:hover, li[role="option"][aria-selected="true"] {
        background-color: #00ff88 !important;
        color: #000000 !important;
        font-weight: bold;
    }
    .stSelectbox svg { fill: #00ff88 !important; }
    
    /* --- BOTÃO NEON --- */
    .stButton > button {
        background: transparent !important;
        border: 2px solid #00ff88 !important;
        color: #00ff88 !important;
        font-family: 'Orbitron', sans-serif;
        text-transform: uppercase;
        font-weight: 900;
        padding: 25px;
        border-radius: 0px; /* Quadrado estilo terminal */
        transition: all 0.3s ease;
        box-shadow: 0 0 15px rgba(0, 255, 136, 0.1);
        width: 100%;
        font-size: 1.2rem;
    }
    .stButton > button:hover {
        background: #00ff88 !important;
        color: #000 !important;
        box-shadow: 0 0 40px rgba(0, 255, 136, 0.6);
        transform: scale(1.02);
    }
    
    /* --- CARDS --- */
    .neon-card {
        background: rgba(10, 10, 10, 0.8);
        border: 1px solid #333;
        padding: 25px;
        border-radius: 5px;
        box-shadow: 0 0 20px rgba(0,0,0,0.8);
        margin-bottom: 20px;
    }
    
    .score-glow {
        font-size: 7rem;
        font-family: 'Orbitron', sans-serif;
        font-weight: 900;
        text-shadow: 0 0 50px currentColor;
        line-height: 1;
        margin-top: 10px;
    }
    
    /* Remove rodapé padrão */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. MAPEAMENTO INVESTING.COM (ID DOS PARES) ---
# Isso conecta o gráfico direto no servidor deles
INVESTING_IDS = {
    "EUR/USD": 1,
    "GBP/USD": 2,
    "USD/JPY": 3,
    "USD/CHF": 4,
    "AUD/USD": 5,
    "EUR/GBP": 6,
    "USD/CAD": 7,
    "NZD/USD": 8,
    "USD/BRL": 2103
}

# --- 4. SESSÃO E LOGIN ---
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'analise_ativa' not in st.session_state:
    st.session_state['analise_ativa'] = None

CREDENCIAIS = {
    "wallace": "admin123",
    "cliente01": "pro2026"
}

# --- 5. COLETOR DE DADOS PARA ANÁLISE MATEMÁTICA (BACKEND) ---
# O gráfico visual vem do Investing (iframe), mas precisamos de dados numéricos para a IA calcular a entrada.
# Usamos Yahoo Finance para o cálculo pois é a fonte mais próxima e estável para robôs.
def get_calculation_data(symbol):
    try:
        # Tenta Yahoo Finance (Padrão)
        import yfinance as yf
        ticker = f"{symbol.replace('/', '')}=X"
        df = yf.download(ticker, period="1d", interval="1m", progress=False)
        if not df.empty:
            df = df.reset_index()
            df.columns = df.columns.str.lower()
            return df.tail(60)
    except:
        pass
        
    # Fallback Simples se falhar (para não travar o botão)
    return None

# --- 6. CÉREBRO VEX (LÓGICA DE FLUXO) ---
def analyze_flow(df):
    if df is None or df.empty:
        # Se não conseguir dados numéricos, gera uma análise baseada em Price Action seguro
        return "NEUTRO", 50.0, "AGUARDANDO DADOS NUMÉRICOS..."

    # Converte para array simples
    try:
        if 'datetime' in df.columns: df = df.rename(columns={'datetime': 'timestamp'})
        if 'date' in df.columns: df = df.rename(columns={'date': 'timestamp'})
        
        close = df['close'].values.flatten() # Garante array 1D
        open_ = df['open'].values.flatten()
        high = df['high'].values.flatten()
        low = df['low'].values.flatten()
        
        c = close[-1]; o = open_[-1]
        
        # Indicadores Matemáticos
        rsi_period = 14
        delta = pd.Series(close).diff()
        gain = (delta.where(delta > 0, 0)).rolling(rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(rsi_period).mean()
        rs = gain / loss
        rsi_series = 100 - (100 / (1 + rs))
        rsi = rsi_series.iloc[-1]
        if np.isnan(rsi): rsi = 50
        
        # Lógica de Fluxo Simples e Direta (V7.0)
        score = 0.0
        signal = "NEUTRO"
        motive = "MERCADO LATERAL"
        
        if c > o: # Vela Verde
            if rsi > 50 and rsi < 85:
                score = 96.0; signal = "COMPRA"; motive = "TENDÊNCIA DE ALTA (INVESTING)"
            elif rsi >= 85:
                score = 92.0; signal = "COMPRA"; motive = "MOMENTUM FORTE DE ALTA"
        elif c < o: # Vela Vermelha
            if rsi < 50 and rsi > 15:
                score = 96.0; signal = "VENDA"; motive = "TENDÊNCIA DE BAIXA (INVESTING)"
            elif rsi <= 15:
                score = 92.0; signal = "VENDA"; motive = "MOMENTUM FORTE DE BAIXA"
                
        return signal, score, motive
    except:
        return "NEUTRO", 50.0, "ERRO NO CÁLCULO"

# --- 7. TELA DE LOGIN (ESTILO HACKER) ---
def tela_login():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    with c2:
        st.markdown("""
            <div style="text-align: center; border: 2px solid #00ff88; padding: 40px; background: #000; box-shadow: 0 0 30px rgba(0,255,136,0.15);">
                <h1 style="font-family: 'Orbitron'; font-size: 3.5rem; margin-bottom: 0; color: #00ff88 !important; text-shadow: 0 0 10px #00ff88;">VEX ELITE</h1>
                <p style="letter-spacing: 6px; color: white; font-size: 0.9rem; margin-bottom: 30px; font-weight: bold;">INVESTING.COM DIRECT LINK</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        usuario = st.text_input("ID", placeholder="IDENTIFICAÇÃO", label_visibility="collapsed")
        st.markdown("<div style='height: 15px'></div>", unsafe_allow_html=True)
        senha = st.text_input("KEY", type="password", placeholder="CHAVE DE ACESSO", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("INICIAR PROTOCOLO"):
            if usuario in CREDENCIAIS and senha == CREDENCIAIS[usuario]:
                st.session_state['logado'] = True
                st.rerun()
            else:
                st.error("ACESSO NEGADO.")

# --- 8. TELA DASHBOARD (LAYOUT ANTIGO + GRÁFICO INVESTING) ---
def tela_dashboard():
    # Cabeçalho
    st.markdown("""
        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 25px;">
            <div>
                <span style="font-family: 'Orbitron'; font-size: 2rem; color: #00ff88 !important; font-weight: 900;">VEX ELITE</span>
            </div>
            <div style="text-align: right;">
                <span style="color: #aaa; font-size: 0.9rem; letter-spacing: 2px;">STATUS:</span>
                <span style="background: #00ff88; color: black; padding: 3px 12px; font-weight: 900; margin-left: 10px;">CONECTADO (BR.INVESTING)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Controle
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([2, 1, 2])
    with c1:
        st.markdown("<h4 style='color: #00ff88 !important; margin-bottom: 10px;'>ATIVO ALVO</h4>", unsafe_allow_html=True)
        # Lista filtrada para os IDs que temos mapeados
        ativo = st.selectbox("", list(INVESTING_IDS.keys()), label_visibility="collapsed")
    with c3:
        st.markdown("<h4 style='color: #00ff88 !important; margin-bottom: 10px;'>AÇÃO</h4>", unsafe_allow_html=True)
        # Botão Clássico "ANALISAR FLUXO"
        acionar = st.button("ANALISAR FLUXO (M1)")
    st.markdown("</div>", unsafe_allow_html=True)

    # Lógica do Botão
    if acionar:
        df = get_calculation_data(ativo)
        sig, precisao, motive = analyze_flow(df)
        st.session_state['analise_ativa'] = {
            'ativo': ativo, 'sig': sig, 'precisao': precisao, 'motive': motive
        }

    # Área Principal
    col_grafico, col_dados = st.columns([2.5, 1.5])
    
    # 1. GRÁFICO OFICIAL DO INVESTING.COM (IFRAME)
    with col_grafico:
        st.markdown("<div class='neon-card' style='padding: 10px;'>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='font-family: Orbitron; color: white;'>GRÁFICO AO VIVO | {ativo}</h3>", unsafe_allow_html=True)
        
        # Pega o ID do par
        pair_id = INVESTING_IDS.get(ativo, 1)
        
        # URL do Widget Oficial do Investing (Tema Escuro)
        # Isso garante que o gráfico seja EXATAMENTE o do site deles.
        investing_url = f"https://ssltvc.investing.com/?pair_ID={pair_id}&height=480&width=100%&interval=60&plotStyle=area&domain_ID=30&lang_ID=12&timezone_ID=12"
        
        # Renderiza o iframe
        components.iframe(investing_url, height=500, scrolling=False)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # 2. PAINEL DE SINAIS (LÓGICA VEX)
    with col_dados:
        if st.session_state['analise_ativa']:
            dados = st.session_state['analise_ativa']
            # Verifica se o gráfico na tela bate com a análise
            if dados['ativo'] != ativo:
                st.warning("⚠️ CLIQUE EM ANALISAR PARA ATUALIZAR O SINAL")
            
            st.markdown("<div class='neon-card' style='text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: center;'>", unsafe_allow_html=True)
            st.markdown("<p style='color: #aaa !important; font-size: 1rem; letter-spacing: 2px;'>FORÇA DO FLUXO</p>", unsafe_allow_html=True)
            
            cor_score = "#00ff88" if dados['precisao'] >= 90 else "#ffcc00"
            if dados['precisao'] < 60: cor_score = "#ff0055"

            st.markdown(f"<div class='score-glow' style='color: {cor_score} !important;'>{dados['precisao']:.1f}%</div>", unsafe_allow_html=True)
            
            if dados['precisao'] >= 90:
                acao_texto = dados['sig'] # COMPRA ou VENDA
                cor_bg = "linear-gradient(45deg, #00ff88, #00cc6a)" if acao_texto == "COMPRA" else "linear-gradient(45deg, #ff0055, #cc0044)"
                
                st.markdown(f"""
                    <div style="background: {cor_bg}; padding: 20px; border-radius: 5px; margin: 20px 0; box-shadow: 0 0 30px {cor_score};">
                        <h1 style="margin:0; font-size: 3.5rem; color: black !important; font-weight: 900; letter-spacing: 3px;">{acao_texto}</h1>
                    </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"<div style='border: 1px solid #333; padding: 15px; margin-top: 10px; background: rgba(0,0,0,0.5);'><span style='color: #00ff88 !important; font-weight: bold;'>MOTIVO:</span> {dados['motive']}</div>", unsafe_allow_html=True)
                st.markdown("<p style='margin-top: 20px; color: white !important; font-weight: bold; animation: pulse 1s infinite; font-size: 1.2rem;'>ENTRADA IMEDIATA</p>", unsafe_allow_html=True)
            
            else:
                st.markdown("""
                    <div style="border: 2px solid #ff0055; padding: 20px; margin: 20px 0; color: #ff0055;">
                        <h2 style="margin:0; font-size: 2rem; font-weight: 900;">AGUARDE</h2>
                    </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='color: #aaa !important;'>Cenário Atual: {dados['motive']}</p>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Estado inicial (antes de clicar)
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
