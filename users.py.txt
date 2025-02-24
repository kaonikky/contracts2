import pandas as pd
import os
from datetime import datetime, timedelta
import hashlib
import secrets

def hash_password(password: str) -> str:
    """Хеширует пароль"""
    return hashlib.sha256(password.encode()).hexdigest()

def init_users():
    """Инициализирует файл пользователей, если он не существует"""
    if not os.path.exists('data/users.csv'):
        df = pd.DataFrame(columns=['username', 'password_hash', 'role', 'full_name'])
        # Создаем администратора по умолчанию
        admin = {
            'username': 'admin',
            'password_hash': hash_password('admin'),
            'role': 'admin',
            'full_name': 'Администратор'
        }
        df = pd.concat([df, pd.DataFrame([admin])], ignore_index=True)
        df.to_csv('data/users.csv', index=False)
        return df
    return pd.read_csv('data/users.csv')

def verify_user(username: str, password: str) -> tuple[bool, str, str]:
    """
    Проверяет учетные данные пользователя
    Возвращает (успех, роль, полное_имя)
    """
    users_df = pd.read_csv('data/users.csv')
    user = users_df[users_df['username'] == username]
    
    if user.empty:
        return False, '', ''
        
    if user.iloc[0]['password_hash'] == hash_password(password):
        return True, user.iloc[0]['role'], user.iloc[0]['full_name']
    
    return False, '', ''

def add_user(username: str, password: str, role: str, full_name: str) -> bool:
    """Добавляет нового пользователя"""
    users_df = pd.read_csv('data/users.csv')
    
    if username in users_df['username'].values:
        return False
        
    new_user = {
        'username': username,
        'password_hash': hash_password(password),
        'role': role,
        'full_name': full_name
    }
    
    users_df = pd.concat([users_df, pd.DataFrame([new_user])], ignore_index=True)
    users_df.to_csv('data/users.csv', index=False)
    return True
