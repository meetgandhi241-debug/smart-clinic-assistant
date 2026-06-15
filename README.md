# Smart Clinic Assistant

🚧 Active Development Healthcare Management Project

Smart Clinic Assistant is a healthcare management system built using Python, Streamlit, and SQLite. The project helps manage patients, doctors, appointments, clinic operations, notifications, prescriptions, and basic AI-powered symptom analysis.

This project is being actively developed to explore real-world healthcare workflow management, clinic operations, appointment systems, and healthcare technology solutions. It serves as both a portfolio project and a foundation for future production-ready healthcare applications.
## Live Demo

Deployed Application:
https://smart-clinic-assistant-c6jqtwfgwusttwtjzibwhn.streamlit.app
---

## Project Status

✅ Active Development

Current Version Features:
Current Version Features:
- Patient Registration & Login
- Doctor Registration & Login
- Doctor Self Registration Portal
- Appointment Booking System
- Live Queue Tracker
- Family Health Dashboard
- Prescription Management
- Notification & Reminder System
- AI Symptom Checker
- Multi-Clinic Support
---

## Features Implemented

### Patient Module
- Patient Registration
- Patient Login
- Patient Dashboard
- Family Health Dashboard

### Doctor Module
- Doctor Registration
- Doctor Login
- Doctor Dashboard
- Live Queue Management
- Doctor Self Registration Portal
- Clinic Settings Management

### Appointment System
- Appointment Booking
- Automatic Queue Number Generation
- Appointment Tracking
- Doctor-wise Queue Management

### Clinic Management
- Small Clinic Management
- Multi-Clinic Support
- Clinic Association for Doctors
- Clinic-Based Data Isolation

### Notification System
- Patient Notifications
- Doctor Notifications
- Mark Notifications as Read
- Unread Notification Counter

### Prescription Management
- Prescription Creation
- Prescription Listing
- Appointment Linked Prescriptions

### AI Symptom Checker
- Rule-Based Symptom Analysis
- Disease Suggestions
- Specialist Recommendations
- Healthcare Guidance

---

## Technology Stack

### Frontend
- Streamlit

### Backend
- Python 3

### Database
- SQLite

### Libraries
- Streamlit
- Pandas
- SQLite3
- Datetime
- Re
- Standard Python Libraries

---

## Key Highlights

- Multi-Clinic Architecture
- Live Queue Tracking
- Appointment Reminder System
- Prescription Management
- Family Health Dashboard
- AI Symptom Analysis
- Doctor Self Registration
- Clinic-Based Data Isolation

---

## Project Structure

```text
smart-clinic-assistant/
│
├── app.py
├── database.py
├── requirements.txt
├── README.md
│
└── tests/
    ├── notifications_test.py
    ├── run_doctor_registration_test.py
    ├── manual_multiclinic_verify.py
    └── manual_notifications_verify.py
```

---

## Installation

### Clone Repository

```bash
git clone https://github.com/meetgandhi241-debug/smart-clinic-assistant.git
cd smart-clinic-assistant
```

### Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Run Application

```bash
streamlit run app.py
```

The application will automatically create the SQLite database on first launch.

---

## Testing

Run individual test scripts:

```bash
python tests/notifications_test.py

python tests/run_doctor_registration_test.py

python tests/manual_notifications_verify.py

python tests/manual_multiclinic_verify.py
```

These scripts verify:

- Notification workflows
- Doctor registration flows
- Appointment visibility
- Multi-clinic isolation
- Database migrations

---

## Multi-Clinic Support

The system supports multiple clinics through clinic-based data separation.

Features include:

- Clinic-specific appointments
- Clinic-specific notifications
- Clinic-specific prescriptions
- Doctor-clinic association
- Clinic-level queue management

---

## AI Symptom Checker

The AI Symptom Checker is currently rule-based.

Capabilities:

- Symptom keyword detection
- Disease prediction suggestions
- Specialist recommendations
- Basic healthcare guidance

Examples:

- Fever + Cough → Common Cold / Flu
- Chest Pain → Cardiologist Recommendation
- Headache → General Physician Recommendation

### Important Note

This feature is for educational purposes only and is **not a medical diagnosis tool**.

---

## Development Roadmap

### Completed

- ✅ Level 1 – Project Setup
- ✅ Level 2 – Home Page
- ✅ Level 3 – Patient Registration
- ✅ Level 4 – Patient Login
- ✅ Level 5 – Patient Dashboard
- ✅ Level 6 – Doctor Registration
- ✅ Level 7 – Doctor Login
- ✅ Level 8 – Appointment Booking
- ✅ Level 9 – Live Queue Tracker
- ✅ Level 10 – Family Health Dashboard
- ✅ Level 11 – Small Clinic Management
- ✅ Level 12 – AI Symptom Checker

### Planned Features

- 🔜 WhatsApp Appointment Reminders
- 🔜 Prescription Storage System
- 🔜 Advanced Multi-Clinic Portal
- 🔜 Doctor Self Registration Portal
- 🔜 Medical Record Uploads
- 🔜 Analytics Dashboard
- 🔜 Real-Time Notifications
- 🔜 Cloud Deployment

---

## Future Improvements

### Security
- Password Hashing
- Role-Based Access Control
- Session Management

### UI/UX
- Responsive Design
- Better Dashboards
- Improved Forms

### Database
- PostgreSQL Migration
- Cloud Database Support

### AI
- NLP-Based Symptom Analysis
- Confidence Scoring
- Advanced Medical Recommendations

---

## Screenshots

Screenshots will be added in future updates.

---

## Contributing

This project is under active development. Suggestions, issues, and pull requests are welcome.

Community feedback and contributions are appreciated as the platform continues to evolve..

---

## License

## License

All rights reserved.

This project is currently under active development.
---

## Author

**Meet Gandhi**

GitHub:
https://github.com/meetgandhi241-debug

Project:
Smart Clinic Assistant
