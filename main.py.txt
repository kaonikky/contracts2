# Содержимое файла main.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from utils import get_contract_status, sort_contracts, filter_contracts, check_inn_exists, get_contract_by_inn, get_org_info, log_contract_change, get_contract_history
from users import init_users, verify_user, add_user
import openpyxl

# Настройка страницы
st.set_page_config(
    page_title="Управление договорами",
    page_icon="📄",
    layout="wide"
)

# Инициализация состояния
if 'sort_column' not in st.session_state:
    st.session_state.sort_column = None
if 'sort_ascending' not in st.session_state:
    st.session_state.sort_ascending = True
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_full_name' not in st.session_state:
    st.session_state.user_full_name = None
if 'org_name' not in st.session_state:
    st.session_state.org_name = None
if 'director' not in st.session_state:
    st.session_state.director = None
if 'address' not in st.session_state:
    st.session_state.address = None

def load_data():
    """Загрузка данных из CSV файла"""
    if not os.path.exists('data/contracts.csv'):
        df = pd.DataFrame(columns=[
            'contract_id', 'name', 'director', 'address', 'inn', 
            'end_date', 'value', 'status', 'comments', 'lawyer'
        ])
        df.to_csv('data/contracts.csv', index=False)
        return df

    try:
        df = pd.read_csv('data/contracts.csv', dtype={
            'contract_id': str,
            'name': str,
            'director': str,
            'address': str,
            'inn': str,
            'value': float,
            'status': str,
            'comments': str,
            'lawyer': str
        })
        df['end_date'] = pd.to_datetime(df['end_date'], errors='coerce')

        for idx in df.index:
            status, emoji = get_contract_status(df.at[idx, 'end_date'])
            df.at[idx, 'status'] = f"{emoji} {status}"

        return df
    except pd.errors.EmptyDataError:
        return pd.DataFrame(columns=[
            'contract_id', 'name', 'director', 'address', 'inn', 
            'end_date', 'value', 'status', 'comments', 'lawyer'
        ])

# Функция выхода
def logout():
    st.session_state.authenticated = False
    st.session_state.user_role = None
    st.session_state.user_full_name = None
    st.rerun()

# Форма входа
if not st.session_state.authenticated:
    st.title('🔐 Вход в систему')

    with st.form("login_form"):
        username = st.text_input("Имя пользователя")
        password = st.text_input("Пароль", type="password")
        submitted = st.form_submit_button("Войти")

        if submitted:
            success, role, full_name = verify_user(username, password)
            if success:
                st.session_state.authenticated = True
                st.session_state.user_role = role
                st.session_state.user_full_name = full_name
                st.rerun()
            else:
                st.error("❌ Неверное имя пользователя или пароль")

else:
    # Загружаем данные и показываем интерфейс
    df = load_data()
    
    # Остальной код интерфейса...
    # [Полный код main.py доступен в репозитории]

init_users()
