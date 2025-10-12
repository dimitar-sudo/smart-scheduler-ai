class ReservationChatbot {
    constructor() {
        this.calendar = null;
        this.currentReservation = {};
        this.isProcessing = false;
        this.initializeCalendar();
        this.setupEventListeners();
        this.loadReservations();
    }

    initializeCalendar() {
        const calendarEl = document.getElementById('calendar');
        
        this.calendar = new FullCalendar.Calendar(calendarEl, {
            initialView: 'dayGridMonth',
            headerToolbar: {
                left: 'prev,next today',
                center: 'title',
                right: 'dayGridMonth,timeGridWeek,timeGridDay'
            },
            themeSystem: 'standard',
            editable: false,
            selectable: false,
            events: [],
            eventClick: (info) => {
                const event = info.event;
                this.showEventDetails(event);
            },
            eventDisplay: 'block',
            eventTimeFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            },
            height: '100%',
            contentHeight: 'auto',
            aspectRatio: 1.5,
            handleWindowResize: true,
            windowResizeDelay: 50,
            
            dayMaxEvents: true,
            dayMaxEventRows: 6,
            views: {
                dayGridMonth: {
                    dayMaxEvents: 6,
                    dayPopoverFormat: { month: 'long', day: 'numeric', year: 'numeric' }
                },
                timeGridWeek: {
                    slotMinTime: '08:00:00',
                    slotMaxTime: '18:00:00',
                    slotDuration: '00:15:00',
                    slotLabelFormat: {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                    },
                    allDaySlot: false,
                    slotEventOverlap: false
                },
                timeGridDay: {
                    slotMinTime: '08:00:00',
                    slotMaxTime: '18:00:00',
                    slotDuration: '00:15:00',
                    slotLabelFormat: {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: true
                    },
                    allDaySlot: false,
                    slotEventOverlap: false
                }
            },
            
            eventDidMount: (info) => {
                info.el.style.boxShadow = '0 2px 4px rgba(0, 0, 0, 0.3)';
                info.el.style.transition = 'all 0.3s ease';
                
                const eventTitle = info.el.querySelector('.fc-event-title');
                if (eventTitle) {
                    eventTitle.style.color = 'white';
                    eventTitle.style.textShadow = '0 1px 2px rgba(0, 0, 0, 0.5)';
                    eventTitle.style.fontWeight = '600';
                    eventTitle.style.fontSize = '0.75rem';
                    eventTitle.style.lineHeight = '1.2';
                }

                const start = info.event.start;
                const end = info.event.end;
                let tooltip = info.event.title;
                
                if (start) {
                    const timeStr = this.formatEventTime(info.event);
                    tooltip += `\n${timeStr}`;
                }
                
                info.el.title = tooltip;
            }
        });

        this.calendar.render();
    }

    formatEventTime(event) {
        const start = event.start;
        const end = event.end;
        
        if (!start) return 'All day';
        
        const startTime = start.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: true 
        });
        
        if (!end) return startTime;
        
        const endTime = end.toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: true 
        });
        
        return `${startTime} - ${endTime}`;
    }

    showEventDetails(event) {
        const start = event.start;
        const end = event.end;
        const title = event.title;
        
        let details = `<strong>${title}</strong>`;
        
        if (start) {
            const dateStr = start.toLocaleDateString([], { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric' 
            });
            const timeStr = this.formatEventTime(event);
            details += `<br>📅 ${dateStr}`;
            details += `<br>⏰ ${timeStr}`;
        }
        
        if (event.extendedProps.description) {
            details += `<br>📝 ${event.extendedProps.description}`;
        }
        
        this.showMessage(details, 'bot');
    }

    setupEventListeners() {
        const chatInput = document.getElementById('chat-input');
        const sendButton = document.getElementById('send-button');

        sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        chatInput.focus();
        this.scrollChatToBottom();
        
        chatInput.addEventListener('input', () => {
            this.autoResizeTextarea(chatInput);
        });
    }

    autoResizeTextarea(textarea) {
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    scrollChatToBottom() {
        const chatMessages = document.getElementById('chat-messages');
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    async sendMessage() {
        const chatInput = document.getElementById('chat-input');
        const message = chatInput.value.trim();

        if (!message || this.isProcessing) return;

        chatInput.value = '';
        chatInput.style.height = 'auto';
        this.isProcessing = true;

        this.showMessage(message, 'user');
        this.showTypingIndicator();

        try {
            const response = await fetch('/process_reservation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    current_reservation: this.currentReservation
                })
            });

            const data = await response.json();
            this.removeTypingIndicator();

            data.messages.forEach(msg => {
                this.showMessage(msg, 'bot');
            });

            if (data.reservation) {
                this.currentReservation = data.reservation;
            }

            if (data.reservation_complete) {
                this.currentReservation = {};
                await this.loadReservations();
            }

        } catch (error) {
            this.removeTypingIndicator();
            this.showMessage('Sorry, there was an error processing your request. Please try again.', 'bot');
            console.error('Error:', error);
        } finally {
            this.isProcessing = false;
            chatInput.focus();
        }
    }

    showMessage(text, sender) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;

        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        const formattedText = sender === 'bot' ? text.replace(/\n/g, '<br>') : text;

        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${sender === 'bot' ? formattedText : this.escapeHtml(text)}</div>
                <div class="message-time">${timeString}</div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        this.scrollChatToBottom();
    }

    showTypingIndicator() {
        const chatMessages = document.getElementById('chat-messages');
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing-indicator';
        typingDiv.className = 'message bot-message';

        typingDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">
                    <div class="typing-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                </div>
            </div>
        `;

        chatMessages.appendChild(typingDiv);
        this.scrollChatToBottom();
    }

    removeTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    async loadReservations(highlightNew = false) {
        try {
            const response = await fetch('/get_reservations');
            const reservations = await response.json();

            console.log('Loaded reservations:', reservations);

            const events = reservations.map((reservation, index) => {
                const name = reservation.title ? reservation.title.toLowerCase() : '';
                const color = this.getEventColor(name);
                
                return {
                    id: `event-${index}-${Date.now()}`,
                    title: reservation.title || 'Unknown Appointment',
                    start: reservation.start,
                    end: reservation.end,
                    allDay: false,
                    color: color,
                    extendedProps: {
                        description: reservation.description || 'Reservation made via chatbot'
                    }
                };
            });

            console.log('Converted events:', events);

            this.calendar.removeAllEvents();
            if (events.length > 0) {
                events.forEach(event => {
                    try {
                        this.calendar.addEvent(event);
                    } catch (error) {
                        console.error('Error adding event:', error, event);
                    }
                });
            }

            this.calendar.render();

        } catch (error) {
            console.error('Error loading reservations:', error);
        }
    }

    getEventColor(name) {
        if (name.includes('john')) return '#10b981';
        if (name.includes('sarah')) return '#f59e0b';
        if (name.includes('mike')) return '#ef4444';
        if (name.includes('emily')) return '#8b5cf6';
        if (name.includes('david')) return '#06b6d4';
        return '#6366f1';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new ReservationChatbot();
});