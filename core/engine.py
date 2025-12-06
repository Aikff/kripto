# core/engine.py

import ccxt
import pandas as pd
import pandas_ta as ta
import streamlit as st
import time

class CryptoEngine:
    def __init__(self):
        # Rate Limit açık olmalı yoksa Binance 300 coinde banlar
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })

    def get_all_futures_symbols(self):
        """
        Binance Futures'daki TÜM aktif USDT paritelerini çeker.
        Filtre yok, Limit yok.
        """
        try:
            self.exchange.load_markets()
            symbols = []
            for market in self.exchange.markets.values():
                # Kriterler: USDT marjinli, Vadeli (Linear), Aktif ve Süresiz (Perpetual)
                if (market['quote'] == 'USDT' and 
                    market['linear'] == True and 
                    market['active'] == True and
                    'BUSDT' not in market['id']): # BUSD paritelerini eledik (artık kullanılmıyor)
                    symbols.append(market['symbol'])
            
            return symbols
        except Exception as e:
            print(f"Sembol listesi hatası: {e}")
            return []

    def fetch_and_analyze(self, symbols, progress_bar=None):
        """
        Verilen sembol listesini tarar ve EMA/SMA durumuna göre ayırır.
        """
        ema25_list = []
        sma50_list = []
        
        total = len(symbols)

        for i, sym in enumerate(symbols):
            try:
                # İlerleme Çubuğunu Güncelle
                if progress_bar:
                    progress_bar.progress((i + 1) / total, text=f"Taranıyor: {sym}")

                # 1 Günlük Mumlar, Son 100 veri yeterli
                ohlcv = self.exchange.fetch_ohlcv(sym, '1d', limit=100)
                
                if not ohlcv or len(ohlcv) < 60: continue

                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # İndikatör Hesaplama
                df.ta.ema(length=25, append=True) # EMA_25
                df.ta.sma(length=50, append=True) # SMA_50

                last_row = df.iloc[-1]
                price = last_row['close']
                ema_val = last_row['EMA_25']
                sma_val = last_row['SMA_50']
                
                asset_name = sym.replace('/USDT', '')

                # --- LİSTE 1: Fiyat EMA 25 ÜSTÜNDEYSE ---
                if price > ema_val:
                    dev = ((price - ema_val) / ema_val) * 100
                    ema25_list.append({
                        'Asset': asset_name,
                        'Price': price,
                        'EMA Value': ema_val,
                        'Deviation %': dev
                    })

                # --- LİSTE 2: Fiyat SMA 50 ÜSTÜNDEYSE ---
                if price > sma_val:
                    dev = ((price - sma_val) / sma_val) * 100
                    sma50_list.append({
                        'Asset': asset_name,
                        'Price': price,
                        'SMA Value': sma_val,
                        'Deviation %': dev
                    })
                
                # Render CPU'sunu boğmamak için mikrosaniye bekleme
                # time.sleep(0.05) 

            except Exception:
                continue

        # Sıralama İşlemi (En yüksek sapma en üstte)
        df_ema = pd.DataFrame(ema25_list)
        if not df_ema.empty:
            df_ema = df_ema.sort_values(by='Deviation %', ascending=False)

        df_sma = pd.DataFrame(sma50_list)
        if not df_sma.empty:
            df_sma = df_sma.sort_values(by='Deviation %', ascending=False)

        return df_ema, df_sma
