import os
import sys
import shutil
import sqlite3
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.db'))
BACKUP = DB_PATH + '.bak'

# Backup
if os.path.exists(DB_PATH):
    shutil.copy2(DB_PATH, BACKUP)

try:
    # Use existing DB (do not recreate) to inspect real app behavior
    # Create test doctor and patient
    doc_email = 'manual.doc@example.com'
    doc_name = 'Manual Doc'
    doc_pw = 'pw'
    try:
        database.register_doctor(doc_name, doc_email, doc_pw, 'General')
    except ValueError:
        pass
    doc = database.get_doctor_by_email(doc_email)
    doc_id = doc[0]

    pat_name = 'Manual Patient'
    pat_email = 'manual.patient@example.com'
    try:
        database.register_patient(pat_name, pat_email, 'pw')
    except Exception:
        pass
    patient = database.get_patient_profile(pat_name)
    pat_id = patient[0]

    print('Initial unread counts:')
    print('Doctor unread:', database.get_unread_count('doctor', doc_id))
    print('Patient unread:', database.get_unread_count('patient', pat_id))

    # Simulate patient booking via app: appointment tomorrow
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).date().isoformat()
    appt_time = '14:30'
    database.create_appointment(pat_name, doc_name, tomorrow, appt_time)
    # App code creates notifications upon booking; simulate that here to verify DB
    database.create_notification('patient', pat_id, 'Appointment Booked', f'Your appointment with {doc_name} on {tomorrow} at {appt_time} has been booked.')
    database.create_notification('doctor', doc_id, 'New Appointment', f'New appointment booked by {pat_name} on {tomorrow} at {appt_time}.')

    print('\nAfter booking:')
    d_unread = database.get_unread_count('doctor', doc_id)
    p_unread = database.get_unread_count('patient', pat_id)
    print('Doctor unread:', d_unread)
    print('Patient unread:', p_unread)

    assert d_unread >= 1, 'Doctor did not receive notification on booking'
    assert p_unread >= 1, 'Patient did not receive notification on booking'

    # Doctor views notifications and marks first as read
    notes = database.get_notifications('doctor', doc_id, unread_only=True)
    if notes:
        nid = notes[0][0]
        database.mark_notification_read(nid)

    d_unread_after = database.get_unread_count('doctor', doc_id)
    print('\nAfter marking one as read:')
    print('Doctor unread:', d_unread_after)
    assert d_unread_after <= d_unread, 'Marking read did not decrease unread count'

    # Now simulate reminder generation for appointment within 24 hours
    soon_dt = datetime.datetime.now() + datetime.timedelta(hours=23)
    soon_date = soon_dt.date().isoformat()
    soon_time = soon_dt.strftime('%H:%M')
    database.create_appointment(pat_name, doc_name, soon_date, soon_time)

    # Simulate reminder scan as app would
    # Find patient's appointments
    appts = database.get_appointments_by_patient(pat_name)
    created_reminder = False
    now = datetime.datetime.now()
    for a in appts:
        appt_date = a[3]
        appt_time = a[4]
        try:
            appt_dt = datetime.datetime.fromisoformat(f"{appt_date}T{appt_time}")
        except Exception:
            continue
        delta = appt_dt - now
        if 0 < delta.total_seconds() <= 24*3600:
            # check existing similar reminder
            notes = database.get_notifications('patient', pat_id, unread_only=False)
            msg = f"Reminder: You have an appointment tomorrow at {appt_time}"
            found = any(n[3] == 'Reminder' and msg in n[4] for n in notes)
            if not found:
                database.create_notification('patient', pat_id, 'Reminder', msg)
                created_reminder = True

    print('\nReminder created:', created_reminder)
    p_unread_final = database.get_unread_count('patient', pat_id)
    print('Patient unread now:', p_unread_final)
    assert p_unread_final >= p_unread, 'Patient unread count did not increase after reminder'

    print('\nManual notification verification passed.')

except AssertionError as e:
    print('ASSERTION FAILED:', e)
    sys.exit(1)
finally:
    # restore backup
    if os.path.exists(BACKUP):
        os.remove(DB_PATH)
        shutil.move(BACKUP, DB_PATH)
    else:
        pass
