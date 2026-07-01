# Smart Clinic Assistant 🏥

A comprehensive, modern healthcare platform designed to streamline clinic operations and empower patients with health management tools. Built with Streamlit, SQLite, and AI-driven clinical decision support.

---

## 📋 Project Description

**Smart Clinic Assistant** is an integrated healthcare management system that bridges the gap between patients and healthcare providers. It provides a unified platform for appointment management, medical record management, prescription tracking, medicine adherence monitoring, and AI-powered health insights.

The application supports **multi-clinic operations** with dedicated interfaces for both patients and healthcare professionals, enabling seamless coordination of care with real-time notifications, emergency SOS alerts, and preventive health risk assessments.

---

## ✨ Features

### Patient Features
- **User Authentication & Profile Management**: Secure registration and login with comprehensive health profile
- **Appointment Booking**: Schedule appointments with doctors across multiple clinics
- **Appointment Queue Management**: Real-time queue tracking and status updates
- **Medicine Management**: Add, edit, and track active medications with dosage and schedule details
- **Medicine Adherence Tracking**: Log daily medicine intake with Taken/Missed/Skipped status
- **Medical Reports Management**: Upload and organize medical reports (PDF, images) with notes
- **AI Report Analysis**: Automatic text extraction and intelligent analysis of medical reports
- **AI Symptom Checker**: Natural language symptom analysis with urgency assessment and specialist recommendations
- **Preventive Health Risk Assessment**: Rule-based health risk scoring with personalized recommendations
- **Health Timeline**: Comprehensive chronological view of all health events (appointments, reports, prescriptions, medicines)
- **Health Trends Dashboard**: Weekly and monthly health analytics with adherence and appointment trends
- **Family Health Management**: Track health information for family members
- **Emergency SOS System**: One-tap emergency alerts to care team and emergency contacts
- **Emergency Contacts Management**: Maintain and manage emergency contact information
- **Emergency Medical Card**: Generate downloadable PDF with critical health information
- **Prescription History**: View all prescriptions issued by doctors
- **Notifications System**: Real-time notifications for appointments, medicines, and health alerts

### Doctor Features
- **Doctor Authentication & Registration**: Register and join existing clinics
- **Clinic Management**: Create new clinics or join existing clinic networks
- **Clinic Settings**: Configure clinic hours and appointment limits
- **Patient Queue Management**: View real-time patient queue and status
- **Appointment Management**: Create, update, and manage patient appointments
- **Prescription Creation**: Issue prescriptions with medications and dosage details
- **Patient Search & Management**: Access patient profiles and health history
- **Multi-Clinic Support**: Manage patients across multiple clinics
- **Notifications**: Receive alerts for new appointments and patient SOS events

### Admin/Clinic Features
- **Multi-Clinic Architecture**: Support for multiple independent clinics
- **Clinic Settings Management**: Configure clinic hours, max appointments, and policies
- **Doctor Registration & Assignment**: Manage doctors and clinic assignments
- **Analytics & Reporting**: View clinic-level appointment and patient metrics

---

## 🛠️ Tech Stack

### Frontend & UI
- **Streamlit** (1.28.1) - Web application framework with responsive UI
- **Custom CSS** - Modern, professional styling with gradient headers and card-based layouts

### Backend & Database
- **Python 3.8+** - Core programming language
- **SQLite3** - Lightweight, file-based relational database
- **JSON** - Data serialization for complex fields

### Medical Document Processing
- **PyPDF2** (4.0.1) - PDF text extraction
- **Pillow** (10.1.0) - Image processing and manipulation
- **pytesseract** (0.3.10) - Optical Character Recognition (OCR) for scanned documents
- **fpdf2** (2.7.0) - PDF generation for reports and emergency cards

### Core Libraries
- **os, sys, pathlib** - File and path management
- **uuid** - Unique identifier generation
- **datetime, re, json** - Date/time, regex, and data handling

---

## 🏗️ Project Architecture

### Directory Structure
```
smart-clinic-assistant/
├── app.py                           # Main Streamlit application (3800+ lines)
├── database.py                      # SQLite database schema and operations
├── requirements.txt                 # Python dependencies
├── README.md                        # Project documentation
├── database.db                      # SQLite database (auto-created)
├── uploads/                         # User-uploaded medical reports
└── tests/                          # Test suite
    ├── auto_qa.py                  # Automated quality assurance tests
    ├── run_doctor_registration_test.py
    ├── manual_multiclinic_verify.py
    ├── manual_notifications_verify.py
    └── notifications_test.py
```

### Database Schema

**Core Tables:**
- `patients` - Patient profiles with health information
- `doctors` - Doctor information and specialization
- `clinics` - Clinic information and details
- `appointments` - Appointment scheduling and queue tracking
- `medicines` - Active medication records
- `medicine_adherence` - Daily medicine intake tracking
- `prescriptions` - Doctor-issued prescriptions

**Medical Records:**
- `medical_reports` - Uploaded medical documents
- `medical_report_analyses` - AI-generated report analyses

**Health Management:**
- `family_members` - Family health information
- `emergency_contacts` - Emergency contact records
- `sos_events` - Emergency SOS alert history

**Clinic Operations:**
- `clinic_settings` - Clinic configuration and hours
- `notifications` - System notifications for patients and doctors

### Application Flow

```
Home Page
├── Patient Portal
│   ├── Registration/Login
│   ├── Dashboard (Quick Actions, Appointments, Medicines)
│   ├── Appointment Booking
│   ├── Medicine Management & Adherence Tracking
│   ├── Medical Reports Upload & AI Analysis
│   ├── AI Symptom Checker
│   ├── Preventive Health Risk Assessment
│   ├── Health Trends & Analytics
│   ├── Family Health Management
│   ├── Emergency SOS System
│   └── Health Timeline View
│
└── Doctor Portal
    ├── Registration/Login
    ├── Clinic Management
    ├── Dashboard
    ├── Patient Queue
    ├── Appointment Management
    └── Prescription Creation
```

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Tesseract OCR (optional, for image-based document processing)
- Git (for version control)

### Step 1: Clone or Download the Project

```bash
git clone https://github.com/yourusername/smart-clinic-assistant.git
cd smart-clinic-assistant
```

Or download the ZIP file and extract it.

### Step 2: Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 4: Optional - Install Tesseract for OCR

**On macOS (using Homebrew):**
```bash
brew install tesseract
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr
```

**On Windows:**
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki

---

## 🚀 Running the Application

### Start the Streamlit Development Server

```bash
streamlit run app.py
```

The application will be available at: **http://localhost:8501**

### Access the Application

Open your web browser and navigate to `http://localhost:8501`

---

## 👤 Demo Accounts

After first run, create accounts through the registration interface:

### Sample Patient Account
- **Name**: Demo Patient
- **Email**: patient@demo.com
- **Password**: demo123

### Sample Doctor Account
- **Name**: Dr. Smith
- **Email**: doctor@demo.com
- **Password**: demo123
- **Specialization**: General Medicine
- **Clinic**: Demo Clinic

**Note**: These are sample credentials. For production, use strong passwords and implement proper security measures.

---

## 📁 Folder Structure Explained

```
├── app.py
│   ├── UI Components (Page Headers, Navigation, Cards)
│   ├── Patient Portal (Registration, Login, Dashboard)
│   ├── Doctor Portal (Registration, Login, Dashboard)
│   ├── Appointment Management
│   ├── Medical Records (Upload, Display, Delete)
│   ├── AI Features
│   │   ├── Symptom Analysis
│   │   ├── Report Analysis
│   │   └── Risk Assessment
│   ├── Health Analytics & Timeline
│   └── Emergency SOS System
│
├── database.py
│   ├── Database Initialization
│   ├── User Management (Patients, Doctors)
│   ├── Appointment Operations
│   ├── Medicine Management
│   ├── Medical Records
│   ├── Prescription Management
│   ├── Notification System
│   └── SOS Event Tracking
│
├── uploads/
│   └── [User-uploaded medical reports stored here]
│
├── tests/
│   ├── auto_qa.py (Automated testing suite)
│   └── [Manual verification tests]
│
└── database.db
    └── [SQLite database - auto-created on first run]
```

---

## 🎨 Screenshots Section

### Home Page
![Home Page Placeholder - Welcome screen with Patient and Doctor login options]

### Patient Dashboard
![Patient Dashboard Placeholder - Quick actions, appointments, and medicines overview]

### Medicine Adherence Tracker
![Medicine Tracker Placeholder - Daily dose logging and adherence analytics]

### AI Symptom Checker
![Symptom Checker Placeholder - Natural language symptom input and analysis]

### Health Trends Dashboard
![Health Trends Placeholder - Weekly/monthly health score and analytics]

### Emergency SOS System
![Emergency SOS Placeholder - Emergency alert and contact management interface]

### Doctor Queue Management
![Doctor Queue Placeholder - Real-time patient queue view]

### Medical Reports Portal
![Medical Reports Placeholder - Upload and AI analysis of medical documents]

---

## 🚀 Deployment Instructions

### Option 1: Deploy to Streamlit Community Cloud (Recommended)

**Prerequisites:**
- GitHub account with the code repository
- Streamlit account (free at streamlit.io)

**Steps:**

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. Go to [Streamlit Cloud](https://streamlit.io/cloud)

3. Click "New app" and connect your GitHub repository

4. Configure deployment:
   - **Repository**: yourusername/smart-clinic-assistant
   - **Branch**: main
   - **Main file path**: app.py

5. Click "Deploy" and wait for the application to build

6. Your app will be available at: `https://your-app-name.streamlit.app`

**Environment Variables (if needed):**
Set in Streamlit Cloud dashboard → Advanced Settings → Secrets

### Option 2: Deploy to Cloud Platforms

**AWS/Google Cloud/Azure:**
- Create a Docker container with Python 3.8+
- Install dependencies from requirements.txt
- Expose port 8501
- Configure persistent storage for database.db and uploads/

**Example Dockerfile:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Important Notes for Production:

1. **Database**: Move from SQLite to PostgreSQL/MySQL for multi-user scaling
2. **Security**: 
   - Implement hashed password storage (bcrypt)
   - Add SSL/TLS encryption
   - Enable CORS headers properly
3. **File Storage**: Use cloud storage (S3, GCS) instead of local uploads/
4. **Backups**: Implement automated database backups
5. **Monitoring**: Set up error tracking and performance monitoring
6. **Authentication**: Consider OAuth2 or LDAP integration

---

## 📈 Future Enhancements

### Planned Features (Roadmap)
- **Video Consultations**: Integrated telemedicine for remote appointments
- **Mobile Application**: Native iOS/Android apps
- **Advanced Analytics**: Predictive health analytics with ML
- **Insurance Integration**: Insurance claim processing and verification
- **Lab Integration**: Real-time lab result synchronization
- **Prescription Marketplace**: Integrated pharmacy ordering
- **Wearable Integration**: Sync with smartwatches and fitness trackers
- **Multi-language Support**: Internationalization (i18n)
- **Voice Assistant**: AI voice-based symptom checker
- **Telemedicine Billing**: Automated appointment billing and payment processing
- **Integration with EMR Systems**: HL7 and FHIR standards compliance
- **Advanced Reporting**: Clinical dashboards and KPIs for clinic management

### Technical Improvements
- Migrate to PostgreSQL for enterprise scalability
- Implement Redis caching layer
- Add comprehensive logging and monitoring
- Containerization with Docker and Kubernetes support
- GraphQL API layer for mobile app
- Automated CI/CD pipeline with GitHub Actions

---

## 📄 License

**All Rights Reserved © 2026**

This project and all its contents are proprietary and confidential. Unauthorized copying, modification, distribution, or use of this project is strictly prohibited without explicit written permission from the copyright holder.

---

## 👨‍💼 Author

**Meet Gandhi**

Healthtech Developer | Healthcare Software Engineer

---

## 🤝 Support

For issues, feature requests, or technical support:
1. Check existing documentation
2. Review the troubleshooting section in app.py comments
3. Check test files for usage examples
4. Contact the development team

---

## 📚 Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [PyPDF2 Guide](https://github.com/py-pdf/pypdf)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)

---

**Last Updated**: July 2026  
**Version**: 1.0.0  
**Status**: Production Ready
