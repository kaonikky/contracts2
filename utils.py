import pandas as pd
from datetime import datetime, timedelta
import uuid
import streamlit as st
import io
import requests
import os
def generate_contract_id():
    """Generate a unique contract ID."""
    return str(uuid.uuid4())[:8]
def get_contract_status(end_date):
    """
    Calculate contract status based on end date.
    Returns tuple (status, emoji)
    """
    if pd.isna(end_date):
        return "Нет даты окончания", "⚪️"
    try:
        today = datetime.now().date()
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date).date()
        else:
            end_date = end_date.date()
        days_remaining = (end_date - today).days
        if days_remaining < 0:
            return f"Истек {abs(days_remaining)} дней назад", "🔴"
        elif days_remaining <= 30:
            return f"Истекает через {days_remaining} дней", "🟡"
        else:
            return "Действующий", "🟢"
    except Exception as e:
        return "Ошибка в дате", "⚪️"
def get_org_info(inn):
    """
    Получает информацию об организации по ИНН через DaData API.
    Возвращает словарь с данными или None в случае ошибки.
    """
    try:
        url = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
        headers = {
            'Authorization': f'Token {os.environ["DADATA_API_KEY"]}',
            'X-Secret': os.environ["DADATA_SECRET_KEY"],
            'Content-Type': 'application/json',
        }
        data = {"query": inn}
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()
        result = response.json()
        if not result.get('suggestions'):
            return None
        org_data = result['suggestions'][0]['data']
        address = org_data.get('address', {}).get('value', '') if org_data.get('address') else ''
        return {
            'name': org_data.get('name', {}).get('short_with_opf', ''),
            'director': org_data.get('management', {}).get('name', ''),
            'inn': org_data.get('inn', ''),
            'address': address
        }
    except Exception as e:
        st.error(f"❌ Ошибка при получении данных организации: {str(e)}")
        return None
def log_contract_change(contract_id, field, old_value, new_value, user):
    """
    Записывает изменение в историю.
    """
    if not os.path.exists('data/contract_history.csv'):
        history_df = pd.DataFrame(columns=['timestamp', 'contract_id', 'field', 'old_value', 'new_value', 'user'])
    else:
        history_df = pd.read_csv('data/contract_history.csv')
    new_record = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'contract_id': contract_id,
        'field': field,
        'old_value': old_value,
        'new_value': new_value,
        'user': user
    }
    history_df = pd.concat([history_df, pd.DataFrame([new_record])], ignore_index=True)
    history_df.to_csv('data/contract_history.csv', index=False)
def sort_contracts(df, sort_by=None, ascending=True):
    """Sort contracts by specified column."""
    if df.empty:
        return df
    # Создаем копию для сортировки
    sorted_df = df.copy()
    if sort_by == 'name':
        # Сортировка по названию (игнорируем регистр)
        return sorted_df.sort_values(
            by='name',
            ascending=ascending,
            key=lambda x: x.str.lower()
        )
    elif sort_by == 'end_date':
        # Конвертируем даты и сортируем
        sorted_df['end_date'] = pd.to_datetime(sorted_df['end_date'], errors='coerce')
        sorted_df = sorted_df.sort_values(by='end_date', ascending=ascending, na_position='last')
        return sorted_df
    return sorted_df
def filter_contracts(df, search_term=""):
    """
    Filter contracts based on search term in any field.
    Returns original DataFrame if search term is empty.
    """
    if df.empty or not str(search_term).strip():
        return df
    # Создаем маску для фильтрации
    mask = pd.Series(False, index=df.index)
    # Преобразуем поисковый запрос
    search_term = str(search_term).lower().strip()
    # Ищем совпадения во всех столбцах
    for column in df.columns:
        values = df[column].fillna('').astype(str).str.lower()
        mask |= values.str.contains(search_term, na=False, regex=False)
    # Возвращаем отфильтрованный датафрейм
    return df[mask]
def check_inn_exists(df, inn):
    """
    Проверяет, существует ли контракт с указанным ИНН.
    Возвращает True, если ИНН уже существует.
    """
    if df.empty:
        return False
    return inn in df['inn'].values
def get_contract_by_inn(df, inn):
    """
    Возвращает информацию о контракте по ИНН.
    """
    if df.empty:
        return None
    contract = df[df['inn'] == inn]
    if not contract.empty:
        return contract.iloc[0]
    return None
