from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import json
from datetime import datetime, timedelta
from database import Database
import logging
import asyncio
import threading
import hmac
import hashlib

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = Database()

# Константы
ADMIN_CODE = os.getenv('ADMIN_CODE', '3546')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '7253076546:AAG_gZ-Ye5yrBVXBFT2T6Pl26D2jQc6p3aY')

def validate_telegram_web_app_data(init_data: str, bot_token: str) -> bool:
    """Проверяет подпись Telegram WebApp initData"""
    try:
        data_dict = dict(pair.split('=') for pair in init_data.split('&'))
        hash_value = data_dict.pop('hash', None)
        
        if not hash_value:
            return False
        
        # Сортируем данные и создаем строку для хеширования
        data_string = '\n'.join(f'{k}={v}' for k, v in sorted(data_dict.items()))
        
        # Создаем подпись
        secret_key = hmac.new(b'WebAppData', bot_token.encode(), hashlib.sha256).digest()
        signature = hmac.new(secret_key, data_string.encode(), hashlib.sha256).hexdigest()
        
        return signature == hash_value
    except Exception as e:
        logger.error(f"Error validating Telegram data: {e}")
        return False
COLORS = ['🟦', '🟧', '🟥', '⬛️', '🟩', '🟪', '🟨', '🟫']
DEFAULT_MORNING_TIME = '10:00'
DEFAULT_EVENING_TIME = '19:00'

# Словарь для отслеживания сессий
sessions = {}

def send_refusal_notification_async(operator, event, reason):
    """Отправляет асинхронное уведомление об отказе (логирует, в реальной системе отправит в Telegram)"""
    logger.info(f"📢 Отказ от смены:")
    logger.info(f"   Оператор: {operator['name']} {operator['surname']}")
    logger.info(f"   Дата: {event['date'] if event else 'N/A'}")
    logger.info(f"   Время: {event['time'] if event else 'N/A'}")
    logger.info(f"   Причина: {reason}")
    # В реальной системе здесь будет отправка в Telegram через bot

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/app')
def mini_app():
    return send_from_directory('static', 'app.html')

# API Endpoints

@app.route('/api/auth/check', methods=['GET'])
def check_auth():
    """Проверяет аутентификацию пользователя"""
    user_id = request.args.get('user_id')
    
    if not user_id:
        return jsonify({'authenticated': False}), 400
    
    if user_id in sessions:
        user = sessions[user_id]
        return jsonify({
            'authenticated': True,
            'user': user,
            'is_admin': user.get('is_admin', 0)
        }), 200
    
    return jsonify({'authenticated': False}), 200

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Вход в приложение по коду"""
    data = request.json
    code = data.get('code', '')
    user_id = data.get('user_id', '')
    
    if not code or not user_id:
        return jsonify({'success': False, 'error': 'Missing credentials'}), 400
    
    # Сначала проверяем, совпадает ли код с ADMIN_CODE
    if code == ADMIN_CODE:
        # Ищем админа в базе или создаем его
        admin = db.get_user_by_code(code)
        if not admin:
            # Создаем администратора если его нет
            admin_id = db.create_user(
                user_id=user_id,
                name="Администратор",
                surname="Системы",
                code=code,
                is_admin=1
            )
            admin = db.get_user_by_id(admin_id)
        
        sessions[user_id] = {
            'id': admin['id'],
            'name': admin['name'],
            'surname': admin['surname'],
            'code': admin['code'],
            'color_emoji': admin['color_emoji'],
            'is_admin': admin['is_admin'],
            'user_id': admin['user_id']
        }
        
        return jsonify({
            'success': True,
            'user': sessions[user_id]
        }), 200
    
    # Поиск пользователя по коду
    user = db.get_user_by_code(code)
    
    if not user:
        return jsonify({'success': False, 'error': 'Invalid code'}), 401
    
    # Сохраняем сессию
    sessions[user_id] = {
        'id': user['id'],
        'name': user['name'],
        'surname': user['surname'],
        'code': user['code'],
        'color_emoji': user['color_emoji'],
        'is_admin': user['is_admin'],
        'user_id': user['user_id']
    }
    
    return jsonify({
        'success': True,
        'user': sessions[user_id]
    }), 200

@app.route('/api/calendar', methods=['GET'])
def get_calendar():
    """Получает календарь с событиями"""
    month = int(request.args.get('month', 3))  # По умолчанию март
    year = int(request.args.get('year', 2026))
    
    # Генерируем дни месяца
    from calendar import monthcalendar, month_name
    
    days = monthcalendar(year, month)
    month_name_str = month_name[month]
    
    calendar_data = []
    for week in days:
        week_data = []
        for day in week:
            if day == 0:
                week_data.append(None)
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                
                # Получаем события на этот день
                events = db.get_events_by_date(date_str)
                
                # Собираем эмодзи и для утра, и для вечера отдельно
                morning_operators = []
                evening_operators = []
                morning_ids = set()
                evening_ids = set()
                
                for event in events:
                    if event['operator_id']:
                        op_user = db.get_user_by_id(event['operator_id'])
                        if op_user:
                            if event['period'] == 'morning' and event['operator_id'] not in morning_ids:
                                morning_operators.append(op_user['color_emoji'])
                                morning_ids.add(event['operator_id'])
                            elif event['period'] == 'evening' and event['operator_id'] not in evening_ids:
                                evening_operators.append(op_user['color_emoji'])
                                evening_ids.add(event['operator_id'])
                
                week_data.append({
                    'day': day,
                    'date': date_str,
                    'morning_operators': morning_operators,
                    'evening_operators': evening_operators
                })
        calendar_data.append(week_data)
    
    return jsonify({
        'month': month,
        'year': year,
        'month_name': month_name_str,
        'calendar': calendar_data
    }), 200

@app.route('/api/events/day', methods=['GET'])
def get_day_events():
    """Получает события на конкретный день"""
    date = request.args.get('date')
    user_id = request.args.get('user_id')
    
    if not date:
        return jsonify({'error': 'Date required'}), 400
    
    events = db.get_events_by_date(date)
    
    # Группируем по периодам
    morning = []
    evening = []
    
    for event in events:
        event_data = {
            'id': event['id'],
            'title': event['title'],
            'time': event['time'],
            'date': event['date'],
            'period': event['period'],
            'operator_id': event['operator_id']
        }
        
        if event['operator_id']:
            operator = db.get_user_by_id(event['operator_id'])
            if operator:
                event_data['operator'] = {
                    'id': operator['id'],
                    'name': operator['name'],
                    'surname': operator['surname'],
                    'color': operator['color_emoji']
                }
        
        if event['period'] == 'morning':
            morning.append(event_data)
        else:
            evening.append(event_data)
    
    # Получаем список всех операторов для отоб события
    all_operators = []
    for event in events:
        if event['operator_id']:
            operator = db.get_user_by_id(event['operator_id'])
            if operator and operator['id'] not in [op['id'] for op in all_operators]:
                all_operators.append({
                    'id': operator['id'],
                    'name': operator['name'],
                    'surname': operator['surname'],
                    'color': operator['color_emoji']
                })
    
    return jsonify({
        'date': date,
        'morning': morning,
        'evening': evening,
        'all_operators': all_operators
    }), 200

@app.route('/api/events/create', methods=['POST'])
def create_event():
    """Создает новое событие (только администратор)"""
    data = request.json
    user_id = data.get('user_id')
    
    # Проверяем права администратора
    if user_id not in sessions or not sessions[user_id].get('is_admin'):
        return jsonify({'success': False, 'error': 'No permission'}), 403
    
    date = data.get('date')
    period = data.get('period')  # 'morning' or 'evening'
    time = data.get('time')
    title = data.get('title')
    
    if not all([date, period, time, title]):
        return jsonify({'success': False, 'error': 'Missing fields'}), 400
    
    event_id = db.create_event(date, time, title, period)
    
    return jsonify({
        'success': True,
        'event_id': event_id
    }), 201

@app.route('/api/events/<int:event_id>/delete', methods=['DELETE'])
def delete_event(event_id):
    """Удаляет событие"""
    user_id = request.args.get('user_id')
    
    if user_id not in sessions or not sessions[user_id].get('is_admin'):
        return jsonify({'success': False, 'error': 'No permission'}), 403
    
    db.delete_event(event_id)
    
    return jsonify({'success': True}), 200

@app.route('/api/events/<int:event_id>/unassign', methods=['POST'])
def unassign_operator(event_id):
    """Удаляет назначение оператора"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in sessions or not sessions[user_id].get('is_admin'):
        return jsonify({'success': False, 'error': 'No permission'}), 403
    
    # Обновляем событие, убирая оператора
    db.assign_operator_to_event(event_id, None)
    
    return jsonify({'success': True}), 200

@app.route('/api/events/<int:event_id>/assign', methods=['POST'])
def assign_operator(event_id):
    """Назначает оператора на событие"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in sessions or not sessions[user_id].get('is_admin'):
        return jsonify({'success': False, 'error': 'No permission'}), 403
    
    operator_id = data.get('operator_id')
    
    if not operator_id:
        return jsonify({'success': False, 'error': 'Operator ID required'}), 400
    
    db.assign_operator_to_event(event_id, operator_id)
    
    return jsonify({'success': True}), 200

@app.route('/api/events/<int:event_id>/refuse', methods=['POST'])
def refuse_shift(event_id):
    """Отказывается от смены"""
    data = request.json
    user_id = data.get('user_id')
    reason = data.get('reason')
    
    if user_id not in sessions:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 403
    
    user = sessions[user_id]
    operator_id = user['id']
    
    if not reason:
        return jsonify({'success': False, 'error': 'Reason required'}), 400
    
    # Получаем информацию о событии
    event = db.get_events_by_date(data.get('date', ''))
    event_found = None
    for e in event:
        if e['id'] == event_id:
            event_found = e
            break
    
    db.create_refusal(operator_id, event_id, reason)
    
    # Отправляем уведомление админам
    send_refusal_notification_async(user, event_found, reason)
    
    return jsonify({'success': True}), 201

# Управление операторами (только админ)

@app.route('/api/operators/list', methods=['GET'])
def get_operators():
    """Получает список всех операторов (только администратор).
    В список также добавляется сам администратор, чтобы он мог
    назначать себя на смену. Поле is_admin указывает, что это админ.
    """
    user_id = request.args.get('user_id')
    
    if user_id not in sessions or not sessions[user_id].get('is_admin'):
        return jsonify({'error': 'No permission'}), 403
    
    operators = db.get_all_operators()
    admin = sessions[user_id]
    
    operators_data = []
    # вставляем администратора первым
    operators_data.append({
        'id': admin['id'],
        'name': admin['name'],
        'surname': admin['surname'],
        'code': admin.get('code', ''),
        'color_emoji': admin['color_emoji'],
        'is_admin': 1
    })
    
    for op in operators:
        operators_data.append({
            'id': op['id'],
            'name': op['name'],
            'surname': op['surname'],
            'code': op['code'],
            'color_emoji': op['color_emoji'],
            'is_admin': 0
        })
    
    return jsonify({'operators': operators_data}), 200

@app.route('/api/operators/<int:operator_id>/update', methods=['PUT'])
def update_operator(operator_id):
    """Обновляет имя и фамилию оператора (админ может редактировать и себя)"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in sessions or not sessions[user_id].get('is_admin'):
        return jsonify({'success': False, 'error': 'Not authenticated'}), 403
    
    name = data.get('name', '')
    surname = data.get('surname', '')
    
    if not name or not surname:
        return jsonify({'success': False, 'error': 'Name and surname required'}), 400
    
    # Обновляем оператора
    db.update_user(operator_id, name, surname)
    
    # Если админ редактирует себя, обновляем сессию
    if operator_id == sessions[user_id]['id']:
        sessions[user_id]['name'] = name
        sessions[user_id]['surname'] = surname
    
    return jsonify({'success': True}), 200

@app.route('/api/operators/create', methods=['POST'])
def create_operator():
    """Создает нового оператора"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in sessions or not sessions[user_id].get('is_admin'):
        return jsonify({'success': False, 'error': 'No permission'}), 403
    
    name = data.get('name')
    surname = data.get('surname')
    
    if not name or not surname:
        return jsonify({'success': False, 'error': 'Name and surname required'}), 400
    
    code = db.generate_operator_code()
    operator_id = db.create_user(None, name, surname, code, is_admin=0)
    
    operator = db.get_user_by_id(operator_id)
    
    return jsonify({
        'success': True,
        'operator': {
            'id': operator['id'],
            'name': operator['name'],
            'surname': operator['surname'],
            'code': operator['code'],
            'color_emoji': operator['color_emoji']
        }
    }), 201

@app.route('/api/operators/<int:operator_id>/delete', methods=['DELETE'])
def delete_operator(operator_id):
    """Удаляет оператора"""
    user_id = request.args.get('user_id')
    
    if user_id not in sessions or not sessions[user_id].get('is_admin'):
        return jsonify({'success': False, 'error': 'No permission'}), 403
    
    db.delete_user(operator_id)
    
    return jsonify({'success': True}), 200

# Напоминания

@app.route('/api/reminders/get', methods=['GET'])
def get_reminders():
    """Получает напоминания пользователя"""
    user_id = request.args.get('user_id')
    
    if user_id not in sessions:
        return jsonify({'error': 'Not authenticated'}), 403
    
    user = sessions[user_id]
    reminders = db.get_reminders_by_user(user['id'])
    
    reminders_data = []
    for reminder in reminders:
        reminders_data.append({
            'type': reminder['type'],
            'time_morning': reminder['time_morning'],
            'time_evening': reminder['time_evening'],
            'enabled': reminder['enabled']
        })
    
    return jsonify({'reminders': reminders_data}), 200

@app.route('/api/reminders/update', methods=['POST'])
def update_reminders():
    """Обновляет напоминания"""
    data = request.json
    user_id = data.get('user_id')
    
    if user_id not in sessions:
        return jsonify({'success': False, 'error': 'Not authenticated'}), 403
    
    user = sessions[user_id]
    reminder_type = data.get('type')
    time_morning = data.get('time_morning', DEFAULT_MORNING_TIME)
    time_evening = data.get('time_evening', DEFAULT_EVENING_TIME)
    enabled = data.get('enabled', 1)
    
    db.create_or_update_reminder(user['id'], reminder_type, time_morning, time_evening, enabled)
    
    return jsonify({'success': True}), 200

# Telegram WebApp Integration

@app.route('/api/tg/check-auth', methods=['POST'])
def check_tg_auth():
    """Проверяет аутентификацию через Telegram WebApp"""
    data = request.json
    init_data = data.get('initData', '')
    
    if not init_data:
        return jsonify({'authenticated': False}), 400
    
    # Проверяем подпись
    if not validate_telegram_web_app_data(init_data, TELEGRAM_BOT_TOKEN):
        return jsonify({'authenticated': False, 'error': 'Invalid signature'}), 403
    
    # Парсим данные для получения user_id
    try:
        data_dict = dict(pair.split('=') for pair in init_data.split('&'))
        user_info = json.loads(data_dict.get('user', '{}'))
        telegram_id = user_info.get('id')
        
        if not telegram_id:
            return jsonify({'authenticated': False}), 400
        
        # Ищем пользователя по Telegram ID
        user = db.get_user_by_telegram_id(telegram_id)
        
        if user and user.get('is_logged_in'):
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user['id'],
                    'name': user['name'],
                    'surname': user['surname'],
                    'is_admin': user['is_admin']
                }
            }), 200
        
        return jsonify({'authenticated': False}), 200
    except Exception as e:
        logger.error(f"Error checking Telegram auth: {e}")
        return jsonify({'authenticated': False, 'error': str(e)}), 400

@app.route('/api/tg/verify-code', methods=['POST'])
def verify_tg_code():
    """Проверяет код и привязывает Telegram ID"""
    data = request.json
    init_data = data.get('initData', '')
    code = data.get('code', '').strip()
    
    if not init_data or not code:
        return jsonify({'success': False, 'error': 'Missing data'}), 400
    
    # Проверяем подпись
    if not validate_telegram_web_app_data(init_data, TELEGRAM_BOT_TOKEN):
        return jsonify({'success': False, 'error': 'Invalid signature'}), 403
    
    try:
        # Парсим данные для получения user_id
        data_dict = dict(pair.split('=') for pair in init_data.split('&'))
        user_info = json.loads(data_dict.get('user', '{}'))
        telegram_id = user_info.get('id')
        
        if not telegram_id:
            return jsonify({'success': False, 'error': 'No user ID'}), 400
        
        # Проверяем код
        if code == ADMIN_CODE:
            # Создаем или получаем админа
            user = db.get_user_by_code(code)
            if not user:
                # Если админа нет, создаем
                user_id = db.create_user(telegram_id, 'Администратор', 'Системы', code, is_admin=1)
                user = db.get_user_by_id(user_id)
            else:
                # Привязываем telegram_id к существующему админу
                db.link_telegram_id(user['id'], telegram_id)
        else:
            # Ищем пользователя по коду
            user = db.get_user_by_code(code)
            
            if not user:
                return jsonify({'success': False, 'error': 'Invalid code'}), 401
            
            # Привязываем Telegram ID
            db.link_telegram_id(user['id'], telegram_id)
        
        # Устанавливаем статус логина
        db.set_login_status(user['id'], True)
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'surname': user['surname'],
                'is_admin': user['is_admin']
            }
        }), 200
    except Exception as e:
        logger.error(f"Error verifying code: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/tg/logout', methods=['POST'])
def tg_logout():
    """Выход из приложения Telegram WebApp"""
    data = request.json
    init_data = data.get('initData', '')
    
    if not init_data:
        return jsonify({'success': False}), 400
    
    # Проверяем подпись
    if not validate_telegram_web_app_data(init_data, TELEGRAM_BOT_TOKEN):
        return jsonify({'success': False, 'error': 'Invalid signature'}), 403
    
    try:
        data_dict = dict(pair.split('=') for pair in init_data.split('&'))
        user_info = json.loads(data_dict.get('user', '{}'))
        telegram_id = user_info.get('id')
        
        if telegram_id:
            db.set_login_status_by_telegram_id(telegram_id, False)
        
        return jsonify({'success': True}), 200
    except Exception as e:
        logger.error(f"Error logging out: {e}")
        return jsonify({'success': False, 'error': str(e)}), 400

# Служебные API

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(debug=False, host='0.0.0.0', port=port)
