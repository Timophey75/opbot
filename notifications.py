"""
Утилиты для отправки уведомлений в Telegram
"""

import asyncio
from datetime import datetime, timedelta
import logging
from database import Database
from bot import bot, send_shift_notification, send_refusal_notification

logger = logging.getLogger(__name__)
db = Database()

async def send_shift_reminder(user_id: int, event_date: str, event_time: str, title: str):
    """Отправляет напоминание о смене"""
    await send_shift_notification(user_id, '', event_date, event_time, title)

async def send_refusal_notification_to_admin(admin_id: int, operator_name: str, event_date: str, event_time: str, reason: str):
    """Отправляет уведомление админу об отказе"""
    await send_refusal_notification(admin_id, operator_name, event_date, event_time, reason)

async def check_and_send_reminders():
    """
    Проверяет и отправляет запланированные напоминания
    Должна запускаться периодически (например, каждый час)
    """
    try:
        current_datetime = datetime.now()
        current_date = current_datetime.date()
        current_time = current_datetime.time()

        # Напоминание за сутки
        reminders_day_before = db.get_reminders_by_type('day_before')
        for reminder in reminders_day_before:
            if reminder['enabled']:
                # Проверяем события на завтра
                tomorrow = current_date + timedelta(days=1)
                tomorrow_str = tomorrow.strftime('%Y-%m-%d')
                
                events = db.get_events_by_date(tomorrow_str)
                user = db.get_user_by_id(reminder['user_id'])
                
                # Проверяем, назначен ли пользователь на эти события
                for event in events:
                    if event['operator_id'] == reminder['user_id']:
                        try:
                            if user['user_id']:
                                await send_shift_reminder(
                                    user['user_id'],
                                    tomorrow_str,
                                    event['time'],
                                    event['title']
                                )
                        except Exception as e:
                            logger.error(f"Error sending reminder: {e}")

        # Напоминание утром
        reminders_morning = db.get_reminders_by_type('morning')
        for reminder in reminders_morning:
            if reminder['enabled']:
                reminder_time = datetime.strptime(reminder['time_morning'], '%H:%M').time()
                
                # Отправляем если время совпадает (с точностью до минуты)
                if (current_time.hour == reminder_time.hour and 
                    current_time.minute == reminder_time.minute):
                    
                    events = db.get_events_by_date(str(current_date))
                    user = db.get_user_by_id(reminder['user_id'])
                    
                    for event in events:
                        if event['operator_id'] == reminder['user_id']:
                            try:
                                if user['user_id']:
                                    await send_shift_reminder(
                                        user['user_id'],
                                        str(current_date),
                                        event['time'],
                                        event['title']
                                    )
                            except Exception as e:
                                logger.error(f"Error sending reminder: {e}")

        # Напоминание вечером накануне
        reminders_evening_before = db.get_reminders_by_type('evening_before')
        for reminder in reminders_evening_before:
            if reminder['enabled']:
                reminder_time = datetime.strptime(reminder['time_evening'], '%H:%M').time()
                
                if (current_time.hour == reminder_time.hour and 
                    current_time.minute == reminder_time.minute):
                    
                    tomorrow = current_date + timedelta(days=1)
                    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
                    
                    events = db.get_events_by_date(tomorrow_str)
                    user = db.get_user_by_id(reminder['user_id'])
                    
                    for event in events:
                        if event['operator_id'] == reminder['user_id']:
                            try:
                                if user['user_id']:
                                    await send_shift_reminder(
                                        user['user_id'],
                                        tomorrow_str,
                                        event['time'],
                                        event['title']
                                    )
                            except Exception as e:
                                logger.error(f"Error sending reminder: {e}")

    except Exception as e:
        logger.error(f"Error checking reminders: {e}")

async def periodic_reminder_checker():
    """
    Запускает проверку напоминаний каждый час
    """
    while True:
        try:
            await check_and_send_reminders()
        except Exception as e:
            logger.error(f"Periodic reminder check error: {e}")
        
        # Ждем 1 минуту перед следующей проверкой
        await asyncio.sleep(60)
