import streamlit as st
import json
from datetime import datetime
import os

# إعداد الصفحة
st.set_page_config(page_title="Expense Tracker", page_icon="💰", layout="wide")

# ملف البيانات
DATA_FILE = 'users_data.json'

# دوال مساعدة
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_total(expenses):
    return sum(float(exp.get('amount', 0)) for exp in expenses)

# تحميل البيانات
if 'users_data' not in st.session_state:
    st.session_state.users_data = load_data()
if 'current_user' not in st.session_state:
    st.session_state.current_user = None

# العنوان الرئيسي
st.title("💰 تطبيق تتبع المصروفات")

# تسجيل الدخول / إنشاء حساب
if st.session_state.current_user is None:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("تسجيل الدخول")
        login_username = st.text_input("اسم المستخدم", key="login_user")
        login_password = st.text_input("كلمة المرور", type="password", key="login_pass")
        
        if st.button("دخول"):
            if login_username in st.session_state.users_data:
                if st.session_state.users_data[login_username]['password'] == login_password:
                    st.session_state.current_user = login_username
                    st.success("تم تسجيل الدخول بنجاح!")
                    st.rerun()
                else:
                    st.error("كلمة مرور خاطئة")
            else:
                st.error("اسم المستخدم غير موجود")
    
    with col2:
        st.subheader("إنشاء حساب جديد")
        new_username = st.text_input("اسم المستخدم الجديد", key="new_user")
        new_password = st.text_input("كلمة المرور", type="password", key="new_pass")
        
        if st.button("إنشاء حساب"):
            if new_username and new_password:
                if new_username not in st.session_state.users_data:
                    st.session_state.users_data[new_username] = {
                        'password': new_password,
                        'expenses': []
                    }
                    save_data(st.session_state.users_data)
                    st.success("تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول")
                else:
                    st.error("اسم المستخدم موجود بالفعل")
            else:
                st.warning("من فضلك أدخل جميع البيانات")

else:
    # واجهة المستخدم بعد تسجيل الدخول
    user = st.session_state.current_user
    user_data = st.session_state.users_data[user]
    
    # شريط علوي
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.header(f"مرحباً، {user}! 👋")
    with col3:
        if st.button("تسجيل الخروج"):
            st.session_state.current_user = None
            st.rerun()
    
    st.markdown("---")
    
    # إضافة مصروف جديد
    with st.expander("➕ إضافة مصروف جديد", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category = st.selectbox(
                "الفئة",
                ["طعام", "مواصلات", "ترفيه", "فواتير", "تسوق", "صحة", "تعليم", "أخرى"]
            )
        
        with col2:
            amount = st.number_input("المبلغ (جنيه)", min_value=0.0, step=1.0)
        
        with col3:
            date = st.date_input("التاريخ", datetime.now())
        
        description = st.text_input("الوصف (اختياري)")
        
        if st.button("➕ إضافة", type="primary"):
            if amount > 0:
                new_expense = {
                    'category': category,
                    'amount': amount,
                    'date': date.strftime('%Y-%m-%d'),
                    'description': description,
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                user_data['expenses'].append(new_expense)
                save_data(st.session_state.users_data)
                st.success(f"تم إضافة مصروف {amount} جنيه في فئة {category}")
                st.rerun()
            else:
                st.warning("من فضلك أدخل مبلغ صحيح")
    
    st.markdown("---")
    
    # عرض الإحصائيات
    if user_data['expenses']:
        total = calculate_total(user_data['expenses'])
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي المصروفات", f"{total:.2f} جنيه")
        with col2:
            st.metric("عدد المصروفات", len(user_data['expenses']))
        with col3:
            avg = total / len(user_data['expenses'])
            st.metric("متوسط المصروف", f"{avg:.2f} جنيه")
        
        st.markdown("---")
        
        # جدول المصروفات
        st.subheader("📊 سجل المصروفات")
        
        # تجميع حسب الفئة
        categories = {}
        for exp in user_data['expenses']:
            cat = exp['category']
            categories[cat] = categories.get(cat, 0) + float(exp['amount'])
        
        col1, col2 = st.columns([2, 3])
        
        with col1:
            st.write("**المصروفات حسب الفئة:**")
            for cat, amount in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                percentage = (amount / total) * 100
                st.write(f"• {cat}: {amount:.2f} جنيه ({percentage:.1f}%)")
        
        with col2:
            import pandas as pd
            df = pd.DataFrame(user_data['expenses'])
            st.dataframe(
                df[['date', 'category', 'amount', 'description']].sort_values('date', ascending=False),
                use_container_width=True,
                hide_index=True
            )
        
        # حذف المصروفات
        st.markdown("---")
        if st.button("🗑️ حذف جميع المصروفات", type="secondary"):
            user_data['expenses'] = []
            save_data(st.session_state.users_data)
            st.success("تم حذف جميع المصروفات")
            st.rerun()
    
    else:
        st.info("لا توجد مصروفات حتى الآن. ابدأ بإضافة مصروف جديد!")
