# main.py

import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from core.engine import CryptoEngine

# --- 1. SAYFA AYARLARI ---
st.set_page_config(layout="wide", page_title="Kripto Tracker", page_icon="🧊")

# --- 2. OTOMATİK YENİLEME (REAL-TIME) ---
# Sayfayı her 60 saniyede bir (60000ms) yeniler.
# Render'da RAM şişmesin diye süre makul tutulmalı.
count = st_autorefresh(interval=60000, limit=None, key="facer")

# --- 3. CUSTOM CSS (RESİMDEKİ UI TASARIMI) ---
st.markdown("""
<style>
    /* Ana Arka Plan (Deep Dark Blue) */
    .stApp {
        background-color: #0e1117;
    }
    
    /* Tablo Başlıkları */
    thead tr th:first-child { display:none }
    tbody th { display:none }
    
    /* Kart Görünümü (Dataframe Konteynerleri) */
    [data-testid="stDataFrame"] {
        background-color: #161b22;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #30363d;
    }
    
    /* Başlıklar */
    h1, h2, h3 {
        color: #e6edf3 !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Alt Başlıklar */
    p {
        color: #8b949e;
    }
    
    /* Yeşil Artış Yazısı (Custom Metric) */
    .positive-val {
        color: #3fb950;
        font-weight: bold;
        background-color: rgba(63, 185, 80, 0.1);
        padding: 2px 8px;
        border-radius: 6px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. BAŞLIK ALANI ---
c1, c2 = st.columns([0.8, 0.2])
with c1:
    st.title("Kripto Tracker Dashboard")
    st.markdown("Real-time crypto analysis based on EMA & SMA indicators.")
with c2:
    # Manuel Yenileme Butonu
    if st.button("🔄 Yenile"):
        st.rerun()

st.divider()

# --- 5. VERİ ÇEKME ---
engine = CryptoEngine()

# Spinner ile yükleniyor efekti
with st.spinner('Piyasa taranıyor... (Binance Futures)'):
    # En hacimli 40 coini tara (Hız için)
    top_coins = engine.get_top_volume_coins(limit=40)
    df_ema, df_sma = engine.fetch_and_analyze(top_coins)

# --- 6. İKİLİ KART YAPISI (GRID) ---
col_left, col_right = st.columns(2)

# --- SOL KART: EMA 25 ---
with col_left:
    st.subheader("Above 25 EMA (1-Day)")
    if not df_ema.empty:
        st.dataframe(
            df_ema,
            column_config={
                "Asset": st.column_config.TextColumn("Asset", width="small"),
                "Price": st.column_config.NumberColumn("Price", format="$%.4f"),
                "EMA Value": st.column_config.NumberColumn("EMA Value", format="$%.4f"),
                "Deviation %": st.column_config.NumberColumn(
                    "Deviation %",
                    format="%.2f%%",
                    help="Fiyatın ortalamadan uzaklığı"
                )
            },
            hide_index=True,
            use_container_width=True,
            height=500
        )
    else:
        st.info("EMA 25 üzerinde coin bulunamadı.")

# --- SAĞ KART: SMA 50 ---
with col_right:
    st.subheader("Above 50 SMA (1-Day)")
    if not df_sma.empty:
        st.dataframe(
            df_sma,
            column_config={
                "Asset": st.column_config.TextColumn("Asset", width="small"),
                "Price": st.column_config.NumberColumn("Price", format="$%.4f"),
                "SMA Value": st.column_config.NumberColumn("SMA Value", format="$%.4f"),
                "Deviation %": st.column_config.NumberColumn(
                    "Deviation %",
                    format="%.2f%%",
                    help="Fiyatın ortalamadan uzaklığı"
                )
            },
            hide_index=True,
            use_container_width=True,
            height=500
        )
    else:
        st.info("SMA 50 üzerinde coin bulunamadı.")