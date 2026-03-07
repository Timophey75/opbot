#!/usr/bin/env python3
"""
Скрипт инициализации системы
Создает администратора по умолчанию
"""

import os
import sys
from dotenv import load_dotenv
from database import Database

load_dotenv()

def init_system():
    """Инициализирует систему и создает администратора"""
    db = Database()
    
    # Проверяем, есть ли админ в системе
    admin_code = os.getenv('ADMIN_CODE', '0000')
    existing_admin = db.get_user_by_code(admin_code)
    
    if existing_admin:
        print(f"✅ Администратор уже существует: {existing_admin['name']} {existing_admin['surname']}")
        print(f"   Код: {existing_admin['code']}")
        print(f"   Цвет: {existing_admin['color_emoji']}")
        return
    
    # Создаем администратора
    print("🔧 Инициализация системы...")
    print(f"   📋 Код администратора: {admin_code}")
    
    admin_id = db.create_user(
        user_id=None,  # Будет заполнен при первом входе
        name="Администратор",
        surname="Системы",
        code=admin_code,
        is_admin=1
    )
    
    admin = db.get_user_by_id(admin_id)
    
    print(f"✅ Администратор создан успешно!")
    print(f"   👤 Имя: {admin['name']} {admin['surname']}")
    print(f"   🔐 Код входа: {admin['code']}")
    print(f"   🎨 Цвет (эмодзи): {admin['color_emoji']}")
    print()
    print("📌 Эти учетные данные используются для входа в админ-панель")

if __name__ == '__main__':
    init_system()
