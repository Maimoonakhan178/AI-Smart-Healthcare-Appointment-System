from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
from werkzeug.security import generate_password_hash, check_password_hash
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///healthcare.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models
class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_registered = db.Column(db.DateTime, default=datetime.utcnow)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

class Provider(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # GP, Nurse, Specialist
    specialty = db.Column(db.String(100))
    available = db.Column(db.Boolean, default=True)
    appointments = db.relationship('Appointment', backref='provider', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/booking')
def booking():
    providers = Provider.query.filter_by(available=True).all()
    return render_template('booking.html', providers=providers)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/dashboard')
def dashboard():
    # Get analytics data
    total_appointments = Appointment.query.count()
    total_patients = Patient.query.count()
    providers = Provider.query.all()
    recent_appointments = Appointment.query.order_by(Appointment.created_at.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         total_appointments=total_appointments,
                         total_patients=total_patients,
                         providers=providers,
                         recent_appointments=recent_appointments)

# API Routes
@app.route('/api/providers')
def get_providers():
    providers = Provider.query.filter_by(available=True).all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'type': p.type,
        'specialty': p.specialty,
        'available': p.available
    } for p in providers])

@app.route('/api/book_appointment', methods=['POST'])
def book_appointment():
    data = request.json
    
    # Check if patient exists, if not create new patient
    patient = Patient.query.filter_by(email=data['email']).first()
    if not patient:
        patient = Patient(
            name=data['name'],
            email=data['email'],
            phone=data['phone']
        )
        db.session.add(patient)
        db.session.flush()
    
    # Create appointment
    appointment_datetime = datetime.strptime(f"{data['date']} {data['time']}", "%Y-%m-%d %H:%M")
    
    appointment = Appointment(
        patient_id=patient.id,
        provider_id=data['provider_id'],
        appointment_date=appointment_datetime,
        reason=data['reason']
    )
    
    db.session.add(appointment)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Appointment booked successfully!'})

@app.route('/api/chat', methods=['POST'])
def chat():
    from ai_chatbot import HealthcareAI
    
    data = request.json
    message = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    # Initialize AI chatbot
    ai = HealthcareAI()
    response = ai.process_message(message)
    
    # Save chat session
    chat_session = ChatSession(
        session_id=session_id,
        message=message,
        response=response
    )
    db.session.add(chat_session)
    db.session.commit()
    
    return jsonify({'response': response})

@app.route('/api/analytics')
def get_analytics():
    # Calculate analytics data
    total_appointments = Appointment.query.count()
    completed_appointments = Appointment.query.filter_by(status='completed').count()
    cancelled_appointments = Appointment.query.filter_by(status='cancelled').count()
    
    # Monthly appointment data
    monthly_data = []
    for i in range(6):
        month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        count = Appointment.query.filter(
            Appointment.created_at >= month_start,
            Appointment.created_at < month_end
        ).count()
        monthly_data.append({
            'month': month_start.strftime('%b'),
            'appointments': count
        })
    
    return jsonify({
        'total_appointments': total_appointments,
        'completed_appointments': completed_appointments,
        'cancelled_appointments': cancelled_appointments,
        'monthly_data': list(reversed(monthly_data))
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Add sample data if tables are empty
        if Provider.query.count() == 0:
            providers = [
                Provider(name="Dr. Sarah Johnson", type="General Practitioner", specialty="Family Medicine"),
                Provider(name="Dr. Michael Chen", type="General Practitioner", specialty="Internal Medicine"),
                Provider(name="Nurse Emily Davis", type="Nurse Practitioner", specialty="Primary Care"),
                Provider(name="Dr. Robert Wilson", type="Specialist", specialty="Cardiology"),
                Provider(name="Dr. Lisa Anderson", type="Specialist", specialty="Dermatology")
            ]
            for provider in providers:
                db.session.add(provider)
            db.session.commit()
    
    app.run(debug=True)
