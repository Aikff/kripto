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

    def get_all_futures_symbols(self):
        try:
            self.exchange.load_markets()
            symbols = []
            for market in self.exchange.markets.values():
                if (market['quote'] == 'USDT' and 
                    market['linear'] == True and 
                    market['active'] == True and
                    'BUSDT' not in market['id']):
                    symbols.append(market['symbol'])
            return symbols
        except:
            return []

    def fetch_and_analyze(self, symbols, progress_bar=None):
        ema25_list = []
        sma50_list = []
        total = len(symbols)

        # Hız için şimdilik limitli tarama yapalım veya 
        # tümünü taramak istersen burayı açabilirsin.
        # Demo olduğu için ilk 50 coini tarıyoruz:
        target_symbols = symbols[:50] 

        for i, sym in enumerate(target_symbols):
            try:
                if progress_bar:
                    progress_bar.progress((i + 1) / len(target_symbols), text=f"Analyzing: {sym}")

                ohlcv = self.exchange.fetch_ohlcv(sym, '1d', limit=100)
                if not ohlcv: continue

                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                df.ta.ema(length=25, append=True)
                df.ta.sma(length=50, append=True)

                last_row = df.iloc[-1]
                price = last_row['close']
                ema_val = last_row['EMA_25']
                sma_val = last_row['SMA_50']
                asset_name = sym.replace('/USDT', '')

                # LISTE 1: EMA 25
                if price > ema_val:
                    dev = ((price - ema_val) / ema_val) * 100
                    ema25_list.append({
                        'Asset': asset_name,
                        'Price': price,
                        'Indicator': ema_val,
                        'Deviation': dev
                    })

                # LISTE 2: SMA 50
                if price > sma_val:
                    dev = ((price - sma_val) / sma_val) * 100
                    sma50_list.append({
                        'Asset': asset_name,
                        'Price': price,
                        'Indicator': sma_val,
                        'Deviation': dev
                    })

            except Exception:
                continue

        return pd.DataFrame(ema25_list), pd.DataFrame(sma50_list)
