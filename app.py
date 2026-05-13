import streamlit as st
import ccxt
import time

# إعدادات الصفحة الاحترافية
st.set_page_config(page_title="Binance Futures Bot", layout="centered", page_icon="🤖")

st.title("🤖 بوت تداول الفيوجرز (نسخة المتصفح)")
st.info("هذه الواجهة مخصصة للعمل على حساب Testnet (الديمو) لضمان الأمان.")

# القائمة الجانبية لإدخال المفاتيح والإعدادات
with st.sidebar:
    st.header("⚙️ إعدادات الاتصال")
    api_key = st.text_input("API Key", type="password", help="أدخل مفتاح الـ API الخاص بـ Binance Testnet")
    secret_key = st.text_input("Secret Key", type="password", help="أدخل الـ Secret Key الخاص بك")
    
    st.divider()
    
    st.header("📊 إعدادات الصفقة")
    symbol = st.selectbox("اختر العملة", ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT"])
    leverage = st.slider("الرافعة المالية (Leverage)", 1, 20, 10)
    
    st.divider()
    st.write("بواسطة: تداول متميز 🚀")

# واجهة العرض الرئيسية للسعر والحالة
col1, col2 = st.columns(2)
with col1:
    price_placeholder = st.empty()
with col2:
    balance_placeholder = st.empty()

status_placeholder = st.empty()

# زر التشغيل
if st.button("🚀 بدء تشغيل البوت"):
    if not api_key or not secret_key:
        st.error("الرجاء إدخال الـ API Key والـ Secret Key أولاً!")
    else:
        try:
            # ربط المنصة عبر مكتبة CCXT
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {'defaultType': 'future'}
            })
            exchange.set_sandbox_mode(True) # تفعيل وضع الديمو (Testnet)
            
            st.success(f"✅ تم الاتصال بنجاح! البوت يراقب {symbol} الآن...")
            
            # حلقة التحديث المستمر
            while True:
                # جلب السعر الحالي
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']
                
                # جلب الرصيد
                balance = exchange.fetch_balance()
                usdt_balance = balance['total'].get('USDT', 0)
                
                # تحديث العرض على الشاشة
                price_placeholder.metric(label=f"سعر {symbol}", value=f"{price} USDT")
                balance_placeholder.metric(label="رصيد USDT (Testnet)", value=f"{usdt_balance:.2f}")
                
                # منطقة الاستراتيجية (مثال بسيط للتدريب)
                status_placeholder.write("🔄 البوت في وضع المراقبة المستمرة...")
                
                # تأخير 5 ثواني قبل التحديث القادم
                time.sleep(5)
                
        except Exception as e:
            st.error(f"❌ حدث خطأ: {str(e)}")
