import streamlit as st
import ccxt  # المكتبة الأساسية للربط مع المنصات
import pandas as pd

# --- إعدادات الصفحة ---
st.set_page_config(page_title="Whale Engine Pro", layout="wide")

# --- واجهة إدخال مفاتيح الـ API (الأمان أولاً) ---
st.sidebar.title("🔑 إعدادات الاتصال")
api_key = st.sidebar.text_input("API Key", type="password")
api_secret = st.sidebar.text_input("Secret Key", type="password")
testnet_mode = st.sidebar.checkbox("تشغيل وضع Testnet", value=True)

# --- الثوابت حسب طلبك ---
FIXED_MARGIN = 100.0  # مارجن ثابت 100$
LEVERAGE = 100        # رافعة 100x

# --- وظيفة الربط بالمنصة ---
def get_exchange():
    if not api_key or not api_secret:
        st.error("الرجاء إدخال مفاتيح الـ API أولاً!")
        return None
    
    exchange = ccxt.gateio({
        'apiKey': api_key,
        'secret': api_secret,
        'options': {'defaultType': 'swap'}  # للتداول في الفيوتشرز
    })
    exchange.set_sandbox_mode(testnet_mode)
    return exchange

# --- نظام المؤشرات الـ 10 ---
def get_indicators_signals():
    # هنا يتم وضع منطق التحليل الفني الحقيقي
    indicators = ["RSI", "MACD", "EMA20", "EMA50", "BB", "Stoch", "ADX", "CCI", "ATR", "Ichimoku"]
    # محاكاة: 1 يعني شراء، 0 يعني بيع/حياد
    signals = [1, 1, 1, 1, 1, 1, 1, 0, 0, 1] 
    return list(zip(indicators, signals))

# --- تنفيذ الصفقة ---
def open_position(exchange, side, price):
    try:
        # حساب الكمية: 100$ * 100 / السعر
        qty = (FIXED_MARGIN * LEVERAGE) / price
        
        # حل مشكلة الخطأ الأحمر (التقريب)
        symbol = 'BTC/USDT:USDT'
        params = {
            'stopLoss': {'type': 'limit', 'price': round(price * 0.995, 1)},
            'takeProfit': {'type': 'limit', 'price': round(price * 1.01, 1)},
        }
        
        order = exchange.create_order(
            symbol=symbol,
            type='market',
            side=side,
            amount=round(qty, 4),
            params=params
        )
        return True, order
    except Exception as e:
        return False, str(e)

# --- الواجهة الرئيسية ---
st.title("🐋 محرك الحيتان: الربط الفعلي")

if st.sidebar.button("فحص الاتصال بالحساب"):
    ex = get_exchange()
    if ex:
        balance = ex.fetch_balance()
        st.sidebar.success(f"متصل! الرصيد المتاح: {balance['total']['USDT']}$")

# عرض المؤشرات
st.subheader("📊 حالة المؤشرات الفنية")
signals_data = get_indicators_signals()
total_buy = sum([s[1] for s in signals_data])

cols = st.columns(5)
for i, (name, val) in enumerate(signals_data):
    cols[i%5].metric(name, "Buy" if val == 1 else "Wait")

st.divider()

# زر التنفيذ
if total_buy >= 7:
    st.success(f"🔥 إشارة دخول قوية ({total_buy}/10)")
    if st.button("فتح صفقة بمارجن 100$ ورافعة 100x"):
        exchange = get_exchange()
        if exchange:
            # جلب السعر الحالي الحقيقي
            ticker = exchange.fetch_ticker('BTC/USDT:USDT')
            current_p = ticker['last']
            
            success, res = open_position(exchange, 'buy', current_p)
            if success:
                st.balloons()
                st.write("✅ تمت الصفقة بنجاح في المنصة!")
                st.json(res)
            else:
                st.error(f"❌ فشل التنفيذ: {res}")
else:
    st.warning("⏳ النظام يراقب.. لا توجد إشارة دخول حالياً.")
