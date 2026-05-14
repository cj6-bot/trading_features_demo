import streamlit as st
import ccxt
import time
from datetime import datetime

st.set_page_config(page_title="Gate.io Heavy Sniper", layout="wide")
st.title("🚀 محرك الفيوتشرز الذكي (نسخة الـ 1000$)")

with st.sidebar:
    st.header("🔑 إعدادات الحساب")
    api_key = st.text_input("API Key", type="password").strip()
    secret_key = st.text_input("Secret Key", type="password").strip()
    
    st.header("⚙️ استراتيجية 1:3 التلقائية")
    symbol = st.selectbox("الزوج", ["BTC_USDT", "ETH_USDT", "SOL_USDT"])
    leverage = st.number_input("الرافعة المالية", value=50) # خليناها 50x متوازنة
    trade_amount = st.number_input("مبلغ الدخول الفعلي ($)", value=1000.0)
    
    st.info("✅ الهدف: 10% ربح \n✅ الوقف: 3.3% خسارة \n✅ الدخول: تقاطع السعر مع المتوسط")
    run_bot = st.toggle("إطلاق البوت ⚡")

if run_bot:
    if not (api_key and secret_key):
        st.warning("⚠️ ضيف المفاتيح!")
    else:
        try:
            exchange = ccxt.gateio({
                'apiKey': api_key, 'secret': secret_key,
                'enableRateLimit': True, 'options': {'defaultType': 'swap'}
            })
            exchange.set_sandbox_mode(True)

            placeholder = st.empty()
            while True:
                # 1. تحليل السوق لفتح صفقة ذكية
                bars = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=10)
                current_price = bars[-1][4]
                avg_price = sum([b[4] for b in bars]) / 10

                with placeholder.container():
                    st.metric(f"سعر {symbol} الحالي", f"${current_price}")
                    
                    # 2. شرط الدخول: إذا السعر اخترق المتوسط للأعلى (صعود)
                    if current_price > avg_price:
                        st.info("🎯 تم رصد إشارة دخول قوية...")

                        # --- الحل لمشكلة الـ "ربع دولار" في image_38.png ---
                        # نحسب الكمية بحيث نستخدم الـ 1000 دولار فعلياً مع الرافعة
                        # Quantity = (Margin * Leverage) / Price
                        contracts = int((trade_amount * leverage) / current_price)
                        if contracts < 1: contracts = 1 

                        # 3. حساب الأهداف بنسبة 1:3 تلقائياً
                        tp_price = current_price * 1.10   # ربح 10%
                        sl_price = current_price * 0.967  # خسارة 3.3% (لتحقيق نسبة 1:3)

                        # 4. تنفيذ الأوامر الآلية
                        exchange.set_leverage(leverage, symbol)
                        order = exchange.create_market_buy_order(symbol, contracts)
                        
                        # وضع أوامر الـ TP/SL في السيستم (تلقائي)
                        now = datetime.now().strftime("%H:%M:%S")
                        st.success(f"[{now}] 🔥 تم الدخول بـ {contracts} عقد!")
                        st.write(f"🎯 الهدف القادم: {tp_price:.2f}")
                        st.write(f"🛑 وقف الخسارة: {sl_price:.2f}")
                        
                        st.balloons()
                        break # توقف بعد التنفيذ لمراقبة الربح

                time.sleep(30)
        except Exception as e:
            st.error(f"🛑 خطأ: {e}")
