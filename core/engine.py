# core/engine.py

import ccxt
import pandas as pd
import pandas_ta as ta

class CryptoEngine:
    def __init__(self):
        self.exchange = ccxt.binance({
            'enableRateLimit': True,
            'options': {'defaultType': 'future'}
        })

    def get_top_volume_coins(self, limit=50):
        """Hacmi en yüksek 50 vadeli coini getirir"""
        try:
            self.exchange.load_markets()
            tickers = self.exchange.fetch_tickers()
            # USDT paritelerini filtrele
            valid = {k: v for k, v in tickers.items() if '/USDT' in k and 'BUSDT' not in k}
            # Hacme göre sırala
            sorted_tickers = sorted(valid.values(), key=lambda x: x['quoteVolume'], reverse=True)
            return [t['symbol'] for t in sorted_tickers[:limit]]
        except:
            return []

    def fetch_and_analyze(self, symbols):
        """
        Tüm coinleri tek seferde tarar ve iki liste oluşturur:
        1. EMA 25 Üstünde olanlar
        2. SMA 50 Üstünde olanlar
        """
        ema25_list = []
        sma50_list = []

        print(f"📡 {len(symbols)} Coin Taranıyor (1D Timeframe)...")

        for sym in symbols:
            try:
                # Günlük mumlar, son 100 mum yeterli
                ohlcv = self.exchange.fetch_ohlcv(sym, '1d', limit=100)
                if not ohlcv: continue

                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                # İndikatörleri Hesapla
                # 1. EMA 25
                df.ta.ema(length=25, append=True)
                # 2. SMA 50
                df.ta.sma(length=50, append=True)

                last_row = df.iloc[-1]
                price = last_row['close']
                ema_val = last_row['EMA_25']
                sma_val = last_row['SMA_50']

                # --- LİSTE 1: EMA 25 ÜZERİNDE OLANLAR ---
                if price > ema_val:
                    dev = ((price - ema_val) / ema_val) * 100
                    ema25_list.append({
                        'Asset': sym.replace('/USDT', ''),
                        'Price': price,
                        'EMA Value': ema_val,
                        'Deviation %': dev
                    })

                # --- LİSTE 2: SMA 50 ÜZERİNDE OLANLAR ---
                if price > sma_val:
                    dev = ((price - sma_val) / sma_val) * 100
                    sma50_list.append({
                        'Asset': sym.replace('/USDT', ''),
                        'Price': price,
                        'SMA Value': sma_val,
                        'Deviation %': dev
                    })

            except Exception as e:
                continue

        # Dataframe'e çevir ve Sapma oranına göre sırala (En yüksek en üstte)
        df_ema = pd.DataFrame(ema25_list)
        if not df_ema.empty:
            df_ema = df_ema.sort_values(by='Deviation %', ascending=False)

        df_sma = pd.DataFrame(sma50_list)
        if not df_sma.empty:
            df_sma = df_sma.sort_values(by='Deviation %', ascending=False)

        return df_ema, df_sma