import os
import sys
import shutil
import sqlite3
import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import database

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.db'))
BACKUP = DB_PATH + '.bak'

# Backup existing DB and start fresh
if os.path.exists(DB_PATH):
    shutil.copy2(DB_PATH, BACKUP)
    os.remove(DB_PATH)

database.create_database()

failures = []

try:
    # 1. Create Clinic A and Clinic B
    cid_a = database.create_clinic('Clinic A', 'Address A')
    cid_b = database.create_clinic('Clinic B', 'Address B')

    print('Clinics created:', cid_a, cid_b)

    # 2. Register one doctor in each clinic
    d1_email = 'doc.a@example.com'
    d2_email = 'doc.b@example.com'
    try:
        database.register_doctor('Doctor A', d1_email, 'pw', 'General')
    except ValueError:
        pass
    try:
        database.register_doctor('Doctor B', d2_email, 'pw', 'General')
    except ValueError:
        pass
    d1 = database.get_doctor_by_email(d1_email)
    d2 = database.get_doctor_by_email(d2_email)
    # set clinic_id on them (doctor registration may not accept clinic_id)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('UPDATE doctors SET clinic_id=? WHERE id=?', (cid_a, d1[0]))
    cur.execute('UPDATE doctors SET clinic_id=? WHERE id=?', (cid_b, d2[0]))
    conn.commit()
    conn.close()

    print('Doctors assigned to clinics:', d1[0], '=>', cid_a, d2[0], '=>', cid_b)

    # 3. Create patients
    p1_email = 'pat.a@example.com'
    p2_email = 'pat.b@example.com'
    database.register_patient('Patient A', p1_email, 'pw')
    database.register_patient('Patient B', p2_email, 'pw')
    p1 = database.get_patient_profile('Patient A')
    p2 = database.get_patient_profile('Patient B')

    # 4. Book appointments in both clinics
    today = datetime.date.today().isoformat()
    database.create_appointment('Patient A', 'Doctor A', today, '09:00', clinic_id=cid_a)
    database.create_appointment('Patient B', 'Doctor B', today, '10:00', clinic_id=cid_b)

    # Also create cross-clinic appointment to test isolation
    database.create_appointment('Patient A', 'Doctor B', today, '11:00', clinic_id=cid_b)

    # 5. Verify doctors only see appointments from their own clinic
    appts_d1 = database.get_appointments_by_doctor('Doctor A', clinic_id=cid_a)
    appts_d1_all = database.get_appointments_by_doctor('Doctor A')
    appts_d2 = database.get_appointments_by_doctor('Doctor B', clinic_id=cid_b)

    print('Doctor A appointments (clinic-scoped):', appts_d1)
    print('Doctor A appointments (all):', appts_d1_all)
    print('Doctor B appointments (clinic-scoped):', appts_d2)

    if any(a[2] != 'Doctor A' for a in appts_d1):
        failures.append('Doctor A sees non-Doctor-A appointment in clinic-scoped query')
    if any(a[2] != 'Doctor B' for a in appts_d2):
        failures.append('Doctor B sees non-Doctor-B appointment in clinic-scoped query')

    # Ensure clinic-scoped query excludes other clinic: Doctor A should not see Doctor B's clinic appt
    if any((a[2] == 'Doctor B') for a in appts_d1_all) and any((a[2] == 'Doctor A') for a in appts_d1_all):
        # all results includes others; ensure clinic-scoped does not include cross-clinic
        if any((a[2] == 'Doctor B') for a in appts_d1):
            failures.append('Clinic-scoped appointments included other clinic appointments')

    # 6. Verify queues are clinic-specific
    queue_a = database.get_queue_for_doctor_date('Doctor A', today, clinic_id=cid_a)
    queue_b = database.get_queue_for_doctor_date('Doctor B', today, clinic_id=cid_b)
    queue_b_all = database.get_queue_for_doctor_date('Doctor B', today)
    print('Queue A:', queue_a)
    print('Queue B (scoped):', queue_b)
    print('Queue B (all):', queue_b_all)

    # queue entries should correspond to their clinics
    if any(q[2] != 'Doctor A' for q in queue_a):
        failures.append('Queue A contains entries not for Doctor A')
    if any(q[2] != 'Doctor B' for q in queue_b):
        failures.append('Queue B contains entries not for Doctor B')
    # ensure scoped queue excludes cross-clinic
    if any(q[2] == 'Doctor A' for q in queue_b):
        failures.append('Doctor B scoped queue includes Doctor A entries')

    # 7. Verify notifications are clinic-specific
    # create notifications with clinic tags
    database.create_notification('doctor', d1[0], 'Test A', 'Message A', clinic_id=cid_a)
    database.create_notification('doctor', d1[0], 'Test B', 'Message B', clinic_id=cid_b)
    notes_a = database.get_notifications('doctor', d1[0], unread_only=False, clinic_id=cid_a)
    notes_b = database.get_notifications('doctor', d1[0], unread_only=False, clinic_id=cid_b)
    print('Doctor A notes for clinic A:', notes_a)
    print('Doctor A notes for clinic B:', notes_b)
    if any(n[-1] != cid_a for n in notes_a if n[-1] is not None):
        failures.append('Notifications for clinic A include wrong clinic_id')
    if any(n[-1] != cid_b for n in notes_b if n[-1] is not None):
        failures.append('Notifications for clinic B include wrong clinic_id')

    # 8. Verify prescriptions are clinic-specific
    # create prescription linked to appointment (which has clinic)
    # find appointment id for Patient A at Doctor A
    appts = database.get_appointments_by_patient('Patient A')
    appt_a = None
    for a in appts:
        if a[2] == 'Doctor A' and a[7] == cid_a:
            appt_a = a
            break
    if not appt_a:
        failures.append('Could not find appointment for Patient A at Doctor A with clinic_id')
    else:
        database.create_prescription(appt_a[1], d1[0], appointment_id=appt_a[0])
        pres = database.get_prescriptions_by_patient(appt_a[1])
        print('Prescriptions for patient A:', pres)
        # prescription row ordering: id, patient_id, doctor_id, date, medicines, dosage, duration, notes, created_at, doctor_name
        # We check that created prescription has clinic_id inferred (join not returning clinic_id) — check raw DB
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute('SELECT clinic_id FROM prescriptions WHERE appointment_id=?', (appt_a[0],))
        row = cur.fetchone()
        conn.close()
        if not row or row[0] != cid_a:
            failures.append('Prescription did not inherit clinic_id from appointment')

    # 9. Verify old data migration works
    # Simulate legacy doctor without clinic_name/clinic_id
    # Insert legacy doctor manually
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("INSERT INTO doctors (name, email, password) VALUES (?, ?, ?)", ('Legacy Doc', 'legacy@example.com', 'pw'))
    lid = cur.lastrowid
    conn.commit()
    conn.close()
    # Run migrations again
    database.create_database()
    # Check doctor now has clinic_id
    legacy = database.get_doctor_by_email('legacy@example.com')
    # doctors tuple schema includes clinic_id at index 8 (0-based)
    if not legacy or (len(legacy) < 9 or legacy[8] is None):
        failures.append('Legacy doctor was not migrated to a clinic with clinic_id')

    # Report
    if failures:
        print('\nVERIFICATION FAILED:')
        for f in failures:
            print('-', f)
        sys.exit(2)
    else:
        print('\nAll multi-clinic verification checks passed.')

finally:
    # restore backup
    if os.path.exists(BACKUP):
        os.remove(DB_PATH)
        shutil.move(BACKUP, DB_PATH)
    else:
        pass
