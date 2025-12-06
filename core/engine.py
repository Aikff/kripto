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

    def generate_ai_comment(self, df):
        """
        ADX ve DMI kullanarak piyasa yorumu yapar.
        """
        try:
            adx_df = df.ta.adx(length=14)
            if adx_df is None: return "Veri Yetersiz", "gray"
            
            adx = adx_df['ADX_14'].iloc[-1]
            di_plus = adx_df['DMP_14'].iloc[-1]
            di_minus = adx_df['DMN_14'].iloc[-1]
            
            comment = ""
            color = "text-neutral-400" # Varsayılan gri

            # ADX Yorumu
            if adx < 20:
                comment = "⚠️ Testere (Yatay)"
                color = "text-red-400"
            elif adx < 25:
                comment = "Zayıf Trend"
                color = "text-yellow-400"
            elif adx > 50:
                comment = "🔥 Parabolik Güç"
                color = "text-green-400 font-bold"
            else:
                comment = "✅ Sağlıklı Trend"
                color = "text-green-400"

            # Yön Yorumu
            if di_plus > di_minus:
                comment += " (Boğa)"
            else:
                comment += " (Ayı)"

            return comment, color

        except:
            return "Analiz Yok", "text-neutral-500"

    def fetch_and_analyze(self, symbols, progress_bar=None):
        ema25_list = []
        sma50_list = []
        
        # Hız için ilk 40 coin (İstersen limiti kaldırıp symbols yapabilirsin)
        target_symbols = symbols[:40]

        for i, sym in enumerate(target_symbols):
            try:
                if progress_bar:
                    progress_bar.progress((i + 1) / len(target_symbols), text=f"AI Analiz Ediyor: {sym}")

                ohlcv = self.exchange.fetch_ohlcv(sym, '1d', limit=100)
                if not ohlcv or len(ohlcv) < 60: continue

                df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                
                df.ta.ema(length=25, append=True)
                df.ta.sma(length=50, append=True)

                last_row = df.iloc[-1]
                price = last_row['close']
                ema_val = last_row['EMA_25']
                sma_val = last_row['SMA_50']
                asset_name = sym.replace('/USDT', '')

                # AI Yorumunu Al
                ai_msg, ai_color = self.generate_ai_comment(df)

                # LISTE 1: EMA 25
                if price > ema_val:
                    dev = ((price - ema_val) / ema_val) * 100
                    ema25_list.append({
                        'Asset': asset_name,
                        'Price': price,
                        'Indicator': ema_val,
                        'Deviation': dev,
                        'AI_Msg': ai_msg,     # YENİ
                        'AI_Color': ai_color  # YENİ
                    })

                # LISTE 2: SMA 50
                if price > sma_val:
                    dev = ((price - sma_val) / sma_val) * 100
                    sma50_list.append({
                        'Asset': asset_name,
                        'Price': price,
                        'Indicator': sma_val,
                        'Deviation': dev,
                        'AI_Msg': ai_msg,     # YENİ
                        'AI_Color': ai_color  # YENİ
                    })

            except Exception:
                continue

        return pd.DataFrame(ema25_list), pd.DataFrame(sma50_list)
