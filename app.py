import streamlit as st
import ccxt
import time
from datetime import datetime
import requests

# 1. إعدادات الصفحة والواجهة
st.set_page_config(page_title="Gate.io Pro Sniper 2026", layout="wide")
st.title("🚀 المحرك النهائي: Gate.io Futures")

# وظيفة لجلب الـ IP (احتياطاً لحل مشاكل الاتصال)
def get_my_ip():
    try:
        return requests.get('https://api.ipify.org').text
    except:
        return "تعذر جلب الـ IP"

# 2. القائمة الجانبية لإدخال البيانات
if 'trade_log' not in st.session_state:
    st.session_state.trade_log = []

with st.sidebar:
    st.header("🔑 مفاتيح Gate.io Testnet")
    api_key = st.text_input("API Key", type="password").strip()
    secret_key = st.text_input("Secret Key", type="password").strip()
    
    st.info(f"🌐 IP جهازك: `{get_my_ip()}`")
    
    st.header("⚙️ إعدادات الصفقات")
    # الذهب في العملات المشفرة يسمى غالباً PAXG أو رموز مشابهة، لكن سنبقى على BTC للضمان
    symbol = st.selectbox("الزوج (Futures)", ["BTC_USDT", "ETH_USDT", "SOL_USDT"])
    leverage = st.slider("الرافعة المالية (Leverage)", 1, 100, 20)
    trade_amount = st.number_input("مبلغ الدخول للصفقة ($)", min_value=1.0, value=100.0)
    
    st.markdown("---")
    st.header("🛡️ إدارة المخاطر (التلقائية)")
    tp = st.number_input("أخذ الربح % (Take Profit)", value=10.0)
    sl = st.number_input("وقف الخسارة % (Stop Loss)", value=5.0)
    
    st.markdown("---")
    run_bot = st.toggle("إطلاق المحرك الآن ⚡")

# 3. محرك التداول الأساسي
if run_bot:
    if not (api_key and secret_key):
        st.warning("⚠️ حبيبي ضيف المفاتيح أولاً!")
    else:
        try:
            # إعداد الاتصال بـ Gate.io Futures Testnet
            exchange = ccxt.gateio({
                'apiKey': api_key,
                'secret': secret_key,
                'enableRateLimit': True,
                'options': {'defaultType': 'swap'} 
            })
            exchange.set_sandbox_mode(True) # تفعيل وضع الديمو

            # جلب الرصيد والسعر الحالي
            balance = exchange.fetch_balance()
            st.success("✅ متصل بنجاح بسيرفر الفيوتشرز!")
            
            # منطقة العرض الحية للبيانات
            col1, col2 = st.columns([1, 2])
            
            while True:
                ticker = exchange.fetch_ticker(symbol)
                price = ticker['last']
                
                with col1:
                    st.metric(f"سعر {symbol}", f"${price}")
                    st.metric("الرصيد المتاح في المحفظة", f"${balance.get('USDT', {}).get('free', 0)}")

                # --- حل مشكلة Precision (العقود الصحيحة) الظاهرة في image_36.png ---
                # Gate.io تطلب أرقام صحيحة للعقود في الغالب (Contracts)
                raw_qty = (trade_amount * leverage) / price
                contracts = int(raw_qty) # تحويل لرقم صحيح (1, 2, 3...) لضمان قبول الطلب
                
                if contracts < 1:
                    contracts = 1
                
                # تنفيذ الدخول التلقائي للصفقة
                try:
                    # ضبط الرافعة المالية المطلوبة
                    exchange.set_leverage(leverage, symbol)
                    
                    # فتح الصفقة (Market Order)
                    order = exchange.create_market_buy_order(symbol, contracts)
                    
                    now = datetime.now().strftime("%H:%M:%S")
                    log_msg = f"[{now}] ✅ تم فتح {contracts} عقد بسعر {price}"
                    st.session_state.trade_log.append(log_msg)
                    st.toast(log_msg)
                    
                except Exception as e_trade:
                    error_msg = f"⚠️ فشل التنفيذ: {str(e_trade)}"
                    st.session_state.trade_log.append(error_msg)

                with col2:
                    st.subheader("📋 سجل التحركات الحية")
                    # عرض آخر 10 عمليات في السجل
                    for entry in reversed(st.session_state.trade_log[-10:]):
                        st.write(entry)

                time.sleep(60) # تحديث العملية كل دقيقة
                st.rerun()

        except Exception as e:
            st.error(f"🛑 خطأ في الاتصال بالسيرفر: {e}")
else:
    st.info("المحرك في وضع الاستعداد. اضبط إعداداتك وشغل البوت.")
