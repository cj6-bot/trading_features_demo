import streamlit as st
import MetaTrader5 as mt5
import time
from datetime import datetime

st.set_page_config(page_title="Gold Sniper MT5", layout="wide")
st.title("🏆 بوت الذهب - رافعة مالية قصوى")

# القائمة الجانبية
with st.sidebar:
    st.header("⚙️ إعدادات الذهب")
    # تأكد من كتابة الرمز كما هو في برنامجك (GOLD أو XAUUSD)
    symbol = st.text_input("رمز الذهب", value="XAUUSD")
    lot_size = st.number_input("حجم اللوت (أعلى لوت)", min_value=0.01, value=1.0, step=0.1)
    
    st.markdown("---")
    run_bot = st.toggle("إطلاق المحرك الآن 🚀")
    if st.button("🚨 إغلاق جميع الصفقات فوراً"):
        st.session_state.force_close = True

# دالة فتح صفقة ذهب
def trade_gold(type):
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return None
    
    price = tick.ask if type == mt5.ORDER_TYPE_BUY else tick.bid
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": float(lot_size),
        "type": type,
        "price": price,
        "magic": 999999,
        "comment": "Gold Sniper",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    return mt5.order_send(request)

if run_bot:
    if not mt5.initialize():
        st.error("❌ افتح برنامج MT5 أولاً!")
    else:
        # عرض بيانات الحساب والرافعة
        acc = mt5.account_info()
        st.success(f"✅ متصل بحساب: {acc.login} | الرافعة المالية: 1:{acc.leverage}")
        
        col1, col2 = st.columns(2)
        price_area = col1.empty()
        log_area = col2.empty()

        while True:
            tick = mt5.symbol_info_tick(symbol)
            if tick:
                price_area.metric("سعر الذهب الحالي 🪙", f"${tick.bid}")
                
                # تنفيذ صفقة كل دقيقة (أو حسب استراتيجيتك)
                res = trade_gold(mt5.ORDER_TYPE_BUY)
                
                now = datetime.now().strftime("%H:%M:%S")
                if res and res.retcode == mt5.TRADE_RETCODE_DONE:
                    st.toast(f"✅ تم دخول صفقة ذهب بلوت {lot_size}!")
                    with log_area:
                        st.write(f"[{now}] 💰 دخلنا صفقة شراء.. انطلق!")
                else:
                    with log_area:
                        st.write(f"[{now}] ⚠️ فشل الدخول (تأكد من الرافعة والرصيد)")

            time.sleep(60) 
            st.rerun()
else:
    mt5.shutdown()
    st.info("المحرك بانتظار إشارة الانطلاق..")
