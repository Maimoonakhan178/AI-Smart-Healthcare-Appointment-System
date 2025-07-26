import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging

class HealthcareAI:
    def __init__(self):
        self._initialize_databases()
        self.session_data = {}

    def _initialize_databases(self):
        self.symptoms_db = self._load_symptom_data()
        self.emergency_keywords = self._load_emergency_keywords()
        self.greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings', 'howdy', "what's up"]
        self.duration_keywords = {
            'sudden': 'acute', 'suddenly': 'acute', 'immediate': 'acute',
            'chronic': 'chronic', 'ongoing': 'chronic', 'persistent': 'chronic',
            'continuous': 'chronic', 'weeks': 'chronic', 'months': 'chronic'
        }
        self.severity_modifiers = {
            'severe': 'high', 'extreme': 'high', 'intense': 'high',
            'unbearable': 'high', 'mild': 'low', 'slight': 'low', 'minor': 'low'
        }

    def _load_symptom_data(self) -> Dict[str, Dict]:
        return {
            'chest pain': {'severity': 'high', 'recommendation': 'emergency', 'category': 'cardiovascular'},
            'shortness of breath': {'severity': 'high', 'recommendation': 'emergency', 'category': 'respiratory'},
            'severe headache': {'severity': 'high', 'recommendation': 'emergency', 'category': 'neurological'},
            'headache': {'severity': 'low', 'recommendation': 'nurse', 'category': 'neurological'},
            'cough': {'severity': 'low', 'recommendation': 'nurse', 'category': 'respiratory'},
            'nausea': {'severity': 'low', 'recommendation': 'nurse', 'category': 'gastrointestinal'},
            'vomiting': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'gastrointestinal'},
            'abdominal pain': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'gastrointestinal'},
            'stomach pain': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'gastrointestinal'},
            'severe abdominal pain': {'severity': 'high', 'recommendation': 'emergency', 'category': 'gastrointestinal'},
            'back pain': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'musculoskeletal'},
            'severe back pain': {'severity': 'high', 'recommendation': 'emergency', 'category': 'musculoskeletal'},
            'dizziness': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'neurological'},
            'fatigue': {'severity': 'low', 'recommendation': 'nurse', 'category': 'general'},
            'fever': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'general'},
            'high fever': {'severity': 'high', 'recommendation': 'emergency', 'category': 'general'},
            'low-grade fever': {'severity': 'low', 'recommendation': 'nurse', 'category': 'general'},
            'rash': {'severity': 'low', 'recommendation': 'nurse', 'category': 'dermatological'},
            'sore throat': {'severity': 'low', 'recommendation': 'nurse', 'category': 'respiratory'},
            'runny nose': {'severity': 'low', 'recommendation': 'nurse', 'category': 'respiratory'},
            'diarrhea': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'gastrointestinal'},
            'constipation': {'severity': 'low', 'recommendation': 'nurse', 'category': 'gastrointestinal'},
            'blurred vision': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'neurological'},
            'palpitations': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'cardiovascular'},
            'joint pain': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'musculoskeletal'},
            'muscle aches': {'severity': 'low', 'recommendation': 'nurse', 'category': 'musculoskeletal'},
            'swollen ankles': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'cardiovascular'},
            'frequent urination': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'genitourinary'},
            'painful urination': {'severity': 'moderate', 'recommendation': 'gp', 'category': 'genitourinary'},
            'menstrual cramps': {'severity': 'low', 'recommendation': 'nurse', 'category': 'reproductive'},
            'breast pain': {'severity': 'low', 'recommendation': 'nurse', 'category': 'reproductive'}
        }

    def _load_emergency_keywords(self) -> List[str]:
        return [
            'chest pain', 'difficulty breathing', 'shortness of breath',
            'severe headache', 'sudden severe headache', 'unconscious', 
            'bleeding heavily', 'heavy bleeding', 'severe bleeding',
            'heart attack', 'stroke', 'severe allergic reaction',
            'loss of consciousness', 'seizure', 'confusion',
            'vomiting blood', 'coughing up blood', 'bloody stool',
            'severe abdominal pain', 'high fever', 'allergic reaction',
            'vision problems', 'severe back pain'
        ]


    def process_message(self, message: str, user_id: str = "default") -> str:
        try:
            message = message.strip().lower()
            if user_id not in self.session_data:
                self._start_new_session(user_id)

            self._log_user_message(user_id, message)

            if any(g in message for g in self.greetings):
                return self._greeting_response()
            if self._is_follow_up_question(message):
                return self._handle_follow_up(message, user_id)
            if (emergency := self._check_emergency_symptoms(message)):
                return self._emergency_response(emergency)
            if (symptoms := self._detect_symptoms_advanced(message)):
                self.session_data[user_id]['detected_symptoms'].extend(symptoms)
                return self._symptom_analysis_response(symptoms)
            if self._is_appointment_query(message):
                return self._appointment_help_response()
            if self._is_hours_query(message):
                return self._hours_response()
            if self._is_medication_query(message):
                return self._medication_response()
            if self._is_insurance_query(message):
                return self._insurance_response()

            return self._intelligent_default_response(message)

        except Exception as e:
            logging.error(f"Error: {e}")
            return self._error_response()

    def _start_new_session(self, user_id: str):
        self.session_data[user_id] = {
            'conversation_history': [],
            'detected_symptoms': [],
            'last_interaction': datetime.now()
        }

    def _log_user_message(self, user_id: str, message: str):
        self.session_data[user_id]['conversation_history'].append({
            'timestamp': datetime.now(),
            'message': message,
            'type': 'user'
        })

    def _detect_symptoms_advanced(self, message: str) -> List[Tuple[str, Dict, str]]:
        detected = []
        for symptom, data in self.symptoms_db.items():
            if symptom in message:
                severity = data['severity']
                for mod, sev in self.severity_modifiers.items():
                    if mod in message:
                        severity = sev
                        break
                duration = 'unknown'
                for dur, typ in self.duration_keywords.items():
                    if dur in message:
                        duration = typ
                        break
                detected.append((symptom, {**data, 'severity': severity}, duration))
        return detected

    def _check_emergency_symptoms(self, message: str) -> List[str]:
        return [kw for kw in self.emergency_keywords if kw in message]

    def _is_follow_up_question(self, message: str) -> bool:
        keywords = [
            'what should i do', 'how long', 'when should i', 'is this normal',
            'should i be worried', 'how serious', 'next steps', 'what if'
        ]
        return any(k in message for k in keywords)

    def _is_appointment_query(self, message: str) -> bool:
        return any(k in message for k in ['appointment', 'book', 'schedule'])

    def _is_hours_query(self, message: str) -> bool:
        return any(k in message for k in ['hours', 'open', 'when are you open'])

    def _is_medication_query(self, message: str) -> bool:
        return any(k in message for k in ['medication', 'drug', 'pill'])

    def _is_insurance_query(self, message: str) -> bool:
        return any(k in message for k in ['insurance', 'copay', 'coverage'])

    def _greeting_response(self) -> str:
        return "Hello! I'm your AI Health Assistant. Describe your symptoms so I can guide you."

    def _emergency_response(self, symptoms: List[str]) -> str:
        return f"EMERGENCY DETECTED: {', '.join(symptoms)}. Please call 911 or go to the ER immediately."

    def _symptom_analysis_response(self, symptoms: List[Tuple[str, Dict, str]]) -> str:
        lines = [f"{s.title()} (Severity: {d['severity'].title()}, Duration: {dur})" for s, d, dur in symptoms]
        return "Symptom(s) detected:\n" + '\n'.join(lines) + "\nPlease consider consulting a healthcare provider."

    def _appointment_help_response(self) -> str:
        return "To book an appointment, visit our website or call during business hours."

    def _hours_response(self) -> str:
        return "Clinic hours: Mon-Fri 8am-6pm, Sat 9am-4pm, Sun closed."

    def _medication_response(self) -> str:
        return "For medication advice, please consult your healthcare provider or pharmacist."

    def _insurance_response(self) -> str:
        return "Please bring your insurance card. Copay and coverage may vary by plan."

    def _intelligent_default_response(self, message: str) -> str:
        return "I'm here to assist with symptoms, appointments, and health info. Please describe how you're feeling."

    def _error_response(self) -> str:
        return "An error occurred. Please try again or rephrase your question."

    def get_session_summary(self, user_id: str = "default") -> Dict:
        session = self.session_data.get(user_id)
        if not session:
            return {"error": "No session found."}
        return {
            "interactions": len(session['conversation_history']),
            "symptoms": [s[0] for s in session['detected_symptoms']],
            "last_seen": session['last_interaction'].strftime("%Y-%m-%d %H:%M:%S")
        }

    def clear_session(self, user_id: str = "default") -> bool:
        return self.session_data.pop(user_id, None) is not None
