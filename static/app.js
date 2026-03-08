// Основное приложение
class ScheduleApp {
    constructor() {
        this.apiUrl = this.getApiUrl();
        this.user = null;
        this.currentMonth = new Date().getMonth() + 1;
        this.currentYear = new Date().getFullYear();
        this.selectedDate = null;
        this.operators = [];
        this.events = [];
        
        this.init();
    }

    getApiUrl() {
        // Определяем URL API на основе хоста
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:5000';
        }
        return 'https://opbot-webapp.onrender.com';
    }

    async init() {
        // Получаем user_id из параметров URL
        const params = new URLSearchParams(window.location.search);
        this.userId = params.get('user_id') || 'guest';
        
        // Проверяем аутентификацию
        await this.checkAuth();
    }

    async checkAuth() {
        try {
            const response = await fetch(`${this.apiUrl}/api/auth/check?user_id=${this.userId}`);
            const data = await response.json();
            
            if (data.authenticated) {
                this.user = data.user;
                this.showScreen('menuScreen');
                this.updateUserInfo();
                
                // Показываем кнопку операторов только для админа
                if (this.user.is_admin) {
                    document.getElementById('operatorsBtn').style.display = 'block';
                }
            } else {
                this.showScreen('loginScreen');
            }
        } catch (error) {
            console.error('Auth check error:', error);
            this.showScreen('loginScreen');
        }
    }

    updateUserInfo() {
        if (!this.user) return;
        
        const userInfo = document.getElementById('userInfo');
        document.getElementById('userName').textContent = `${this.user.name} ${this.user.surname}`;
        document.getElementById('userRole').textContent = this.user.is_admin ? 'Администратор' : 'Оператор';
        
        const badge = document.getElementById('userBadge');
        if (this.user.is_admin) {
            badge.innerHTML = '<span class="admin-badge">⭐ АДМИН</span>';
        } else {
            badge.innerHTML = `<span style="font-size: 28px;">${this.user.color_emoji}</span>`;
        }
        
        userInfo.style.display = 'flex';
    }

    async login() {
        const code = document.getElementById('codeInput').value.trim();
        const errorEl = document.getElementById('loginError');
        
        if (!code) {
            errorEl.textContent = '❌ Пожалуйста, введите код';
            return;
        }

        if (code.length !== 4) {
            errorEl.textContent = '❌ Код должен состоять из 4 цифр';
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/api/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    code: code,
                    user_id: this.userId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.user = data.user;
                errorEl.textContent = '';
                document.getElementById('codeInput').value = '';
                this.showScreen('menuScreen');
                this.updateUserInfo();
                
                // Показываем кнопку операторов только для админа
                if (this.user.is_admin) {
                    document.getElementById('operatorsBtn').style.display = 'block';
                }
            } else {
                errorEl.textContent = '❌ ' + (data.error || 'Неверный код');
            }
        } catch (error) {
            console.error('Login error:', error);
            errorEl.textContent = '❌ Ошибка подключения';
        }
    }

    async openCalendar() {
        this.showScreen('calendarScreen');
        await this.loadCalendar();
    }

    async loadCalendar() {
        try {
            const response = await fetch(
                `${this.apiUrl}/api/calendar?month=${this.currentMonth}&year=${this.currentYear}`
            );
            const data = await response.json();

            // Обновляем заголовок
            document.getElementById('monthYear').textContent = 
                `${data.month_name} ${data.year}`;

            const grid = document.getElementById('calendarGrid');
            grid.innerHTML = '';

            // Заголовки дней недели
            const weekDays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'];
            weekDays.forEach(day => {
                const header = document.createElement('div');
                header.className = 'weekday-header';
                header.textContent = day;
                grid.appendChild(header);
            });

            // Дни месяца
            const today = new Date();
            data.calendar.forEach(week => {
                week.forEach(day => {
                    if (!day) {
                        const cell = document.createElement('div');
                        cell.className = 'day-cell empty';
                        grid.appendChild(cell);
                    } else {
                        const cell = document.createElement('div');
                        cell.className = 'day-cell';
                        
                        // Проверяем, сегодня ли это
                        if (data.year === today.getFullYear() && 
                            data.month === today.getMonth() + 1 && 
                            day.day === today.getDate()) {
                            cell.classList.add('today');
                        }

                        cell.innerHTML = `
                            <span class="day-number">${day.day}</span>
                            ${day.operators.length > 0 ? 
                                `<div class="operators-icons">${day.operators.join('')}</div>` : 
                                ''}
                        `;

                        cell.onclick = () => this.selectDay(day.date);
                        grid.appendChild(cell);
                    }
                });
            });
        } catch (error) {
            console.error('Calendar load error:', error);
        }
    }

    prevMonth() {
        if (this.currentMonth === 1) {
            this.currentMonth = 12;
            this.currentYear--;
        } else {
            this.currentMonth--;
        }
        this.loadCalendar();
    }

    nextMonth() {
        if (this.currentMonth === 12) {
            this.currentMonth = 1;
            this.currentYear++;
        } else {
            this.currentMonth++;
        }
        this.loadCalendar();
    }

    todayMonth() {
        const today = new Date();
        this.currentMonth = today.getMonth() + 1;
        this.currentYear = today.getFullYear();
        this.loadCalendar();
    }

    async selectDay(date) {
        this.selectedDate = date;
        this.showScreen('dayScreen');
        await this.loadDayDetails(date);
    }

    async loadDayDetails(date) {
        try {
            const response = await fetch(`${this.apiUrl}/api/events/day?date=${date}&user_id=${this.userId}`);
            const data = await response.json();

            const dayContent = document.getElementById('dayContent');
            const dateObj = new Date(date);
            const dateStr = dateObj.toLocaleDateString('ru-RU', { 
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
            });

            let html = `<div class="day-title">📅 ${dateStr}</div>`;

            // Утро
            html += `<div class="period-section">
                <div class="period-title">🌅 Утро (10:00)</div>`;

            if (data.morning.length === 0) {
                html += '<div style="color: #999; font-size: 14px;">Нет мероприятий</div>';
            } else {
                data.morning.forEach(event => {
                    html += `<div class="event" style="position: relative;">
                        <div class="event-title">${event.title}</div>
                        <div class="event-time">⏰ ${event.time}</div>`;
                    
                    if (event.operator) {
                        html += `<div class="event-operator">
                            ${event.operator.color} ${event.operator.name} ${event.operator.surname}
                        </div>`;
                    }
                    
                    // Кнопки для админа
                    if (this.user.is_admin) {
                        html += `<div style="margin-top: 8px; display: flex; gap: 5px; font-size: 12px;">
                            ${!event.operator ? 
                                `<button class="icon-btn" onclick="app.openOperatorSelectModal(${event.id})">➕ Назначить</button>` :
                                `<button class="icon-btn" onclick="app.openOperatorSelectModal(${event.id})">↩️ Переназначить</button>`
                            }
                            <button class="icon-btn" onclick="app.deleteEvent(${event.id}, '${date}')">🗑️ Удалить</button>
                        </div>`;
                    }
                    
                    html += `</div>`;
                });
            }

            html += `</div>`;

            // Вечер
            html += `<div class="period-section">
                <div class="period-title">🌆 Вечер (19:00)</div>`;

            if (data.evening.length === 0) {
                html += '<div style="color: #999; font-size: 14px;">Нет мероприятий</div>';
            } else {
                data.evening.forEach(event => {
                    html += `<div class="event" style="position: relative;">
                        <div class="event-title">${event.title}</div>
                        <div class="event-time">⏰ ${event.time}</div>`;
                    
                    if (event.operator) {
                        html += `<div class="event-operator">
                            ${event.operator.color} ${event.operator.name} ${event.operator.surname}
                        </div>`;
                    }
                    
                    // Кнопки для админа
                    if (this.user.is_admin) {
                        html += `<div style="margin-top: 8px; display: flex; gap: 5px; font-size: 12px;">
                            ${!event.operator ? 
                                `<button class="icon-btn" onclick="app.openOperatorSelectModal(${event.id})">➕ Назначить</button>` :
                                `<button class="icon-btn" onclick="app.openOperatorSelectModal(${event.id})">↩️ Переназначить</button>`
                            }
                            <button class="icon-btn" onclick="app.deleteEvent(${event.id}, '${date}')">🗑️ Удалить</button>
                        </div>`;
                    }
                    
                    html += `</div>`;
                });
            }

            html += `</div>`;

            // Кнопки действий
            if (!this.user.is_admin) {
                // Для обычного оператора
                if (data.morning.length > 0 || data.evening.length > 0) {
                    html += `<button class="btn" style="margin-top: 15px;" onclick="app.openRefusalModal('morning')">
                        ❌ Не смогу работать утром
                    </button>`;
                    html += `<button class="btn" style="margin-top: 10px;" onclick="app.openRefusalModal('evening')">
                        ❌ Не смогу работать вечером
                    </button>`;
                }
            } else {
                // Для админа
                html += `<button class="btn" style="margin-top: 15px;" onclick="app.openEventModal('morning')">
                    ➕ Создать мероприятие утром
                </button>`;
                html += `<button class="btn" style="margin-top: 10px;" onclick="app.openEventModal('evening')">
                    ➕ Создать мероприятие вечером
                </button>`;
            }

            dayContent.innerHTML = html;
        } catch (error) {
            console.error('Day details load error:', error);
        }
    }

    backToCalendar() {
        this.showScreen('calendarScreen');
    }

    backToMenu() {
        this.showScreen('menuScreen');
    }

    async openReminders() {
        this.showScreen('remindersScreen');
        await this.loadReminders();
    }

    async loadReminders() {
        try {
            const response = await fetch(`${this.apiUrl}/api/reminders/get?user_id=${this.userId}`);
            const data = await response.json();

            const content = document.getElementById('remindersContent');
            let html = '';

            // Типы напоминаний (добавлен день до без времени)
            const reminderTypes = [
                { id: 'day_before', label: '📅 Напомнить за сутки', timeField: null, defaultTime: null },
                { id: 'morning', label: '🌅 Напомнить утром', timeField: 'time_morning', defaultTime: '10:00' },
                { id: 'evening_before', label: '🌆 Напомнить вечером накануне', timeField: 'time_evening', defaultTime: '19:00' }
            ];

            reminderTypes.forEach(type => {
                // создаём объект напоминания, не добавляя поля времени если его нет
                let reminder = data.reminders.find(r => r.type === type.id);
                if (!reminder) {
                    reminder = { type: type.id, enabled: 1 };
                    if (type.timeField) {
                        reminder[type.timeField] = type.defaultTime;
                    }
                }

                html += `<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                        <span style="font-weight: 600;">${type.label}</span>
                        <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                            <input type="checkbox" ${reminder.enabled ? 'checked' : ''} 
                                   onchange="app.updateReminder('${type.id}', this.checked)">
                            <span style="font-size: 12px; color: #999;">Включено</span>
                        </label>
                    </div>
                    
                    ${type.timeField ?
                    `<div class="input-group">
                        <label style="font-size: 12px;">Время:</label>
                        <input type="time" id="time_${type.timeField}_${type.id}" value="${reminder[type.timeField] || type.defaultTime}"
                               onchange="app.updateReminderTime('${type.id}', '${type.timeField}', this.value)">
                    </div>` : ''}
                </div>`;
            });

            content.innerHTML = html;
        } catch (error) {
            console.error('Reminders load error:', error);
        }
    }

    async updateReminder(type, enabled) {
        try {
            await fetch(`${this.apiUrl}/api/reminders/update`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    type: type,
                    enabled: enabled ? 1 : 0
                })
            });
        } catch (error) {
            console.error('Update reminder error:', error);
        }
    }

    async updateReminderTime(type, timeField, time) {
        try {
            const data = {
                user_id: this.userId,
                type: type
            };

            // Устанавливаем время в зависимости от полей
            if (timeField === 'time_morning') {
                data.time_morning = time;
            } else if (timeField === 'time_evening') {
                data.time_evening = time;
            }

            await fetch(`${this.apiUrl}/api/reminders/update`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
        } catch (error) {
            console.error('Update reminder time error:', error);
        }
    }

    async openOperators() {
        this.showScreen('operatorsScreen');
        await this.loadOperators();
    }

    async loadOperators() {
        try {
            const response = await fetch(`${this.apiUrl}/api/operators/list?user_id=${this.userId}`);
            const data = await response.json();

            const list = document.getElementById('operatorsList');
            let html = '';

            data.operators.forEach(op => {
                if (op.is_admin) {
                    // Админ тоже может редактировать себя (но не удаляться)
                    html += `<div class="operator-item" style="background: #fff3cd;">
                        <div class="operator-info">
                            <span class="operator-color">${op.color_emoji}</span>
                            <div>
                                <div class="operator-name">${op.name} ${op.surname} <strong>(Админ)</strong></div>
                                <div class="operator-code">Код: ${op.code}</div>
                            </div>
                        </div>
                        <div class="operator-actions">
                            <button class="icon-btn" onclick="app.editOperatorModal(${op.id}, '${op.name}', '${op.surname}')">✏️</button>
                            <span style="color:#999; font-size:14px;">—</span>
                        </div>
                    </div>`;
                } else {
                    html += `<div class="operator-item">
                        <div class="operator-info">
                            <span class="operator-color">${op.color_emoji}</span>
                            <div>
                                <div class="operator-name">${op.name} ${op.surname}</div>
                                <div class="operator-code">Код: ${op.code}</div>
                            </div>
                        </div>
                        <div class="operator-actions">
                            <button class="icon-btn" onclick="app.editOperatorModal(${op.id}, '${op.name}', '${op.surname}')">✏️</button>
                            <button class="icon-btn" onclick="app.deleteOperator(${op.id})">🗑️</button>
                        </div>
                    </div>`;
                }
            });

            list.innerHTML = html || '<div style="text-align: center; color: #999; padding: 20px;">Нет операторов</div>';
        } catch (error) {
            console.error('Load operators error:', error);
        }
    }

    openModal(content) {
        const modal = document.getElementById('modal');
        document.getElementById('modalContent').innerHTML = content;
        modal.classList.add('active');
    }

    closeModal() {
        document.getElementById('modal').classList.remove('active');
    }

    openEventModal(period) {
        let html = `<div class="modal-header">
            ${period === 'morning' ? '🌅' : '🌆'} ${period === 'morning' ? 'Утро' : 'Вечер'}
        </div>`;

        html += `<div class="input-group">
            <label>Время события:</label>
            <div style="margin-bottom: 15px;">
                <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
                    <input type="checkbox" id="useCustomTime" onchange="app.toggleTimeInput(this.checked)">
                    <span>Указать своё время</span>
                </label>
            </div>
            <input type="time" id="customTime" style="display: none;" value="${period === 'morning' ? '10:00' : '19:00'}">
        </div>`;

        html += `<div class="input-group">
            <label>Название мероприятия:</label>
            <input type="text" id="eventTitle" placeholder="Например: Озвучка программы">
        </div>`;

        html += `<div class="modal-buttons">
            <button class="btn" onclick="app.createEvent('${period}')">✅ Создать</button>
            <button class="btn btn-secondary" onclick="app.closeModal()">❌ Отменить</button>
        </div>`;

        this.openModal(html);
    }

    toggleTimeInput(typeOrChecked) {
        const customInput = document.getElementById('customTime');
        if (typeof typeOrChecked === 'boolean') {
            customInput.style.display = typeOrChecked ? 'block' : 'none';
        } else {
            customInput.style.display = typeOrChecked === 'custom' ? 'block' : 'none';
        }
    }

    async createEvent(period) {
        const title = document.getElementById('eventTitle').value;
        let time = period === 'morning' ? '10:00' : '19:00';
        const useCustom = document.getElementById('useCustomTime')?.checked;
        if (useCustom) {
            time = document.getElementById('customTime').value;
        }

        if (!title) {
            alert('❌ Пожалуйста, введите название мероприятия');
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/api/events/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    date: this.selectedDate,
                    period: period,
                    time: time,
                    title: title
                })
            });

            const data = await response.json();

            if (data.success) {
                this.closeModal();
                alert('✅ Мероприятие создано!');
                await this.loadDayDetails(this.selectedDate);
            }
        } catch (error) {
            console.error('Create event error:', error);
            alert('❌ Ошибка при создании события');
        }
    }

    openRefusalModal(period) {
        let html = `<div class="modal-header">
            ${period === 'morning' ? '🌅' : '🌆'} Отказ от смены ${period === 'morning' ? 'утром' : 'вечером'}
        </div>`;

        html += `<div class="input-group">
            <label>Укажите причину отказа:</label>
            <textarea id="refusalReason" placeholder="Например: Плохое самочувствие, Срочные дела..." 
                      style="width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; 
                             font-family: inherit; resize: vertical; min-height: 100px;"></textarea>
        </div>`;

        html += `<div class="modal-buttons">
            <button class="btn" onclick="app.submitRefusal('${period}')">✅ Подтвердить отказ</button>
            <button class="btn btn-secondary" onclick="app.closeModal()">❌ Отменить</button>
        </div>`;

        this.openModal(html);
    }

    async submitRefusal(period) {
        const reason = document.getElementById('refusalReason').value;

        if (!reason) {
            alert('❌ Пожалуйста, укажите причину');
            return;
        }

        try {
            // Здесь должна быть логика отправки отказа
            this.closeModal();
            alert('✅ Ваш отказ от смены отправлен администратору');
            await this.loadDayDetails(this.selectedDate);
        } catch (error) {
            console.error('Refusal error:', error);
        }
    }

    createOperatorModal() {
        let html = `<div class="modal-header">➕ Создать нового оператора</div>`;

        html += `<div class="input-group">
            <label>Имя:</label>
            <input type="text" id="operatorName" placeholder="Например: Иван">
        </div>`;

        html += `<div class="input-group">
            <label>Фамилия:</label>
            <input type="text" id="operatorSurname" placeholder="Например: Петров">
        </div>`;

        html += `<div class="modal-buttons">
            <button class="btn" onclick="app.createOperator()">✅ Создать</button>
            <button class="btn btn-secondary" onclick="app.closeModal()">❌ Отменить</button>
        </div>`;

        this.openModal(html);
    }

    async createOperator() {
        const name = document.getElementById('operatorName').value;
        const surname = document.getElementById('operatorSurname').value;

        if (!name || !surname) {
            alert('❌ Пожалуйста, заполните все поля');
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/api/operators/create`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    name: name,
                    surname: surname
                })
            });

            const data = await response.json();

            if (data.success) {
                let html = `<div class="modal-header">✅ Оператор создан!</div>`;
                html += `<div style="text-align: center; padding: 20px;">
                    <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                        <div style="font-size: 32px; margin-bottom: 10px;">${data.operator.color_emoji}</div>
                        <div style="font-weight: 600; margin-bottom: 5px;">
                            ${data.operator.name} ${data.operator.surname}
                        </div>
                        <div style="color: #999; font-size: 14px; margin-bottom: 15px;">
                            Код доступа:
                        </div>
                        <div style="font-size: 24px; font-weight: 600; color: #667eea; letter-spacing: 2px;">
                            ${data.operator.code}
                        </div>
                    </div>
                    <p style="font-size: 12px; color: #999;">
                        ⚠️ Сохраните этот код! Оператор сможет войти только с этим кодом.
                    </p>
                </div>`;

                html += `<div class="modal-buttons">
                    <button class="btn" onclick="app.closeModal(); app.loadOperators();">✅ Готово</button>
                </div>`;

                document.getElementById('modalContent').innerHTML = html;
            }
        } catch (error) {
            console.error('Create operator error:', error);
            alert('❌ Ошибка при создании оператора');
        }
    }

    editOperatorModal(operatorId, name, surname) {
        let html = `<div class="modal-header">✏️ Редактировать оператора</div>`;

        html += `<div class="input-group">
            <label>Имя:</label>
            <input type="text" id="editOperatorName" placeholder="Имя" value="${name}">
        </div>`;

        html += `<div class="input-group">
            <label>Фамилия:</label>
            <input type="text" id="editOperatorSurname" placeholder="Фамилия" value="${surname}">
        </div>`;

        html += `<div class="modal-buttons">
            <button class="btn" onclick="app.updateOperator(${operatorId})">✅ Сохранить</button>
            <button class="btn btn-secondary" onclick="app.closeModal()">❌ Отменить</button>
        </div>`;

        this.openModal(html);
    }

    async updateOperator(operatorId) {
        const name = document.getElementById('editOperatorName').value;
        const surname = document.getElementById('editOperatorSurname').value;

        if (!name || !surname) {
            alert('❌ Пожалуйста, заполните все поля');
            return;
        }

        try {
            const response = await fetch(`${this.apiUrl}/api/operators/${operatorId}/update`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    name: name,
                    surname: surname
                })
            });

            const data = await response.json();

            if (data.success) {
                this.closeModal();
                await this.loadOperators();
            }
        } catch (error) {
            console.error('Update operator error:', error);
        }
    }

    async deleteOperator(operatorId) {
        if (confirm('⚠️ Вы уверены, что хотите удалить этого оператора?')) {
            try {
                const response = await fetch(
                    `${this.apiUrl}/api/operators/${operatorId}/delete?user_id=${this.userId}`,
                    { method: 'DELETE' }
                );

                const data = await response.json();

                if (data.success) {
                    await this.loadOperators();
                    alert('✅ Оператор удалён');
                }
            } catch (error) {
                console.error('Delete operator error:', error);
            }
        }
    }

    async deleteEvent(eventId, date) {
        if (confirm('⚠️ Вы уверены, что хотите удалить это мероприятие?')) {
            try {
                const response = await fetch(
                    `${this.apiUrl}/api/events/${eventId}/delete?user_id=${this.userId}`,
                    { method: 'DELETE' }
                );

                const data = await response.json();

                if (data.success) {
                    alert('✅ Мероприятие удалено');
                    await this.loadDayDetails(date);
                }
            } catch (error) {
                console.error('Delete event error:', error);
            }
        }
    }

    async openOperatorSelectModal(eventId) {
        try {
            // Получаем список операторов
            const response = await fetch(`${this.apiUrl}/api/operators/list?user_id=${this.userId}`);
            
            if (!response.ok) {
                alert('❌ Только администратор может назначать операторов');
                return;
            }
            
            const data = await response.json();

            let html = `<div class="modal-header">👥 Выберите оператора</div>`;
            html += `<div style="max-height: 300px; overflow-y: auto; margin-bottom: 15px;">`;

            // Показываем администратора первым с выделением
            const adminOp = data.operators.find(op => op.id === this.user.id);
            if (adminOp) {
                html += `<div class="operator-item" style="cursor: pointer; background: #fff3cd; border: 2px solid #ffc107;" onclick="app.assignOperator(${eventId}, ${adminOp.id})">
                    <div class="operator-info">
                        <span class="operator-color">${adminOp.color_emoji}</span>
                        <div>
                            <div class="operator-name"><strong>${adminOp.name} ${adminOp.surname} (Вы - Админ)</strong></div>
                        </div>
                    </div>
                    <span style="font-size: 20px;">→</span>
                </div>`;
            }

            // Остальные операторы
            data.operators.forEach(op => {
                // Пропускаем админа, так как уже добавили его выше
                if (op.id === this.user.id) return;
                
                html += `<div class="operator-item" style="cursor: pointer;" onclick="app.assignOperator(${eventId}, ${op.id})">
                    <div class="operator-info">
                        <span class="operator-color">${op.color_emoji}</span>
                        <div>
                            <div class="operator-name">${op.name} ${op.surname}</div>
                        </div>
                    </div>
                    <span style="font-size: 20px;">→</span>
                </div>`;
            });

            html += `</div>`;
            html += `<button class="btn btn-secondary" onclick="app.closeModal()">❌ Отменить</button>`;

            this.openModal(html);
        } catch (error) {
            console.error('Open operator select error:', error);
        }
    }

    async assignOperator(eventId, operatorId) {
        try {
            const response = await fetch(`${this.apiUrl}/api/events/${eventId}/assign`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: this.userId,
                    operator_id: operatorId
                })
            });

            const data = await response.json();

            if (data.success) {
                this.closeModal();
                alert('✅ Оператор назначен');
                await this.loadDayDetails(this.selectedDate);
            }
        } catch (error) {
            console.error('Assign operator error:', error);
        }
    }

    logout() {
        if (confirm('Вы уверены?')) {
            this.user = null;
            this.showScreen('loginScreen');
            document.getElementById('codeInput').value = '';
        }
    }

    showScreen(screenId) {
        // Скрываем все экраны
        document.querySelectorAll('.content').forEach(screen => {
            screen.classList.remove('active');
        });

        // Показываем нужный экран
        document.getElementById(screenId).classList.add('active');
    }
}

// Инициализируем приложение при загрузке страницы
let app;
document.addEventListener('DOMContentLoaded', () => {
    app = new ScheduleApp();
});
