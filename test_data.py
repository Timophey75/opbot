#!/usr/bin/env python3
"""
Скрипт для тестирования приложения
Создает тестовых операторов, события и проверяет функциональность
"""

import sqlite3
from database import Database
from datetime import datetime, timedelta

def create_test_data():
    """Создает тестовые данные в БД"""
    
    db = Database()
    
    print("🧪 Тестирование системы...\n")
    
    # Создаем операторов
    print("👥 Создание тестовых операторов...")
    
    operators = [
        ("Иван", "Петров"),
        ("Мария", "Сидорова"),
        ("Алексей", "Иванов"),
    ]
    
    operator_ids = []
    for name, surname in operators:
        op_id = db.create_user(
            user_id=None,
            name=name,
            surname=surname,
            code=db.generate_operator_code(),
            is_admin=0
        )
        op_user = db.get_user_by_id(op_id)
        operator_ids.append(op_id)
        print(f"  ✅ {name} {surname}")
        print(f"     Код: {op_user['code']}, Цвет: {op_user['color_emoji']}")
    
    # Создаем тестовые события
    print("\n📅 Создание тестовых событий...")
    
    today = datetime.now().date()
    
    events = [
        (str(today), "10:00", "Утренняя встреча", "morning", operator_ids[0]),
        (str(today), "19:00", "Вечерний брифинг", "evening", operator_ids[1]),
        (str(today + timedelta(days=1)), "10:00", "Планирование дня", "morning", operator_ids[2]),
        (str(today + timedelta(days=1)), "19:00", "Анализ результатов", "evening", operator_ids[0]),
    ]
    
    for date, time, title, period, op_id in events:
        event_id = db.create_event(date, time, title, period, op_id)
        print(f"  ✅ {title} ({date} {time})")
    
    # Проверяем операторов
    print("\n🔍 Проверка операторов...")
    all_ops = db.get_all_operators()
    print(f"  Всего операторов: {len(all_ops)}")
    
    for op in all_ops:
        print(f"  - {op['name']} {op['surname']} ({op['code']}) {op['color_emoji']}")
    
    # Проверяем события на сегодня
    print(f"\n📋 События на {today}...")
    today_events = db.get_events_by_date(str(today))
    for event in today_events:
        op = db.get_user_by_id(event['operator_id']) if event['operator_id'] else None
        op_name = f"{op['color_emoji']} {op['name']} {op['surname']}" if op else "Не назначен"
        print(f"  - {event['title']} ({event['time']}) → {op_name}")
    
    # Напоминания
    print("\n🔔 Настройка напоминаний...")
    for op_id in operator_ids[:2]:
        db.create_or_update_reminder(op_id, 'day_before', '10:00', '19:00', 1)
        print(f"  ✅ Напоминания для оператора {op_id}")
    
    print("\n✅ Тестовые данные созданы успешно!")
    print("\n📝 Коды для входа:")
    print("  - Администратор: 0000")
    for op in all_ops[:3]:
        print(f"  - {op['name']} {op['surname']}: {op['code']}")

if __name__ == '__main__':
    create_test_data()
