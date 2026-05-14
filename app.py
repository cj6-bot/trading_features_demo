import streamlit as st
import ccxt
import pandas as pd
import time
from datetime import datetime

# 1. إعدادات الواجهة الأساسية
st.set_page_config(page_title="Whale Hunter Pro 2026", layout="wide")
st.title("🐋 محرك الحيتان: النسخة الاحترافية (Server-Side TP/SL)")
st.subheader("تحليل فريم (1H) وتنفيذ (1M) - رافعة 100x - نظام تصويت 10 مؤشرات")

# 2. القائمة الجانبية (إعدادات المستخدم)
with st.sidebar:
    st.header("🔑 مفاتيح API")
    api_key = st.text_input("API Key", type="password").strip()
    secret_key = st.text_input("Secret Key", type="password").strip()
    
    st.markdown("---")
    st.header("⚙️ إعدادات الاستراتيجية")
    symbol = st.selectbox("الزوج", ["BTC_USDT", "ETH_USDT", "SOL_USDT"])
    min_signals = st.slider("قوة الإشارة (عدد المؤشرات)", 1, 10, 7)
    leverage = st.number_input("الرافعة المالية", value=100) # تم ضبطها على 100 كما طلبت
    trade_amount = st.number_input("مبلغ الدخول (Margin) $", value=1000.0)
    
    st.info(f"💡 سيتم إرسال الأهداف تلقائياً لسيرفر المنصة لضمان السرعة (Latency)")
    run_bot = st.toggle("تشغيل الرادار الآن ⚡")

# 3. دالة تحليل المؤشرات (نظام التصويت)
def get_advanced_signals(exchange, symbol):
    # جلب بيانات فريم الدقيقة
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=100)
    df = pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
    
    signals = 0
    current_price = df['close'].iloc[-1]
    
    # --- توزيع الأصوات (10 أصوات) ---
    # 1. رادار الحيتان (حجم التداول)
    avg_vol = df['volume'].mean()
    if df['volume'].iloc[-1] > avg_vol * 1.5: signals += 3 # الحيتان لها ثقل أكبر
    
    # 2. تقاطع المتوسطات EMA
    ema9 = df['close'].ewm(span=9).mean().iloc[-1]
    ema21 = df['close'].ewm(span=21).mean().iloc[-1]
    if ema9 > ema21: signals += 2
    
    # 3. الزخم RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rsi = 100 - (100 / (1 + (gain/loss))).iloc[-1]
    if 40 < rsi < 70: signals += 1
    
    # 4. الماكد MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    macd = (exp1 - exp2).iloc[-1]
    if macd > 0: signals += 2
    
    # 5. اتجاه السعر الفوري
    if current_price > df['open'].iloc[-1]: signals += 2
    
    return signals, current_price

# 4. المحرك التنفيذي
if run_bot:
    if not (api_key and secret_key):
        st.error("❌ يرجى إدخال مفاتيح API أولاً")
    else:
        try:
            exchange = ccxt.gateio({
                'apiKey': api_key, 'secret': secret_key,
                'enableRateLimit': True, 'options': {'defaultType': 'swap'}
            })
            exchange.set_sandbox_mode(True) # وضع التجريب

            st.success(f"🚀 الرادار يراقب {symbol} الآن...")
            placeholder = st.empty()
            
            while True:
                total_score, price = get_advanced_signals(exchange, symbol)
                
                with placeholder.container():
                    st.metric("السعر الحالي", f"${price}")
                    st.write(f"📊 نتيجة تصويت المؤشرات: {total_score} من 10")
                    
                    if total_score >= min_signals:
                        st.balloons()
                        # حساب الكمية الحقيقية (الـ 1000$ مع الرافعة)
                        qty = int((trade_amount * leverage) / price)
                        if qty < 1: qty = 1
                        
                        # حساب الأهداف (1:3 Risk Ratio)
                        tp_price = price * 1.015  # هدف 1.5%
                        sl_price = price * 0.995  # وقف 0.5%
                        
                        # أ. فتح الصفقة ماركت
                        exchange.set_leverage(leverage, symbol)
                        order = exchange.create_market_buy_order(symbol, qty)
                        st.success(f"🔥 تم فتح الصفقة! الكمية: {qty} عقد")
                        
                        # ب. إرسال أمر التيك بروفيت للسيرفر (Limit)
                        exchange.create_order(symbol, 'limit', 'sell', qty, tp_price, {'reduce_only': True})
                        st.info(f"🎯 الهدف ثُبت في المنصة: {tp_price:.2f}")
                        
                        # ج. إرسال أمر الستوب لوز للسيرفر (Stop Market)
                        exchange.create_order(symbol, 'stop_market', 'sell', qty, params={'stopPrice': sl_price, 'reduce_only': True})
                        st.warning(f"🛑 الوقف ثُبت في المنصة: {sl_price:.2f}")
                        
                        break # توقف لمراقبة النتيجة

                time.sleep(10)
                st.rerun()

        except Exception as e:
            st.error(f"🛑 خطأ في الاتصال: {e}")
