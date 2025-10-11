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
            eventColor: '#10b981',
            eventTextColor: '#ffffff',
            eventTimeFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            },
            // Calendar sizing and performance
            height: '100%',
            contentHeight: 'auto',
            aspectRatio: 1.8,
            handleWindowResize: true,
            windowResizeDelay: 50,
            
            // Enhanced calendar settings
            dayMaxEvents: true,
            dayMaxEventRows: 8,
            views: {
                dayGridMonth: {
                    dayMaxEvents: 8,
                    dayPopoverFormat: { month: 'long', day: 'numeric', year: 'numeric' },
                    fixedWeekCount: false,
                    dayMinHeight: 70
                },
                timeGridWeek: {
                    slotMinTime: '00:00:00',
                    slotMaxTime: '24:00:00',
                    slotDuration: '00:15:00',
                    slotLabelFormat: {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false
                    },
                    allDaySlot: false,
                    slotEventOverlap: false,
                    scrollTime: '00:00:00',
                    slotLabelInterval: '01:00:00'
                },
                timeGridDay: {
                    slotMinTime: '00:00:00',
                    slotMaxTime: '24:00:00',
                    slotDuration: '00:15:00',
                    slotLabelFormat: {
                        hour: '2-digit',
                        minute: '2-digit',
                        hour12: false
                    },
                    allDaySlot: false,
                    slotEventOverlap: false,
                    scrollTime: '00:00:00',
                    slotLabelInterval: '01:00:00'
                }
            },
            
            // Better event rendering
            eventDidMount: (info) => {
                // Remove any default styles that might cause issues
                info.el.style.backgroundColor = '';
                info.el.style.backgroundImage = '';
                
                // Add consistent styling
                info.el.style.boxShadow = '0 1px 3px rgba(0, 0, 0, 0.3)';
                info.el.style.transition = 'all 0.3s ease';
                
                // Ensure text is readable
                const eventTitle = info.el.querySelector('.fc-event-title');
                if (eventTitle) {
                    eventTitle.style.color = 'white';
                    eventTitle.style.textShadow = '0 1px 2px rgba(0, 0, 0, 0.5)';
                    eventTitle.style.fontWeight = '600';
                    eventTitle.style.fontSize = '0.7rem';
                    eventTitle.style.lineHeight = '1.1';
                }

                // Add time display for events
                const eventTime = info.el.querySelector('.fc-event-time');
                if (eventTime) {
                    eventTime.style.fontWeight = '600';
                    eventTime.style.opacity = '0.9';
                    eventTime.style.fontSize = '0.65rem';
                }
                
                // Add tooltip with full event details
                const start = info.event.start;
                const end = info.event.end;
                let tooltip = info.event.title;
                
                if (start) {
                    const timeStr = this.formatEventTime(info.event);
                    tooltip += `\n${timeStr}`;
                }
                
                info.el.title = tooltip;
                
                // Highlight new events
                if (info.event.extendedProps.isNew) {
                    info.el.classList.add('fc-event-highlight');
                    setTimeout(() => {
                        info.event.setExtendedProp('isNew', false);
                    }, 6000);
                }
            },
            
            // Better date formatting
            titleFormat: { year: 'numeric', month: 'long' },
            slotLabelFormat: {
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
            }
        });

        this.calendar.render();
        
        // Ensure proper sizing after render
        setTimeout(() => {
            this.calendar.updateSize();
            this.initializeCalendarScroll();
        }, 100);
        
        // Also update on window resize
        window.addEventListener('resize', () => {
            setTimeout(() => {
                this.calendar.updateSize();
                this.initializeCalendarScroll();
            }, 50);
        });
    }

    initializeCalendarScroll() {
        // Initialize scroll position for timeGrid views
        const currentView = this.calendar.view;
        if (currentView.type === 'timeGridWeek' || currentView.type === 'timeGridDay') {
            // Scroll to 9 AM by default
            const scrollEl = document.querySelector('.fc-timegrid-body .fc-scroller');
            if (scrollEl) {
                // Calculate scroll position for 9 AM
                const nineAmPosition = 9 * 60; // 9 AM in minutes from midnight
                const slotHeight = 35; // Height of each time slot in pixels
                const scrollPosition = (nineAmPosition / 15) * (slotHeight / 4);
                
                scrollEl.scrollTop = scrollPosition;
            }
        }
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

        // Send message on button click
        sendButton.addEventListener('click', () => {
            this.sendMessage();
        });

        // Send message on Enter key
        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-focus input and scroll to bottom on load
        chatInput.focus();
        this.scrollChatToBottom();
        
        // Auto-resize textarea
        chatInput.addEventListener('input', () => {
            this.autoResizeTextarea(chatInput);
        });
    }

    autoResizeTextarea(textarea) {
        // Reset height to auto to get the correct scrollHeight
        textarea.style.height = 'auto';
        // Set the height to scrollHeight to fit content, with max height
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

        // Clear input and reset height
        chatInput.value = '';
        chatInput.style.height = 'auto';
        this.isProcessing = true;

        // Add user message to chat
        this.showMessage(message, 'user');

        // Show typing indicator
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

            // Remove typing indicator
            this.removeTypingIndicator();

            // Show bot responses
            data.messages.forEach(msg => {
                this.showMessage(msg, 'bot');
            });

            // Update current reservation state
            if (data.reservation) {
                this.currentReservation = data.reservation;
                
                // Show current reservation status
                if (this.currentReservation.title || this.currentReservation.start || this.currentReservation.end) {
                    let statusMsg = "Current reservation details:\n";
                    if (this.currentReservation.title) statusMsg += `• Name: ${this.currentReservation.title}\n`;
                    if (this.currentReservation.start) {
                        try {
                            const startDate = new Date(this.currentReservation.start);
                            statusMsg += `• Date: ${startDate.toLocaleDateString()}\n`;
                        } catch (e) {
                            statusMsg += `• Date: ${this.currentReservation.start}\n`;
                        }
                    }
                    if (this.currentReservation.end) {
                        try {
                            const endDate = new Date(this.currentReservation.end);
                            statusMsg += `• Time: ${endDate.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}\n`;
                        } catch (e) {
                            statusMsg += `• Time: ${this.currentReservation.end}\n`;
                        }
                    }
                    this.showMessage(statusMsg, 'bot');
                }
            }

            // If reservation is complete, reset for next one
            if (data.reservation_complete) {
                this.currentReservation = {};
                await this.loadReservations(true); // Refresh calendar with highlight
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

        // Convert newlines to <br> tags for bot messages
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

            // Convert reservations to FullCalendar events format
            const events = reservations.map((reservation, index) => {
                // Generate consistent color based on name
                const eventId = reservation.title + reservation.start;
                
                return {
                    id: eventId,
                    title: reservation.title,
                    start: reservation.start,
                    end: reservation.end,
                    allDay: reservation.allDay,
                    description: reservation.description,
                    extendedProps: {
                        isNew: highlightNew && index === reservations.length - 1
                    },
                    // Add color coding based on name
                    color: this.getEventColor(reservation.title)
                };
            });

            // Update calendar
            this.calendar.removeAllEvents();
            this.calendar.addEventSource(events);
            
            // Refresh calendar view
            this.calendar.render();

        } catch (error) {
            console.error('Error loading reservations:', error);
        }
    }

    getEventColor(title) {
        // Color coding based on names for better visual distinction
        const colors = {
            'john': '#10b981',
            'sarah': '#f59e0b', 
            'mike': '#ef4444',
            'emily': '#8b5cf6',
            'david': '#06b6d4'
        };
        
        if (!title) return '#6366f1';
        
        const lowerTitle = title.toLowerCase();
        for (const [name, color] of Object.entries(colors)) {
            if (lowerTitle.includes(name)) {
                return color;
            }
        }
        
        // Default color for other names
        return '#6366f1';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the chatbot when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new ReservationChatbot();
});