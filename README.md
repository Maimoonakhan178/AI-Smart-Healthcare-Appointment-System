# Healthcare Appointment System

A comprehensive healthcare appointment system built with Flask backend, HTML/CSS/JS frontend, and Python AI chatbot.

## Features

### 🏥 Patient Booking System
- Multi-step appointment booking process
- Provider selection (GPs, Nurses, Specialists)
- Date and time slot selection
- Patient information collection
- Appointment confirmation

### 🤖 AI Symptom Checker
- Quick symptom assessment with severity indicators
- AI-powered chatbot for detailed symptom analysis
- Intelligent triage recommendations
- Natural language processing for symptom understanding

### 📊 Analytics Dashboard
- Real-time appointment metrics
- Provider performance tracking
- Patient satisfaction monitoring
- System alerts and AI insights
- Interactive charts and visualizations

## Installation

1. **Clone the repository**
\`\`\`bash
git clone <repository-url>
cd healthcare-appointment-system
\`\`\`

2. **Create virtual environment**
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. **Install dependencies**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Initialize database**
\`\`\`bash
python scripts/create_sample_data.py
\`\`\`

5. **Run the application**
\`\`\`bash
python app.py
\`\`\`

6. **Access the application**
Open your browser and go to `http://localhost:5000`

## Project Structure

\`\`\`
healthcare-appointment-system/
├── app.py                 # Main Flask application
├── ai_chatbot.py         # AI chatbot logic
├── requirements.txt      # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css    # Main stylesheet
│   └── js/
│       ├── main.js      # Common JavaScript
│       ├── booking.js   # Booking functionality
│       ├── chatbot.js   # Chatbot functionality
│       └── dashboard.js # Dashboard functionality
├── templates/
│   ├── base.html        # Base template
│   ├── index.html       # Home page
│   ├── booking.html     # Booking page
│   ├── chatbot.html     # Chatbot page
│   └── dashboard.html   # Dashboard page
└── scripts/
    └── create_sample_data.py # Database initialization
\`\`\`

## Database Schema

### Tables
- **Patient**: Patient information and contact details
- **Provider**: Healthcare provider information and specialties
- **Appointment**: Appointment bookings and scheduling
- **ChatSession**: AI chatbot conversation history

## API Endpoints

### Patient Booking
- `GET /api/providers` - Get available healthcare providers
- `POST /api/book_appointment` - Book a new appointment

### AI Chatbot
- `POST /api/chat` - Send message to AI chatbot

### Analytics
- `GET /api/analytics` - Get dashboard analytics data

## AI Chatbot Features

The AI chatbot provides:
- **Symptom Analysis**: Intelligent assessment of patient symptoms
- **Triage Recommendations**: Guidance on appropriate care level
- **Emergency Detection**: Identification of urgent medical situations
- **General Health Information**: Answers to common health questions

### Recommendation Logic
- **Nurse Practitioner**: Basic symptoms, routine care
- **General Practitioner**: General health concerns, multiple symptoms
- **Specialist**: Complex symptoms requiring specialized care
- **Emergency**: Severe symptoms requiring immediate attention

## Dashboard Analytics

The dashboard provides insights on:
- **Appointment Metrics**: Total appointments, completion rates
- **Patient Analytics**: Active patients, satisfaction scores
- **Provider Performance**: Utilization rates, average duration
- **System Alerts**: Wait time warnings, capacity issues
- **AI Insights**: Automated recommendations for optimization

## Customization

### Adding New Symptoms
Edit `ai_chatbot.py` and update the `symptoms_db` dictionary:

```python
self.symptoms_db = {
    'new_symptom': {'severity': 'moderate', 'recommendation': 'gp'},
    # ... existing symptoms
}
