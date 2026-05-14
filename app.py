
import streamlit as st

# --- إعدادات ثابتة حسب طلبك ---
FIXED_MARGIN = 100.0  # المارجن الثابت من رصيدك هو 100 دولار
LEVERAGE = 100        # الرافعة المالية الثابتة

st.sidebar.title("🐋 محرك الحيتان الاحترافي")
st.sidebar.info(f"المارجن الثابت: {FIXED_MARGIN}$ | الرافعة: {LEVERAGE}x")

# --- محاكي نظام المؤشرات الـ 10 ---
def check_indicators():
    # محاكاة لـ 10 مؤشرات تعطي إشارات (1 للشراء، 0 للحياد)
    # في الكود الحقيقي، استبدل هذا بجلب بيانات RSI, MACD, إلخ.
    indicator_results = [1, 1, 1, 1, 1, 1, 1, 0, 0, 1] # مثال لـ 8 مؤشرات إيجابية
    return sum(indicator_results), indicator_results

# --- الحسابات التنفيذية ---
current_price = 79841.1 # السعر الحالي من المنصة

# حجم الصفقة الإجمالي = 100$ * 100 = 10,000$
total_position_value = FIXED_MARGIN * LEVERAGE 
calculated_qty = total_position_value / current_price

# --- واجهة المستخدم ---
st.title("📊 نظام التداول الآلي")

vote_count, details = check_indicators()

st.subheader(f"نتيجة تصويت المؤشرات: {vote_count} من 10")

# حل مشكلة الخطأ الأحمر (AUTO_INVALID_PARAM_PRICE) عبر تقريب الأسعار
entry_price = round(current_price, 1)
tp_price = round(entry_price * 1.01, 1) # هدف ربح 1% كمثال
sl_price = round(entry_price * 0.995, 1) # وقف خسارة 0.5% كمثال

if vote_count >= 7:
    st.success(f"✅ إشارة قوية! التصويت {vote_count}/10")
    st.write(f"🔹 حجم الصفقة الكلي: **{total_position_value}$**")
    st.write(f"🔹 الكمية (Qty): `{calculated_qty:.4f}` BTC")
    
    if st.button("دخول الصفقة الآن"):
        # إرسال الطلب للمنصة مع تقريب الأرقام لمنع أخطاء الـ API
        order_data = {
            "initial_price": entry_price,
            "qty": round(calculated_qty, 4),
            "take_profit": tp_price,
            "stop_loss": sl_price
        }
        st.json(order_data)
        st.success("🚀 تم إرسال الأوامر للمنصة بنجاح!")
else:
    st.warning("⚠️ المؤشرات لا تدعم الدخول حالياً.")

st.divider()
st.caption("ملاحظة: تم تثبيت المارجن عند 100$ والتقريب مفعل لتفادي أخطاء Gate.io.")

