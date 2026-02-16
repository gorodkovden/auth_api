"""
Настройка хэширования паролей
"""

import bcrypt

# Можем задать свой rounds для генератора соли, больше - безпоасней и медленей
salt = bcrypt.gensalt(rounds=12)

# Функция создания хеша пароля
def get_password_hash(password):
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# Проверка пароля
def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))