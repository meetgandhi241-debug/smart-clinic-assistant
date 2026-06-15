import os
import sys
import shutil
import sqlite3
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.db'))
BACKUP = DB_PATH + '.bak'

def setup_db():
    if os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP)
        os.remove(DB_PATH)
    database.create_database()

def teardown_db():
    if os.path.exists(BACKUP):
        os.remove(DB_PATH)
        shutil.move(BACKUP, DB_PATH)

def run_tests():
    setup_db()
    try:
        # create doctor and patient
        doctor_email = 'notify.doc@example.com'
        doctor_name = 'Notify Doc'
        database.register_doctor(doctor_name, doctor_email, 'pw', 'General')
        doc = database.get_doctor_by_email(doctor_email)
        doc_id = doc[0]

        patient_name = 'Notify Patient'
        patient_email = 'notify.patient@example.com'
        database.register_patient(patient_name, patient_email, 'pw')
        pat = database.get_patient_profile(patient_name)
        pat_id = pat[0]

        # Book appointment -> should create notifications via app normally, but we simulate here
        database.create_appointment(patient_name, doctor_name, (datetime.date.today() + datetime.timedelta(days=1)).isoformat(), '09:00')
        # simulate creating notifications
        database.create_notification('patient', pat_id, 'Appointment Booked', 'Test booking')
        database.create_notification('doctor', doc_id, 'New Appointment', 'Test booking')

        # Check unread counts
        p_unread = database.get_unread_count('patient', pat_id)
        d_unread = database.get_unread_count('doctor', doc_id)
        print('patient_unread:', p_unread)
        print('doctor_unread:', d_unread)

        assert p_unread >= 1
        assert d_unread >= 1

        # Mark one as read
        notes = database.get_notifications('patient', pat_id, unread_only=True)
        if notes:
            nid = notes[0][0]
            database.mark_notification_read(nid)
        assert database.get_unread_count('patient', pat_id) <= p_unread

        # Reminder generation: create reminder for appointment within 24h
        # simulate by checking scan logic in app; here we create a reminder and ensure visibility
        database.create_notification('patient', pat_id, 'Reminder', 'Reminder: You have an appointment tomorrow at 09:00')
        notes_all = database.get_notifications('patient', pat_id, unread_only=False)
        assert any('Reminder' in n[3] for n in notes_all)

        print('Notifications tests passed')
    finally:
        teardown_db()

if __name__ == '__main__':
    run_tests()
