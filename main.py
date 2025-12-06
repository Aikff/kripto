# main.py

import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from core.engine import CryptoEngine

# --- 1. SAYFA VE TASARIM AYARLARI ---
st.set_page_config(layout="wide", page_title="Kripto Tracker", page_icon="🧊")

# Otomatik Yenileme: Her 5 dakikada bir (300.000ms)
# Tüm coinleri taramak uzun sürdüğü için 1 dk yerine 5 dk daha sağlıklıdır.
st_autorefresh(interval=300000, key="datarefresh")

# --- CSS ENJEKSİYONU (DARK UI) ---
st.markdown("""
<style>
    /* Ana Arka Plan */
    .stApp { background-color: #0d1117; }
    
    /* Kart Yapısı */
    div[data-testid="stDataFrame"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 10px;
    }
    
    /* Başlıklar */
    h1, h2, h3 { color: #c9d1d9 !important; font-family: sans-serif; }
    p { color: #8b949e !important; }
    
    /* Metrik Renkleri */
    div[data-testid="stMetricValue"] { color: #3fb950; }
</style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
c1, c2 = st.columns([0.85, 0.15])
with c1:
    st.title("Kripto Tracker Dashboard")
    st.markdown("Real-time analysis: All Active Binance Futures Coins")
with c2:
    if st.button("🔄 Tara", use_container_width=True):
        st.rerun()

st.divider()

# --- 3. VERİ TARAMA SÜRECİ ---
engine = CryptoEngine()

# İlk açılışta veya yenilemede çalışır
status_text = st.empty()
progress_bar = st.progress(0, text="Piyasa verileri alınıyor...")

try:
    # 1. Tüm Sembolleri Getir
    all_symbols = engine.get_all_futures_symbols()
    status_text.text(f"Toplam {len(all_symbols)} aktif coin bulundu. Analiz başlıyor...")
    
    # 2. Analiz Et (İlerleme çubuğu ile)
    df_ema, df_sma = engine.fetch_and_analyze(all_symbols, progress_bar)
    
    # İşlem bitince barı temizle
    progress_bar.empty()
    status_text.empty()

    # --- 4. SONUÇLARI GÖSTER (GRID) ---
    col_left, col_right = st.columns(2)

    # SOL KART: EMA 25
    with col_left:
        st.subheader(f"Above 25 EMA (1-Day) - {len(df_ema)}")
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
                        help="Yeşil oran, fiyatın ortalamadan ne kadar yukarıda olduğunu gösterir."
                    )
                },
                hide_index=True,
                use_container_width=True,
                height=600
            )
        else:
            st.warning("EMA 25 üzerinde coin yok.")

    # SAĞ KART: SMA 50
    with col_right:
        st.subheader(f"Above 50 SMA (1-Day) - {len(df_sma)}")
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
                        help="Yeşil oran, fiyatın ortalamadan ne kadar yukarıda olduğunu gösterir."
                    )
                },
                hide_index=True,
                use_container_width=True,
                height=600
            )
        else:
            st.warning("SMA 50 üzerinde coin yok.")

except Exception as e:
    st.error(f"Bir hata oluştu: {e}")
