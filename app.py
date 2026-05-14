import streamlit as st
import ccxt
import time
from datetime import datetime

st.set_page_config(page_title="Gate.io Futures Sniper", layout="wide")
st.title("🚀 بوت Gate.io للفيوتشرز - نسخة السحاب")

with st.sidebar:
    st.header("🔑 مفاتيح Gate.io Testnet")
    api_key = st.text_input("API Key", type="password").strip()
    secret_key = st.text_input("Secret Key", type="password").strip()
    
    st.header("⚙️ إعدادات الفيوتشرز")
    # الرموز في Gate.io فيوتشرز تكون بصيغة BTC_USDT
    symbol = st.selectbox("الزوج", ["BTC_USDT", "ETH_USDT", "SOL_USDT"])
    leverage = st.slider("الرافعة المالية", 1, 100, 10)
    trade_amount = st.number_input("مبلغ الدخول ($)", min_value=1.0, value=10.0)
    
    st.markdown("---")
    run_bot = st.toggle("إطلاق المحرك الآن 🚀")

if run_bot:
    if not (api_key and secret_key):
        st.warning("⚠️ أدخل المفاتيح أولاً!")
    else:
        try:
            # إعداد الاتصال بـ Gate.io Futures Testnet
            exchange = ccxt.gateio({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {'defaultType': 'swap'} 
            })
            
            # تفعيل وضع الساندبوكس (الديمو)
            exchange.set_sandbox_mode(True)

            # جلب الرصيد للتأكد من الاتصال
            balance = exchange.fetch_balance()
            st.success("✅ متصل بنجاح بسيرفر الفيوتشرز!")

            placeholder = st.empty()
            
            while True:
                with placeholder.container():
                    ticker = exchange.fetch_ticker(symbol)
                    price = ticker['last']
                    st.metric(f"سعر {symbol} الحالي", f"${price}")
                    
                    # حساب الكمية (Size)
                    # ملاحظة: العقود في الفيوتشرز تحسب بالـ Contract Size
                    amount = trade_amount / price
                    
                    try:
                        # تنفيذ صفقة شراء ماركت
                        order = exchange.create_market_buy_order(symbol, amount)
                        now = datetime.now().strftime("%H:%M:%S")
                        st.success(f"[{now}] 🎯 تم فتح مركز فيوتشرز بنجاح!")
                    except Exception as e_trade:
                        st.error(f"⚠️ خطأ بالتداول: {e_trade}")

                time.sleep(30)
                st.rerun()

        except Exception as e:
            st.error(f"🛑 خطأ اتصال: {e}")
else:
    st.info("المحرك بانتظار إشارة البدء..")
