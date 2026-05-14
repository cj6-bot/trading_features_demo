import streamlit as st
import ccxt
import time
from datetime import datetime

# إعدادات الصفحة
st.set_page_config(page_title="OKX Crypto Sniper", layout="wide")
st.title("🤖 بوت OKX للكريبتو - نسخة المحترفين")

with st.sidebar:
    st.header("🔑 مفاتيح OKX Demo")
    api_key = st.text_input("API Key", type="password")
    secret_key = st.text_input("Secret Key", type="password")
    passphrase = st.text_input("Passphrase", type="password") # OKX تطلب كلمة مرور للمفتاح
    
    st.header("⚙️ إعدادات الصفقات")
    symbol = st.selectbox("العملة", ["BTC/USDT:USDT", "ETH/USDT:USDT", "SOL/USDT:USDT"])
    leverage = st.slider("الرافعة المالية", 1, 100, 20)
    trade_amount = st.number_input("مبلغ الدخول ($)", min_value=10.0, value=50.0)
    
    st.markdown("---")
    run_bot = st.toggle("إطلاق المحرك الآن 🚀")

if run_bot:
    if not (api_key and secret_key and passphrase):
        st.error("❌ لازم تضيف الـ API Key والـ Secret والـ Passphrase!")
    else:
        try:
            # الربط بحساب الـ Demo في OKX
            exchange = ccxt.okx({
                'apiKey': api_key,
                'secret': secret_key,
                'password': passphrase,
                'enableRateLimit': True,
                'options': {'defaultType': 'swap'} # للتداول بالعقود الدائمة
            })
            
            # تفعيل وضع التجريبي (Demo Mode)
            exchange.set_sandbox_mode(True) 

            # جلب الرصيد
            balance = exchange.fetch_balance()
            st.success("✅ تم الاتصال بنجاح بـ OKX Demo")
            
            col1, col2 = st.columns(2)
            col1.metric("الرصيد المتاح USDT", f"{balance.get('USDT', {}).get('free', 0)}")

            while True:
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']
                
                # حساب الكمية (Quantity)
                qty = (trade_amount * leverage) / price
                
                # تنفيذ صفقة شراء (Market Order)
                try:
                    order = exchange.create_market_buy_order(symbol, qty)
                    now = datetime.now().strftime("%H:%M:%S")
                    st.toast(f"🚀 تم الدخول بصفقة {symbol} بسعر {price}")
                    st.write(f"[{now}] ✅ تم تنفيذ صفقة شراء للعملة {symbol}")
                except Exception as e_trade:
                    st.error(f"⚠️ فشل الدخول: {e_trade}")

                time.sleep(60)
                st.rerun()

        except Exception as e:
            st.error(f"🛑 خطأ في الاتصال: {e}")
else:
    st.info("بانتظار إشارة الانطلاق على OKX!")
