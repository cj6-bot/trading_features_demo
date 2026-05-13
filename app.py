import streamlit as st
import ccxt
import time

# إعدادات الصفحة
st.set_page_config(page_title="Binance Futures Bot", layout="centered", page_icon="🤖")

st.title("🤖 بوت تداول الفيوجرز (النسخة العالمية)")
st.info("تم تعديل الروابط لتجاوز القيود الجغرافية للسيرفرات.")

# القائمة الجانبية
with st.sidebar:
    st.header("⚙️ إعدادات الاتصال")
    api_key = st.text_input("API Key", type="password")
    secret_key = st.text_input("Secret Key", type="password")
    
    st.divider()
    
    st.header("📊 إعدادات الصفقة")
    symbol = st.selectbox("اختر العملة", ["BTC/USDT", "ETH/USDT", "SOL/USDT"])
    leverage = st.slider("الرافعة المالية", 1, 20, 10)

# واجهة العرض
price_placeholder = st.empty()
status_placeholder = st.empty()

if st.button("🚀 بدء تشغيل البوت"):
    if not api_key or not secret_key:
        st.error("الرجاء إدخال المفاتيح أولاً!")
    else:
        try:
            # إعداد المنصة مع روابط مباشرة لتجاوز الحجب الجغرافي
            exchange = ccxt.binance({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {
                    'defaultType': 'future',
                    'adjustForTimeDifference': True
                }
            })
            
            # إجبار المكتبة على استخدام روابط الـ API العالمية (تجاوز حجب السيرفرات الأمريكية)
            exchange.urls['api']['public'] = 'https://fapi.binance.com/fapi/v1'
            exchange.urls['api']['private'] = 'https://fapi.binance.com/fapi/v1'
            
            st.success(f"✅ تم الاتصال بنجاح! البوت يراقب {symbol}")
            
            while True:
                # جلب السعر
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']
                
                # تحديث الشاشة
                price_placeholder.metric(label=f"سعر {symbol} الحالي", value=f"{price} USDT")
                status_placeholder.write("🔄 يتم التحديث تلقائياً كل 5 ثوانٍ...")
                
                time.sleep(5)
                
        except Exception as e:
            # عرض الخطأ بشكل مبسط
            if "451" in str(e) or "restricted" in str(e).lower():
                st.error("❌ لا تزال باينانس تحجب السيرفر. جرب استخدام مفتاح API من حساب رسمي أو تغيير الـ VPN.")
            else:
                st.error(f"❌ حدث خطأ: {str(e)}")
