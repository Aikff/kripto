# main.py

import streamlit as st
import pandas as pd
from core.engine import CryptoEngine
import time

# Sayfa Ayarı (Geniş Mod)
st.set_page_config(layout="wide", page_title="Kripto Tracker Dashboard", page_icon="💎")

# --- HTML OLUŞTURUCU FONKSİYONLAR ---

def generate_table_rows(df, indicator_type):
    """
    Pandas verisini senin HTML tablosundaki <tr> yapısına çevirir.
    """
    html_rows = ""
    
    if df.empty:
        return """<tr><td colspan="4" class="px-4 py-3 text-neutral-400 text-center">Veri bulunamadı...</td></tr>"""

    # Sapma oranına göre sırala
    df = df.sort_values(by='Deviation', ascending=False)

    for index, row in df.iterrows():
        asset = row['Asset']
        price = f"${row['Price']:,.4f}"
        ind_val = f"${row['Indicator']:,.4f}"
        dev = row['Deviation']
        
        # Renk tonu (Yeşil)
        dev_str = f"+{dev:.2f}%"
        
        # Logo yerine Baş Harf (Avatar) Mantığı
        # Gerçek resim URL'leri genelde API gerektirir, bu yöntem daha hızlıdır.
        avatar_color = "bg-blue-600" if indicator_type == "EMA" else "bg-purple-600"
        initial = asset[0]

        row_html = f"""
        <tr class="hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
            <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                    <div class="flex items-center justify-center w-8 h-8 rounded-full {avatar_color} text-white font-bold text-xs">
                        {initial}
                    </div>
                    <div class="text-white text-sm font-medium leading-normal">{asset}</div>
                </div>
            </td>
            <td class="px-4 py-3 text-white text-sm font-normal leading-normal">{price}</td>
            <td class="px-4 py-3 text-neutral-400 text-sm font-normal leading-normal">{ind_val}</td>
            <td class="px-4 py-3 text-sm font-normal leading-normal">
                <span class="inline-flex items-center rounded-md bg-green-500/10 px-2 py-1 text-xs font-medium text-green-400 ring-1 ring-inset ring-green-500/20">
                    {dev_str}
                </span>
            </td>
        </tr>
        """
        html_rows += row_html
    return html_rows

# --- VERİ ÇEKME ---

engine = CryptoEngine()

# Spinner Streamlit'in kendi özelliği, HTML'in üstünde görünecek
with st.spinner('Binance Futures taranıyor...'):
    # Tüm sembolleri al (Demo hız için limitliyoruz, istersen kaldır)
    all_symbols = engine.get_all_futures_symbols()
    # Hızlı olsun diye ilk 40'ı tarıyoruz. Gerçekte hepsini taratabilirsin.
    df_ema, df_sma = engine.fetch_and_analyze(all_symbols[:40])

# HTML Satırlarını Oluştur
rows_ema = generate_table_rows(df_ema, "EMA")
rows_sma = generate_table_rows(df_sma, "SMA")

# --- ANA HTML ŞABLONU ---
# Senin verdiğin kodun Streamlit'e uyarlanmış ve dinamikleştirilmiş hali.

full_html = f"""
<!DOCTYPE html>
<html class="dark" lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <style>
        /* Streamlit'in varsayılan boşluklarını sıfırla */
        .stApp {{ background-color: #101622; }}
        .block-container {{ padding: 0 !important; max-width: 100% !important; }}
        
        body {{ font-family: 'Manrope', sans-serif; background-color: #101622; color: white; }}
        
        /* Scrollbar Güzelleştirme */
        ::-webkit-scrollbar {{ width: 8px; }}
        ::-webkit-scrollbar-track {{ background: #101622; }}
        ::-webkit-scrollbar-thumb {{ background: #333; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #555; }}
    </style>
    <script>
        tailwind.config = {{
            darkMode: "class",
            theme: {{
                extend: {{
                    colors: {{
                        "primary": "#135bec",
                        "background-dark": "#101622",
                    }},
                    fontFamily: {{
                        "display": ["Manrope", "sans-serif"]
                    }}
                }}
            }}
        }}
    </script>
</head>
<body>

<div class="relative flex h-full min-h-screen w-full flex-col bg-background-dark overflow-x-hidden">
    
    <header class="flex items-center justify-between border-b border-white/10 px-6 py-4 bg-[#101622]">
        <div class="flex items-center gap-4 text-white">
            <div class="size-8 text-primary">
               <svg fill="none" viewBox="0 0 48 48" xmlns="http://www.w3.org/2000/svg">
                    <path clip-rule="evenodd" d="M24 8.18819L33.4123 11.574L24 15.2071L14.5877 11.574L24 8.18819ZM9 15.8487L21 20.4805V37.6263L9 32.9945V15.8487ZM27 37.6263V20.4805L39 15.8487V32.9945L27 37.6263Z" fill="currentColor" fill-rule="evenodd"></path>
                </svg>
            </div>
            <h2 class="text-xl font-bold tracking-tight">Kripto Tracker</h2>
        </div>
        <div class="flex items-center gap-4">
             <div class="text-sm text-neutral-400">Canlı Veri: Binance Futures</div>
             <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        </div>
    </header>

    <main class="flex-1 p-6 lg:p-10">
        
        <div class="mb-8">
            <h1 class="text-white text-3xl lg:text-4xl font-black tracking-tight mb-2">Dashboard</h1>
            <p class="text-neutral-400 text-base">Gerçek zamanlı EMA ve SMA kesişim analizi.</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
            
            <div class="flex flex-col gap-4">
                <div class="flex items-center justify-between px-2">
                    <h2 class="text-white text-xl font-bold">Above 25 EMA (1-Day)</h2>
                    <span class="bg-blue-500/20 text-blue-400 text-xs px-2 py-1 rounded-full">{len(df_ema)} Coin</span>
                </div>
                
                <div class="overflow-hidden rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead class="border-b border-white/10 bg-white/5">
                                <tr>
                                    <th class="px-4 py-3 text-neutral-400 text-xs font-bold uppercase tracking-wider">Asset</th>
                                    <th class="px-4 py-3 text-neutral-400 text-xs font-bold uppercase tracking-wider">Price</th>
                                    <th class="px-4 py-3 text-neutral-400 text-xs font-bold uppercase tracking-wider">EMA Value</th>
                                    <th class="px-4 py-3 text-neutral-400 text-xs font-bold uppercase tracking-wider">Deviation %</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-white/5">
                                {rows_ema} </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="flex flex-col gap-4">
                <div class="flex items-center justify-between px-2">
                    <h2 class="text-white text-xl font-bold">Above 50 SMA (1-Day)</h2>
                    <span class="bg-purple-500/20 text-purple-400 text-xs px-2 py-1 rounded-full">{len(df_sma)} Coin</span>
                </div>
                
                <div class="overflow-hidden rounded-xl border border-white/10 bg-white/5 backdrop-blur-sm">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead class="border-b border-white/10 bg-white/5">
                                <tr>
                                    <th class="px-4 py-3 text-neutral-400 text-xs font-bold uppercase tracking-wider">Asset</th>
                                    <th class="px-4 py-3 text-neutral-400 text-xs font-bold uppercase tracking-wider">Price</th>
                                    <th class="px-4 py-3 text-neutral-400 text-xs font-bold uppercase tracking-wider">SMA Value</th>
                                    <th class="px-4 py-3 text-neutral-400 text-xs font-bold uppercase tracking-wider">Deviation %</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-white/5">
                                {rows_sma} </tbody>
                        </table>
                    </div>
                </div>
            </div>

        </div>
    </main>
</div>

</body>
</html>
"""

# HTML'i Streamlit'e render et
# scrolling=True diyerek içeriğin taşmasını engelliyoruz
st.components.v1.html(full_html, height=1200, scrolling=True)

# Otomatik Yenileme Butonu (Streamlit native butonu, HTML dışında kalır)
# Sayfayı en alta koyuyoruz ki tasarımı bozmasın
if st.button("🔄 Verileri Yenile", key="refresh_btn"):
    st.rerun()
