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
        end_date = pd.to_datetime(end_date).date()
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

# [Остальные функции из utils.py доступны в репозитории]
