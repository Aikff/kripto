# main.py

import streamlit as st
import pandas as pd
from core.engine import CryptoEngine

st.set_page_config(layout="wide", page_title="AI Kripto Tracker", page_icon="🧠")

# --- HTML SATIR OLUŞTURUCU ---
def generate_table_rows(df):
    html_rows = ""
    if df.empty:
        return """<tr><td colspan="5" class="px-4 py-3 text-neutral-400 text-center">Veri bulunamadı...</td></tr>"""

    df = df.sort_values(by='Deviation', ascending=False)

    for index, row in df.iterrows():
        asset = row['Asset']
        price = f"${row['Price']:,.4f}"
        ind_val = f"${row['Indicator']:,.4f}"
        dev = f"+{row['Deviation']:.2f}%"
        ai_msg = row['AI_Msg']
        ai_color = row['AI_Color']
        
        # Avatar Rengi (Random hissi versin diye isme göre)
        initial = asset[0]
        
        row_html = f"""
        <tr class="hover:bg-white/5 transition-colors border-b border-white/5 last:border-0">
            <td class="px-4 py-3">
                <div class="flex items-center gap-3">
                    <div class="flex items-center justify-center w-8 h-8 rounded-full bg-blue-600/20 text-blue-400 border border-blue-500/30 font-bold text-xs">
                        {initial}
                    </div>
                    <div class="text-white text-sm font-medium">{asset}</div>
                </div>
            </td>
            <td class="px-4 py-3 text-white text-sm">{price}</td>
            <td class="px-4 py-3 text-neutral-400 text-sm">{ind_val}</td>
            <td class="px-4 py-3">
                <span class="inline-flex items-center rounded-md bg-green-500/10 px-2 py-1 text-xs font-medium text-green-400 ring-1 ring-inset ring-green-500/20">
                    {dev}
                </span>
            </td>
            <td class="px-4 py-3 text-sm font-medium {ai_color}">
                {ai_msg}
            </td>
        </tr>
        """
        html_rows += row_html
    return html_rows

# --- VERİ ÇEKME ---
engine = CryptoEngine()
with st.spinner('Yapay Zeka Piyasayı Tarıyor...'):
    all_symbols = engine.get_all_futures_symbols()
    df_ema, df_sma = engine.fetch_and_analyze(all_symbols[:50]) # İlk 50 (Demo)

rows_ema = generate_table_rows(df_ema)
rows_sma = generate_table_rows(df_sma)

# --- HTML ŞABLONU ---
full_html = f"""
<!DOCTYPE html>
<html class="dark" lang="en">
<head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap" rel="stylesheet"/>
    <style>
        .stApp {{ background-color: #101622; }}
        body {{ font-family: 'Manrope', sans-serif; background-color: #101622; color: white; }}
        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-track {{ background: #101622; }}
        ::-webkit-scrollbar-thumb {{ background: #333; border-radius: 3px; }}
    </style>
</head>
<body>

<div class="relative flex h-full min-h-screen w-full flex-col bg-[#101622] overflow-x-hidden">
    
    <header class="flex items-center justify-between border-b border-white/10 px-6 py-4 bg-[#101622]">
        <div class="flex items-center gap-4 text-white">
            <h2 class="text-xl font-bold tracking-tight text-white">AI Kripto Tracker</h2>
        </div>
        <div class="flex items-center gap-2">
             <div class="text-xs text-neutral-500">Powered by ADX/DMI Engine</div>
             <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
        </div>
    </header>

    <main class="flex-1 p-4 lg:p-8">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            <div class="flex flex-col gap-4">
                <div class="flex items-center justify-between px-1">
                    <h2 class="text-white text-lg font-bold">Above 25 EMA (1-Day)</h2>
                    <span class="bg-blue-500/10 text-blue-400 text-xs px-2 py-1 rounded-full">{len(df_ema)} Coin</span>
                </div>
                <div class="overflow-hidden rounded-xl border border-white/10 bg-white/5">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead class="border-b border-white/10 bg-white/5">
                                <tr>
                                    <th class="px-4 py-3 text-neutral-500 text-xs font-bold uppercase">Asset</th>
                                    <th class="px-4 py-3 text-neutral-500 text-xs font-bold uppercase">Price</th>
                                    <th class="px-4 py-3 text-neutral-500 text-xs font-bold uppercase">EMA</th>
                                    <th class="px-4 py-3 text-neutral-500 text-xs font-bold uppercase">Dev %</th>
                                    <th class="px-4 py-3 text-neutral-500 text-xs font-bold uppercase">AI Analiz</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-white/5">
                                {rows_ema}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="flex flex-col gap-4">
                <div class="flex items-center justify-between px-1">
                    <h2 class="text-white text-lg font-bold">Above 50 SMA (1-Day)</h2>
                    <span class="bg-purple-500/10 text-purple-400 text-xs px-2 py-1 rounded-full">{len(df_sma)} Coin</span>
                </div>
                <div class="overflow-hidden rounded-xl border border-white/10 bg-white/5">
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead class="border-b border-white/10 bg-white/5">
                                <tr>
                                    <th class="px-4 py-3 text-neutral-500 text-xs font-bold uppercase">Asset</th>
                                    <th class="px-4 py-3 text-neutral-500 text-xs font-bold uppercase">Price</th>
                                    <th class="px-4 py-3 text-neutral-500 text-xs font-bold uppercase">SMA</th>
                                    <th class="px-4 py-3 text-neutral-500 text-xs font-bold uppercase">Dev %</th>
                                    <th class="px-4 py-3 text-neutral-500 text-xs font-bold uppercase">AI Analiz</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-white/5">
                                {rows_sma}
                            </tbody>
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

st.components.v1.html(full_html, height=1200, scrolling=True)

if st.button("🔄 Verileri Yenile"):
    st.rerun()
