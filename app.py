import streamlit as st
import ccxt
import pandas as pd
import time
from datetime import datetime

# 1. إعدادات الواجهة
st.set_page_config(page_title="Whale Logic Sniper 2026", layout="wide")
st.title("🐋 بوت صيد الحيتان: نظام الـ 10 مؤشرات")

# 2. القائمة الجانبية (هنا السلايدر!)
with st.sidebar:
    st.header("🔑 إعدادات API")
    api_key = st.text_input("API Key", type="password").strip()
    secret_key = st.text_input("Secret Key", type="password").strip()
    
    st.markdown("---")
    st.header("⚙️ استراتيجية السكالبينج")
    
    # السلايدر لاختيار قوة الإشارة (عدد المؤشرات)
    min_signals = st.slider("عدد المؤشرات المطلوبة (التصويت)", min_value=1, max_value=10, value=7)
    
    leverage = st.number_input("الرافعة المالية", value=50)
    trade_amount = st.number_input("مبلغ الدخول (Margin) $", value=1000.0)
    
    st.info(f"💡 البوت ماراح يفتح إلا إذا اتفقوا {min_signals} مؤشرات.")
    run_bot = st.toggle("إطلاق المحرك العملاق 🚀")

# 3. دالة حساب المؤشرات الـ 10
def get_advanced_signals(exchange, symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=50)
    df = pd.DataFrame(ohlcv, columns=['ts', 'open', 'high', 'low', 'close', 'volume'])
    
    signals = 0
    current_price = df['close'].iloc[-1]
    
    # مؤشرات تجريبية (للتوضيح)
    ema9 = df['close'].ewm(span=9).mean().iloc[-1]
    ema21 = df['close'].ewm(span=21).mean().iloc[-1]
    if ema9 > ema21: signals += 2 # تقاطع الاتجاه
    
    avg_vol = df['volume'].mean()
    if df['volume'].iloc[-1] > avg_vol * 1.5: signals += 3 # حركة حيتان
    
    # إضافة بقية المؤشرات لتمثيل الـ 10 أصوات
    if current_price > df['open'].iloc[-1]: signals += 2
    if df['close'].iloc[-1] > df['close'].iloc[-2]: signals += 3
    
    return signals, current_price

# 4. المحرك الأساسي
if run_bot:
    if not (api_key and secret_key):
        st.error("❌ حبيبي وين المفاتيح؟")
    else:
        try:
            exchange = ccxt.gateio({'apiKey': api_key, 'secret': secret_key})
            exchange.set_sandbox_mode(True) 
            
            st.success(f"✅ الرادار شغال.. السلايدر مضبوط على {min_signals} مؤشرات.")
            placeholder = st.empty()
            
            while True:
                symbol = "BTC_USDT"
                total_score, price = get_advanced_signals(exchange, symbol)
                
                with placeholder.container():
                    st.metric("السعر الحالي", f"${price}")
                    st.write(f"📈 نتيجة تصويت المؤشرات: {total_score} من 10")
                    
                    if total_score >= min_signals:
                        st.balloons()
                        # حساب الكمية الحقيقية (الـ 1000 دولار)
                        qty = int((trade_amount * leverage) / price)
                        if qty < 1: qty = 1
                        
                        # أهداف منطقية 1.5% و 0.5% (نسبة 1:3)
                        tp_price = price * 1.015
                        sl_price = price * 0.995
                        
                        st.success(f"🔥 تم رصد إشارة! الكمية: {qty} | الهدف: {tp_price:.2f}")
                        # هنا يوضع أمر التنفيذ الحقيقي
                        break 

                time.sleep(10)
                st.rerun()
        except Exception as e:
            st.error(f"🛑 خطأ: {e}")
