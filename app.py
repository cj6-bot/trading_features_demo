import streamlit as st
import MetaTrader5 as mt5
import pandas as pd
import time
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="Gold MT5 Terminal", layout="wide")
st.title("🏆 منصة تداول الذهب الآلية (MT5 + Streamlit)")

# تعريف السجل في الجلسة
if 'trade_log' not in st.session_state:
    st.session_state.trade_log = []

# القائمة الجانبية للإعدادات القوية
with st.sidebar:
    st.header("⚙️ إعدادات الذهب")
    symbol = st.text_input("رمز الذهب (تأكد من البرنامج)", value="XAUUSD")
    lot_size = st.number_input("حجم اللوت (أعلى رافعة)", min_value=0.01, value=1.0, step=0.1)
    
    st.markdown("---")
    st.header("📈 المؤشرات والإضافات")
    use_rsi = st.checkbox("تفعيل مؤشر RSI", value=True)
    use_ema = st.checkbox("تفعيل مؤشر EMA 200", value=True)
    
    st.markdown("---")
    auto_trade = st.toggle("إطلاق المحرك التلقائي 🚀")
    
    if st.button("🚨 إغلاق جميع صفقات الذهب"):
        st.warning("جاري إغلاق المراكز...")

# دالة فتح الصفقات
def send_gold_order(order_type):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None
    
    price = tick.ask if order_type == mt5.ORDER_TYPE_BUY else tick.bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot_size),
        "type": order_type,
        "price": price,
        "magic": 123456,
        "comment": "Gold Sniper Streamlit",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    return mt5.order_send(request)

# المحرك الأساسي
if auto_trade:
    if not mt5.initialize():
        st.error(f"❌ فشل الاتصال بـ MT5. تأكد أن البرنامج مفتوح! الخطأ: {mt5.last_error()}")
    else:
        # جلب معلومات الحساب
        acc = mt5.account_info()
        col1, col2, col3 = st.columns(3)
        col1.metric("الرصيد", f"${acc.balance}")
        col2.metric("الأسهم (Equity)", f"${acc.equity}")
        col3.metric("الرافعة المتاحة", f"1:{acc.leverage}")

        # عرض الأسعار الحية
        price_spot = st.empty()
        
        while True:
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                with price_spot.container():
                    st.subheader(f"🪙 سعر الذهب المباشر: {tick.bid}")
                    
                # محاكاة عمل المؤشرات القوية (هنا نضع شروط الدخول)
                # مثال: تنفيذ صفقة شراء عند استيفاء الشروط
                res = send_gold_order(mt5.ORDER_TYPE_BUY)
                
                now = datetime.now().strftime("%H:%M:%S")
                if res and res.retcode == mt5.TRADE_RETCODE_DONE:
                    st.session_state.trade_log.append(f"[{now}] ✅ تم فتح صفقة ذهب بلوت {lot_size}")
                else:
                    st.session_state.trade_log.append(f"[{now}] ⚠️ خطأ في التنفيذ: {res.comment if res else 'No Tick'}")

                # عرض سجل العمليات
                st.markdown("---")
                st.subheader("📋 سجل عمليات البوت الحية")
                for log in reversed(st.session_state.trade_log[-10:]):
                    st.write(log)

            time.sleep(30) # تحديث كل 30 ثانية
            st.rerun()

else:
    mt5.shutdown()
    st.info("المحرك متوقف. البرنامج جاهز للانطلاق من القائمة الجانبية.")
