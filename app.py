import streamlit as st
import sqlite3
from database import create_database, register_patient, login_patient, register_doctor, login_doctor, create_appointment, get_doctors, get_appointments_by_doctor, get_patient_by_id, update_patient_profile, get_patient_profile, get_appointments_by_patient, update_appointment_status, add_family_member, get_family_members_by_patient, delete_family_member, update_family_member, set_clinic_settings, save_clinic_settings, get_clinic_settings, get_appointments_count_by_doctor_date, get_appointments_count_by_doctor_date_status, get_queue_for_doctor_date, get_current_active_queue_number, mark_next_patient, create_prescription, get_prescriptions_by_patient, get_doctor_by_email, create_notification, get_notifications, mark_notification_read, mark_all_notifications_read, get_unread_count, create_clinic, get_clinics, get_clinic_by_id
import datetime

st.set_page_config(page_title="Smart Clinic Assistant", page_icon="🏥", layout="wide")


def analyze_symptoms(symptoms_text: str):
    """Rule-based symptom analyzer. Returns (conditions, specialists).

    Matching is case-insensitive and works on comma-separated or free text.
    Detects: fever, cough, cold, headache, chest pain.
    Special handling: any occurrence of 'chest pain' recommends Cardiologist.
    """
    import re

    if not symptoms_text or not symptoms_text.strip():
        return [], []

    text = symptoms_text.lower()

    # Helper to test for whole-word presence (handles free text and comma-separated)
    def has_word(phrase):
        # phrase may contain spaces (e.g., 'chest pain'), so search for it as a phrase
        pattern = r"\b" + re.escape(phrase.lower()) + r"\b"
        return re.search(pattern, text) is not None

    conditions = []
    specialists = set()

    # Chest pain -> immediate cardiology referral
    if has_word('chest pain'):
        conditions.append('Chest Pain / Cardiac Concern')
        specialists.add('Cardiologist')

    # Fever and cough combination
    fever_present = has_word('fever')
    cough_present = has_word('cough')
    if fever_present and cough_present:
        conditions.extend(['Common Cold', 'Flu', 'Viral Fever'])
        specialists.add('General Physician')
    else:
        # Individual detections
        if fever_present:
            conditions.append('Fever')
            specialists.add('General Physician')
        if cough_present:
            conditions.append('Cough')
            specialists.add('General Physician')

    if has_word('cold'):
        conditions.append('Common Cold')
        specialists.add('General Physician')

    if has_word('headache'):
        conditions.append('Headache')
        specialists.add('General Physician')

    # Keep specialists list non-empty: default to General Physician
    if not specialists:
        specialists.add('General Physician')

    # Deduplicate conditions while preserving order
    seen = set()
    unique_conditions = []
    for c in conditions:
        if c not in seen:
            unique_conditions.append(c)
            seen.add(c)

    return unique_conditions, sorted(specialists)

# Ensure database exists
create_database()

# Initialize navigation state
if "page" not in st.session_state:
    st.session_state.page = "home"

# -----------------
# Home page
# -----------------
if st.session_state.page == "home":
    st.title("🏥 Smart Clinic Assistant")
    st.write("Welcome to Smart Clinic Assistant")
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("👤 Patient")

        if st.button("Patient Login"):
            st.session_state.page = "patient_login"
            st.rerun()

        if st.button("Patient Register"):
            st.session_state.page = "patient_register"
            st.rerun()

    with col2:
        st.subheader("👨‍⚕️ Doctor")

        if st.button("Doctor Login"):
            st.session_state.page = "doctor_login"
            st.rerun()

        if st.button("Doctor Register"):
            st.session_state.page = "doctor_register"
            st.rerun()

# -----------------
# Patient Registration
# -----------------
if st.session_state.page == "patient_register":
    st.title("👤 Patient Registration")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Register"):
            if name and email and password:
                register_patient(name, email, password)
                st.success("Registration Successful! You can now login.")
            else:
                st.error("Please fill all fields")

    with col2:
        if st.button("Back"):
            st.session_state.page = "home"
            st.rerun()

# -----------------
# Doctor Registration
# -----------------
if st.session_state.page == "doctor_register":
    st.title("👨‍⚕️ Doctor Registration")
    st.write("Please provide your clinic details to register.")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", key="doc_name")
        email = st.text_input("Email", key="doc_email")
        phone = st.text_input("Phone Number", key="doc_phone")
        specialization = st.text_input("Specialization", key="doc_specialization")
    with col2:
        reg_mode = st.radio("Clinic Option", ("Create New Clinic", "Join Existing Clinic"), key="clinic_mode")
        if reg_mode == "Create New Clinic":
            clinic_name = st.text_input("Clinic Name", key="doc_clinic")
            clinic_address = st.text_area("Clinic Address", key="doc_clinic_addr")
            selected_clinic_id = None
        else:
            clinics = get_clinics()
            if clinics:
                clinic_options = [f"{c[1]}" for c in clinics]
                sel = st.selectbox("Select Clinic to Join", clinic_options, key="join_clinic")
                selected_clinic_id = clinics[clinic_options.index(sel)][0]
                clinic_name = None
                clinic_address = None
            else:
                st.info("No existing clinics. Please create a new clinic.")
                clinic_name = st.text_input("Clinic Name", key="doc_clinic")
                clinic_address = st.text_area("Clinic Address", key="doc_clinic_addr")
                selected_clinic_id = None

        password = st.text_input("Password", type="password", key="doc_password")
        confirm = st.text_input("Confirm Password", type="password", key="doc_confirm")

    if st.button("Register Doctor"):
        # Validation
        if not all([name, email, phone, specialization, clinic_name, clinic_address, password, confirm]):
            st.error("All fields are required.")
        elif password != confirm:
            st.error("Password and Confirm Password do not match.")
        else:
            # Check unique email
            existing = get_doctor_by_email(email)
            if existing:
                st.error("An account with this email already exists.")
            else:
                try:
                    # Determine clinic_id: create if needed or use selected
                    if reg_mode == "Create New Clinic":
                        cid = create_clinic(clinic_name.strip(), clinic_address.strip() if clinic_address else None)
                    else:
                        cid = selected_clinic_id

                    conn_phone = phone.strip() if phone else None
                    # Insert doctor with clinic_id
                    from database import sqlite3 as _sqlite3
                    db = _sqlite3.connect("database.db")
                    cur = db.cursor()
                    cur.execute("INSERT INTO doctors (name, email, password, phone, specialization, clinic_name, clinic_address, clinic_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name.strip(), email.strip(), password, conn_phone, specialization.strip(), clinic_name.strip() if clinic_name else None, clinic_address.strip() if clinic_address else None, cid))
                    db.commit()
                    db.close()
                    st.success("Registration successful. Redirecting to login...")
                    st.session_state.page = "doctor_login"
                    st.rerun()
                except Exception as e:
                    st.error(f"Failed to register doctor: {e}")

    if st.button("Back"):
        st.session_state.page = "home"
        st.rerun()

# -----------------
# Doctor Login
# -----------------
if st.session_state.page == "doctor_login":
    st.title("🔐 Doctor Login")

    email = st.text_input("Email", key="doctor_login_email")
    password = st.text_input("Password", type="password", key="doctor_login_password")

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Login"):
            doctor = login_doctor(email, password)
            if doctor:
                st.session_state.doctor = doctor
                st.session_state.page = "doctor_dashboard"
                st.rerun()
            else:
                st.error("Invalid Email or Password")

    with col2:
        if st.button("Back"):
            st.session_state.page = "home"
            st.rerun()

# -----------------
# Patient Login
# -----------------
if st.session_state.page == "patient_login":
    st.title("🔐 Patient Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Login"):
            patient = login_patient(email, password)
            if patient:
                st.session_state.patient = patient
                st.session_state.page = "patient_dashboard"
                st.rerun()
            else:
                st.error("Invalid Email or Password")

    with col2:
        if st.button("Back"):
            st.session_state.page = "home"
            st.rerun()


if st.session_state.page == "patient_dashboard":
    # Require logged-in patient
    if "patient" not in st.session_state:
        st.warning("Please login first.")
        st.session_state.page = "patient_login"
        st.rerun()

    patient = st.session_state.patient
    patient_name = patient[1] if len(patient) > 1 else "Patient"

    st.title("🏥 Patient Dashboard")
    st.success("Login Successful!")
    st.write(f"Welcome, {patient_name}!")

    st.markdown("---")
    st.subheader("Book Appointment")

    if st.button("Health Profile"):
        st.session_state.page = "patient_profile"
        st.rerun()

    if st.button("Family Health Dashboard"):
        st.session_state.page = "family_dashboard"
        st.rerun()

    clinics = get_clinics()
    if not clinics:
        st.info("No clinics available. Please contact the clinic to register.")
    else:
        clinic_options = [f"{c[1]}" for c in clinics]
        sel_clinic = st.selectbox("Select Clinic", clinic_options)
        sel_idx = clinic_options.index(sel_clinic)
        clinic_id = clinics[sel_idx][0]

        doctors = get_doctors()
        # filter doctors by selected clinic
        clinic_doctors = [d for d in doctors if len(d) > 8 and d[8] == clinic_id]
        if not clinic_doctors:
            st.info("No doctors registered for this clinic.")
        else:
            doctor_options = [f"{d[1]} ({d[5]})" if len(d) > 5 and d[5] else d[1] for d in clinic_doctors]
            selected = st.selectbox("Select Doctor", doctor_options)
            selected_index = doctor_options.index(selected)
            doctor_obj = clinic_doctors[selected_index]
            doctor_name = doctor_obj[1]
            doctor_id = doctor_obj[0]

            appointment_date = st.date_input("Appointment Date")
            appointment_time = st.time_input("Appointment Time")

            if st.button("Book Appointment"):
                create_appointment(patient_name, doctor_name, appointment_date.isoformat(), appointment_time.strftime("%H:%M"), clinic_id=clinic_id)
                # create notifications for patient and doctor
                patient_profile = get_patient_profile(patient_name)
                patient_id = patient_profile[0] if patient_profile else None
                appt_time_str = appointment_time.strftime("%H:%M")
                create_notification('patient', patient_id, 'Appointment Booked', f'Your appointment with {doctor_name} on {appointment_date.isoformat()} at {appt_time_str} has been booked.', clinic_id=clinic_id)
                if doctor_id:
                    create_notification('doctor', doctor_id, 'New Appointment', f'New appointment booked by {patient_name} on {appointment_date.isoformat()} at {appt_time_str}.', clinic_id=clinic_id)
                st.success("Appointment booked successfully!")

    st.markdown("---")
    st.subheader("My Appointments")
    # Show patient's appointments with status
    patient_appointments = get_appointments_by_patient(patient_name)
    if patient_appointments:
        rows = [{"Doctor": a[2], "Date": a[3], "Time": a[4], "Queue": (a[5] if len(a) > 5 else None), "Status": (a[6] if len(a) > 6 else "Pending")} for a in patient_appointments]
        st.table(rows)
    else:
        st.info("You have no appointments.")

    # Reminders: simulate reminders for appointments within 24 hours
    try:
        now = datetime.datetime.now()
        for a in patient_appointments or []:
            appt_date = a[3]
            appt_time = a[4]
            try:
                appt_dt = datetime.datetime.fromisoformat(f"{appt_date}T{appt_time}")
            except Exception:
                # if time not iso, try combining
                appt_dt = None
            if appt_dt:
                delta = appt_dt - now
                if 0 < delta.total_seconds() <= 24 * 3600:
                    # check if similar reminder already exists
                    patient_id = st.session_state.patient[0]
                    clinic_for_appt = a[7] if len(a) > 7 else None
                    existing = get_notifications('patient', patient_id, unread_only=False, limit=50, clinic_id=clinic_for_appt)
                    msg = f"Reminder: You have an appointment tomorrow at {appt_time}"
                    found = any((r[4] == 'Reminder' or (isinstance(r[4], str) and r[4].startswith('Reminder'))) and msg in r[5] for r in existing)
                    if not found:
                        create_notification('patient', patient_id, 'Reminder', msg, clinic_id=clinic_for_appt)
    except Exception:
        pass

    st.markdown("---")
    st.subheader("AI Symptom Checker")
    st.write("Enter your symptoms (comma separated or free text). Example: 'fever, cough' or 'headache'.")
    symptoms_input = st.text_area("Describe your symptoms", value="", height=120, key="symptoms_input")
    if st.button("Analyze Symptoms"):
        if not symptoms_input or not symptoms_input.strip():
            st.error("Please enter symptoms to analyze.")
        else:
            conditions, specialists = analyze_symptoms(symptoms_input)
            st.markdown("**Possible Conditions:**")
            if conditions:
                for c in conditions:
                    st.write("- ", c)
            else:
                st.write("- No likely conditions detected.")

            st.markdown("**Recommended Specialist(s):**")
            if specialists:
                for s in specialists:
                    st.write("- ", s)
            else:
                st.write("- General Physician")

            st.warning("This is not a medical diagnosis. Consult a qualified doctor.")

    st.markdown("---")
    st.subheader("My Prescriptions")
    patient_id = patient[0]
    try:
        prescriptions = get_prescriptions_by_patient(patient_id)
    except Exception:
        prescriptions = []

    if prescriptions:
        pres_rows = []
        for p in prescriptions:
            pres_rows.append({
                "Doctor": p[9] if len(p) > 9 and p[9] else "Unknown",
                "Date": p[3] if len(p) > 3 else "",
                "Medicines": p[4] if len(p) > 4 and p[4] else "",
                "Dosage": p[5] if len(p) > 5 and p[5] else "",
                "Duration": p[6] if len(p) > 6 and p[6] else "",
                "Notes": p[7] if len(p) > 7 and p[7] else "",
            })
        st.table(pres_rows)
    else:
        st.info("You have no prescriptions.")

    # Recent Notifications widget
    st.markdown("---")
    st.subheader("Notifications")
    patient_id = patient[0]
    try:
        unread_count = get_unread_count('patient', patient_id)
    except Exception:
        unread_count = 0

    coln1, coln2 = st.columns([1, 3])
    with coln1:
        if st.button(f"🔔 {unread_count}", key='patient_bell'):
            st.session_state['show_patient_notifications'] = not st.session_state.get('show_patient_notifications', False)
            st.rerun()
    with coln2:
        st.write(f"Unread: {unread_count}")

    if st.session_state.get('show_patient_notifications'):
        notes = get_notifications('patient', patient_id, unread_only=False, limit=50)
        if notes:
            for n in notes:
                nid, _, _, title, message, is_read, created_at = n
                cols = st.columns([6,1])
                with cols[0]:
                    st.write(f"**{title}** — {message}  \n  _{created_at}_")
                with cols[1]:
                    if not is_read and st.button('Mark Read', key=f'markread_p_{nid}'):
                        mark_notification_read(nid)
                        st.rerun()
            if st.button('Mark all as read', key='patient_mark_all'):
                mark_all_notifications_read('patient', patient_id)
                st.rerun()
        else:
            st.info('No notifications')

    if st.button("Logout"):
        if "patient" in st.session_state:
            del st.session_state.patient
        st.session_state.page = "home"
        st.rerun()


# -----------------
# Patient Profile
# -----------------
if st.session_state.page == "patient_profile":
    if "patient" not in st.session_state:
        st.warning("Please login first.")
        st.session_state.page = "patient_login"
        st.rerun()

    patient = st.session_state.patient
    patient_id = patient[0]

    st.title("Patient Health Profile")

    # Prefill fields from patient tuple (schema: id, name, email, password, age, blood_group, phone, emergency_contact, address, medical_history, allergies)
    age_val = patient[4] if len(patient) > 4 else None
    blood_group_val = patient[5] if len(patient) > 5 else ""
    phone_val = patient[6] if len(patient) > 6 else ""
    emergency_contact_val = patient[7] if len(patient) > 7 else ""
    address_val = patient[8] if len(patient) > 8 else ""
    medical_history_val = patient[9] if len(patient) > 9 else ""
    allergies_val = patient[10] if len(patient) > 10 else ""

    age = st.number_input("Age", value=age_val if age_val is not None else 0, min_value=0, max_value=150, step=1, key="profile_age")
    blood_group = st.text_input("Blood Group", value=blood_group_val, key="profile_blood_group")
    phone = st.text_input("Phone", value=phone_val, key="profile_phone")
    emergency_contact = st.text_input("Emergency Contact", value=emergency_contact_val, key="profile_emergency")
    address = st.text_area("Address", value=address_val, key="profile_address")
    medical_history = st.text_area("Medical History", value=medical_history_val, key="profile_history")
    allergies = st.text_input("Allergies", value=allergies_val, key="profile_allergies")

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Save Profile"):
            # Save to DB
            update_patient_profile(patient_id, age, blood_group, phone, emergency_contact, address, medical_history, allergies)
            # Refresh session patient tuple
            st.session_state.patient = get_patient_by_id(patient_id)
            st.success("Profile saved successfully.")

    with col2:
        if st.button("Back"):
            st.session_state.page = "patient_dashboard"
            st.rerun()


# -----------------
# Family Health Dashboard (Patient)
# -----------------
if st.session_state.page == "family_dashboard":
    if "patient" not in st.session_state:
        st.warning("Please login first.")
        st.session_state.page = "patient_login"
        st.rerun()

    patient = st.session_state.patient
    patient_id = patient[0]
    patient_name = patient[1] if len(patient) > 1 else "Patient"

    st.title("Family Health Dashboard")
    st.write(f"Patient: {patient_name}")
    st.markdown("---")
    # show flash success messages set before a rerun
    if "family_flash" in st.session_state:
        st.success(st.session_state.pop("family_flash"))
    # Load patient's appointments so Live Queue can reference them
    patient_appointments = get_appointments_by_patient(patient_name)
    st.subheader("My Live Queue")
    # Show live queue info for today's appointment(s)
    today_iso = datetime.date.today().isoformat()
    todays_appts = [a for a in patient_appointments if len(a) > 3 and a[3] == today_iso]
    if todays_appts:
        # Use the first appointment for today's queue info
        my_appt = todays_appts[0]
        my_doctor = my_appt[2]
        my_queue = my_appt[5] if len(my_appt) > 5 and my_appt[5] is not None else None

        if my_queue is None:
            st.info("You are not in the live queue for today.")
        else:
            current_active = get_current_active_queue_number(my_doctor, today_iso)
            if current_active is None:
                current_active_display = 0
                current_active = 0
            else:
                current_active_display = current_active

            patients_ahead = my_queue - current_active
            if patients_ahead < 0:
                patients_ahead = 0

            estimated_wait_mins = patients_ahead * 5

            st.write(f"**Doctor:** {my_doctor}")
            st.write(f"**Your Queue #:** {my_queue}")
            st.write(f"**Current Patient #:** {current_active_display}")
            st.write(f"**Patients Ahead:** {patients_ahead}")
            st.write(f"**Estimated Wait:** {estimated_wait_mins} minutes")
    else:
        st.info("No appointments for today.")

    st.subheader("Add Family Member")
    member_name = st.text_input("Member Name", key="fm_name")
    relationship = st.text_input("Relationship", key="fm_relationship")
    age = st.number_input("Age", min_value=0, max_value=150, step=1, key="fm_age")
    blood_group = st.text_input("Blood Group", key="fm_blood")
    allergies = st.text_input("Allergies", key="fm_allergies")
    existing_conditions = st.text_area("Existing Conditions", key="fm_conditions")
    emergency_contact = st.text_input("Emergency Contact", key="fm_emergency")

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("Add Member"):
            # Validation
            if not member_name or not relationship:
                st.error("Please provide member name and relationship.")
            else:
                # Validate emergency contact if provided
                ec = emergency_contact.strip() if emergency_contact else ""
                if ec and (not ec.isdigit() or len(ec) != 10):
                    st.error("Emergency contact must be a valid 10-digit phone number.")
                else:
                    try:
                        add_family_member(patient_id, member_name, relationship, age if age else None, blood_group, allergies if allergies else None, existing_conditions if existing_conditions else None, ec if ec else None)
                        # persist success message across rerun and show immediately
                        st.session_state["family_flash"] = "Family member added successfully."
                        st.success("Family member added successfully.")
                        # Clear form fields
                        for k in ["fm_name","fm_relationship","fm_age","fm_blood","fm_allergies","fm_conditions","fm_emergency"]:
                            try:
                                del st.session_state[k]
                            except Exception:
                                pass
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to add member: {e}")

    with col2:
        if st.button("Back to Dashboard"):
            st.session_state.page = "patient_dashboard"
            st.rerun()

    st.markdown("---")
    st.subheader("My Family Members")
    members = get_family_members_by_patient(patient_id)
    if members:
        # Show table with extended fields
        rows = []
        for m in members:
            # m: (id, patient_id, member_name, relationship, age, blood_group, allergies, existing_conditions, emergency_contact)
            rows.append({"ID": m[0], "Name": m[2], "Relationship": m[3], "Age": m[4], "Blood Group": m[5], "Allergies": m[6] or "", "Existing Conditions": m[7] or "", "Emergency Contact": m[8] or ""})

        st.table(rows)

        # Provide Edit/Delete buttons per member
        for m in members:
            col_a, col_b, col_c = st.columns([4, 1, 1])
            with col_a:
                st.write(f"{m[2]} — {m[3]} — Age: {m[4]} — Blood Group: {m[5]}")
                if m[6]:
                    st.write(f"Allergies: {m[6]}")
                if m[7]:
                    st.write(f"Existing Conditions: {m[7]}")
                if m[8]:
                    st.write(f"Emergency Contact: {m[8]}")
            with col_b:
                if st.button("Edit", key=f"edit_member_{m[0]}"):
                    # populate edit state
                    st.session_state.edit_member_id = m[0]
                    st.session_state.edit_member_name = m[2]
                    st.session_state.edit_member_relationship = m[3]
                    st.session_state.edit_member_age = m[4] if m[4] is not None else 0
                    st.session_state.edit_member_blood = m[5] or ""
                    st.session_state.edit_member_allergies = m[6] or ""
                    st.session_state.edit_member_conditions = m[7] or ""
                    st.session_state.edit_member_emergency = m[8] or ""
                    st.rerun()
            with col_c:
                if st.button("Delete", key=f"del_member_{m[0]}"):
                    try:
                        delete_family_member(m[0])
                        st.session_state["family_flash"] = "Family member deleted successfully."
                        st.success("Family member deleted successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete member: {e}")

        # Edit form
        if "edit_member_id" in st.session_state:
            edit_id = st.session_state.edit_member_id
            st.markdown("---")
            st.subheader("Edit Family Member")
            ename = st.text_input("Member Name", value=st.session_state.get("edit_member_name", ""), key="edit_name")
            erel = st.text_input("Relationship", value=st.session_state.get("edit_member_relationship", ""), key="edit_relationship")
            eage = st.number_input("Age", min_value=0, max_value=150, value=st.session_state.get("edit_member_age", 0), key="edit_age")
            eblood = st.text_input("Blood Group", value=st.session_state.get("edit_member_blood", ""), key="edit_blood")
            eall = st.text_input("Allergies", value=st.session_state.get("edit_member_allergies", ""), key="edit_allergies")
            econ = st.text_area("Existing Conditions", value=st.session_state.get("edit_member_conditions", ""), key="edit_conditions")
            eemer = st.text_input("Emergency Contact", value=st.session_state.get("edit_member_emergency", ""), key="edit_emergency")

            colx, coly = st.columns([3,1])
            with colx:
                if st.button("Save Changes"):
                    # validation
                    if not ename or not erel:
                        st.error("Name and Relationship are required.")
                    else:
                        # Validate emergency contact if provided
                        ec_edit = eemer.strip() if eemer else ""
                        if ec_edit and (not ec_edit.isdigit() or len(ec_edit) != 10):
                            st.error("Emergency contact must be a valid 10-digit phone number.")
                        else:
                            try:
                                update_family_member(edit_id, member_name=ename, relationship=erel, age=eage if eage else None, blood_group=eblood if eblood else None, allergies=eall if eall else None, existing_conditions=econ if econ else None, emergency_contact=ec_edit if ec_edit else None)
                                # persist success message across rerun and show immediately
                                st.session_state["family_flash"] = "Family member updated successfully."
                                st.success("Family member updated successfully.")
                                # clear edit state
                                for k in ["edit_member_id","edit_member_name","edit_member_relationship","edit_member_age","edit_member_blood","edit_member_allergies","edit_member_conditions","edit_member_emergency"]:
                                    try:
                                        del st.session_state[k]
                                    except Exception:
                                        pass
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed to update member: {e}")
            with coly:
                if st.button("Cancel"):
                    for k in ["edit_member_id","edit_member_name","edit_member_relationship","edit_member_age","edit_member_blood","edit_member_allergies","edit_member_conditions","edit_member_emergency"]:
                        try:
                            del st.session_state[k]
                        except Exception:
                            pass
                    st.rerun()
    else:
        st.info("No family members added yet.")


# -----------------
# Doctor Dashboard
# -----------------
if st.session_state.page == "doctor_dashboard":
    if "doctor" not in st.session_state:
        st.warning("Please login first.")
        st.session_state.page = "doctor_login"
        st.rerun()

    doctor = st.session_state.doctor
    # doctor tuple: (id, name, email, password, phone, specialization, clinic_name, clinic_address, clinic_id)
    doctor_name = doctor[1] if len(doctor) > 1 else "Doctor"
    doctor_specialization = doctor[5] if len(doctor) > 5 else ""
    clinic_name = doctor[6] if len(doctor) > 6 else ""
    clinic_id = doctor[8] if len(doctor) > 8 else None

    st.title("Doctor Dashboard")
    st.success("Login Successful!")
    # show one-time flash for prescription save
    if "prescription_flash" in st.session_state:
        st.success(st.session_state.pop("prescription_flash"))
    st.write(f"Name: {doctor_name}")
    st.write(f"Specialization: {doctor_specialization}")
    if clinic_name:
        st.write(f"Clinic: {clinic_name}")

    # Notification bell + unread count
    try:
        doc_id = doctor[0]
        doc_unread = get_unread_count('doctor', doc_id, clinic_id=clinic_id)
    except Exception:
        doc_unread = 0
    coln1, coln2 = st.columns([1, 5])
    with coln1:
        if st.button(f"🔔 {doc_unread}", key='doctor_bell'):
            st.session_state['show_doctor_notifications'] = not st.session_state.get('show_doctor_notifications', False)
            st.rerun()
    with coln2:
        pass

    if st.session_state.get('show_doctor_notifications'):
        notes = get_notifications('doctor', doc_id, unread_only=False, limit=50, clinic_id=clinic_id)
        st.markdown('**Notifications**')
        if notes:
            for n in notes:
                # n: id, user_type, user_id, clinic_id, title, message, is_read, created_at
                nid, _, _, n_clinic, title, message, is_read, created_at = n
                cols = st.columns([6,1])
                with cols[0]:
                    st.write(f"**{title}** — {message}  \n  _{created_at}_")
                with cols[1]:
                    if not is_read and st.button('Mark Read', key=f'markread_d_{nid}'):
                        mark_notification_read(nid)
                        st.rerun()
            if st.button('Mark all as read', key='doctor_mark_all'):
                mark_all_notifications_read('doctor', doc_id, clinic_id=clinic_id)
                st.rerun()
        else:
            st.info('No notifications')

    # Show today's appointment stats
    today = datetime.date.today().isoformat()
    try:
        total_today = get_appointments_count_by_doctor_date(doctor_name, today)
        pending_today = get_appointments_count_by_doctor_date_status(doctor_name, today, "Pending", clinic_id=clinic_id)
        completed_today = get_appointments_count_by_doctor_date_status(doctor_name, today, "Completed", clinic_id=clinic_id)
        cancelled_today = get_appointments_count_by_doctor_date_status(doctor_name, today, "Cancelled", clinic_id=clinic_id)
    except Exception:
        total_today = pending_today = completed_today = cancelled_today = 0

    st.markdown("---")
    st.subheader("Today's Appointments")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Total", total_today)
    col_b.metric("Pending", pending_today)
    col_c.metric("Completed", completed_today)
    col_d.metric("Cancelled", cancelled_today)

    st.markdown("---")
    st.subheader("My Appointments")

    appointments = get_appointments_by_doctor(doctor_name)
    if appointments:
        # Interactive list with "View Profile" and status management per appointment
        for a in appointments:
            appt_id = a[0]
            patient_name = a[1]
            appt_date = a[3]
            appt_time = a[4]
            queue_number = a[5] if len(a) > 5 else None
            status = a[6] if len(a) > 6 else "Pending"

            col1, col2, col3 = st.columns([4, 2, 2])
            with col1:
                st.write(f"**Patient:** {patient_name}  —  **Date:** {appt_date}  —  **Time:** {appt_time}")
            with col2:
                st.write(f"**Status:** {status}")
                if queue_number is not None:
                    st.write(f"**Queue #**: {queue_number}")
            with col3:
                if st.button("View Profile", key=f"view_{appt_id}"):
                    profile = get_patient_profile(patient_name)
                    if profile:
                        st.session_state.profile_to_view = profile
                    else:
                        st.session_state.profile_to_view = None
                if st.button("Mark Completed", key=f"complete_{appt_id}"):
                    try:
                        update_appointment_status(appt_id, "Completed")
                        st.success("Appointment marked as Completed.")
                        # notify patient
                        profile = get_patient_profile(patient_name)
                        patient_id = profile[0] if profile else None
                        if patient_id:
                            create_notification('patient', patient_id, 'Appointment Completed', f'Your appointment on {appt_date} at {appt_time} has been completed.', clinic_id=clinic_id)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to update status: {e}")
                if st.button("Cancel", key=f"cancel_{appt_id}"):
                    try:
                        update_appointment_status(appt_id, "Cancelled")
                        st.success("Appointment cancelled.")
                        # notify patient and doctor
                        profile = get_patient_profile(patient_name)
                        patient_id = profile[0] if profile else None
                        if patient_id:
                            create_notification('patient', patient_id, 'Appointment Cancelled', f'Your appointment on {appt_date} at {appt_time} was cancelled.', clinic_id=clinic_id)
                        doctor_id = doctor[0]
                        create_notification('doctor', doctor_id, 'Appointment Cancelled', f'Appointment for {patient_name} on {appt_date} at {appt_time} was cancelled.', clinic_id=clinic_id)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to cancel appointment: {e}")
                # Allow writing a prescription for completed appointments
                if status == 'Completed':
                    if st.button("Write Prescription", key=f"write_{appt_id}"):
                        # find patient id
                        profile = get_patient_profile(patient_name)
                        patient_id = profile[0] if profile else None
                        st.session_state['prescribe_for'] = appt_id
                        st.session_state['prescribe_patient_id'] = patient_id
                        st.session_state['prescribe_patient_name'] = patient_name
                        st.session_state['prescribe_appt_date'] = appt_date
                        st.session_state['prescribe_appt_time'] = appt_time
                        st.session_state['prescribe_doctor_id'] = doctor[0]
                        st.rerun()

        # Display selected profile if any
        if "profile_to_view" in st.session_state:
            profile = st.session_state.profile_to_view
            if profile:
                st.markdown("---")
                st.subheader("Patient Profile")
                name = profile[1] if len(profile) > 1 else ""
                age = profile[4] if len(profile) > 4 else ""
                blood_group = profile[5] if len(profile) > 5 else ""
                phone = profile[6] if len(profile) > 6 else ""
                emergency_contact = profile[7] if len(profile) > 7 else ""
                address = profile[8] if len(profile) > 8 else ""
                medical_history = profile[9] if len(profile) > 9 else ""
                allergies = profile[10] if len(profile) > 10 else ""

                st.write("**Name:**", name)
                st.write("**Age:**", age)
                st.write("**Blood Group:**", blood_group)
                st.write("**Phone:**", phone)
                st.write("**Emergency Contact:**", emergency_contact)
                st.write("**Address:**", address)
                st.write("**Medical History:**", medical_history)
                st.write("**Allergies:**", allergies)

                if st.button("Close Profile"):
                    del st.session_state.profile_to_view
                    st.rerun()
            else:
                st.error("Patient profile not found.")
                if st.button("Dismiss"):
                    del st.session_state.profile_to_view
                    st.rerun()
    # Prescription form (shown when doctor clicked Write Prescription)
    if 'prescribe_for' in st.session_state:
        st.markdown('---')
        st.subheader('Write Prescription')
        appt_id = st.session_state.get('prescribe_for')
        presc_patient_id = st.session_state.get('prescribe_patient_id')
        presc_patient_name = st.session_state.get('prescribe_patient_name')
        presc_date = st.session_state.get('prescribe_appt_date')
        presc_doctor_id = st.session_state.get('prescribe_doctor_id')

        presc_time = st.session_state.get('prescribe_appt_time')
        st.write(f"Patient: {presc_patient_name}")
        st.write(f"Appointment ID: {appt_id}")
        st.write(f"Appointment Date: {presc_date}")
        st.write(f"Appointment Time: {presc_time}")
        medicines = st.text_area('Medicines (comma or newline separated)', key=f'medicines_{appt_id}')
        dosage = st.text_input('Dosage (e.g., 1 tablet twice a day)', key=f'dosage_{appt_id}')
        duration = st.text_input('Duration (e.g., 5 days)', key=f'duration_{appt_id}')
        notes = st.text_area('Notes', key=f'notes_{appt_id}')

        if st.button('Save Prescription', key=f'save_presc_{appt_id}'):
            # Validation
            if not medicines or not medicines.strip():
                st.error('Please enter at least one medicine.')
            elif not dosage or not dosage.strip():
                st.error('Please enter dosage information.')
            elif not duration or not duration.strip():
                st.error('Please enter duration.')
            else:
                try:
                    # Save with appointment linkage
                    create_prescription(presc_patient_id, presc_doctor_id, appointment_id=appt_id, date=presc_date, medicines=medicines.strip(), dosage=dosage.strip(), duration=duration.strip(), notes=notes.strip() if notes else None)
                    # set a flash message and redirect back to doctor dashboard
                    st.session_state['prescription_flash'] = 'Prescription saved successfully.'
                    for k in ['prescribe_for','prescribe_patient_id','prescribe_patient_name','prescribe_appt_date','prescribe_appt_time','prescribe_doctor_id']:
                        if k in st.session_state:
                            del st.session_state[k]
                    st.session_state['page'] = 'doctor_dashboard'
                    st.rerun()
                except Exception as e:
                    st.error(f'Failed to save prescription: {e}')
    else:
        st.write("No appointments yet.")

    if st.button("Logout"):
        if "doctor" in st.session_state:
            del st.session_state.doctor
        st.session_state.page = "home"
        st.rerun()


    # Clinic Settings section
    st.markdown("---")
    st.subheader("Live Queue Management")
    queue = get_queue_for_doctor_date(doctor_name, today, clinic_id=clinic_id)
    if queue:
        if st.button("Next Patient"):
            try:
                mark_next_patient(doctor_name, today, clinic_id=clinic_id)
                st.success("Moved to next patient.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to advance queue: {e}")

        # Show queue in order
        for q in queue:
            q_id = q[0]
            q_patient = q[1]
            q_num = q[5] if len(q) > 5 else None
            q_status = q[6] if len(q) > 6 else "Pending"

            col1, col2, col3 = st.columns([1, 3, 3])
            with col1:
                st.write(f"#{q_num}")
            with col2:
                st.write(f"{q_patient}")
            with col3:
                st.write(f"Status: {q_status}")
                if st.button("Start Consultation", key=f"start_{q_id}"):
                    try:
                        update_appointment_status(q_id, "In Progress")
                        st.success("Consultation started.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to start consultation: {e}")
                if st.button("Complete Consultation", key=f"complete_queue_{q_id}"):
                    try:
                        update_appointment_status(q_id, "Completed")
                        st.success("Consultation completed.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to complete consultation: {e}")
    else:
        st.write("No queue for today.")

    st.markdown("---")
    st.subheader("Clinic Settings")
    doctor_id = doctor[0]
    settings = get_clinic_settings(doctor_id)
    open_time_val = settings[2] if settings and len(settings) > 2 and settings[2] else None
    close_time_val = settings[3] if settings and len(settings) > 3 and settings[3] else None
    max_appts_val = settings[4] if settings and len(settings) > 4 and settings[4] is not None else 0

    # Use text inputs for times (HH:MM) to keep simple storage
    col1, col2, col3 = st.columns([2,2,1])
    with col1:
        open_time = st.text_input("Open Time (HH:MM)", value=open_time_val if open_time_val else "09:00", key="clinic_open")
    with col2:
        close_time = st.text_input("Close Time (HH:MM)", value=close_time_val if close_time_val else "17:00", key="clinic_close")
    with col3:
        max_appointments = st.number_input("Max/Day", min_value=0, value=max_appts_val if max_appts_val else 10, step=1, key="clinic_max")

    if st.button("Save Clinic Settings"):
        save_clinic_settings(
            doctor_id,
            open_time,
            close_time,
            max_appointments
        )
        st.success("Clinic settings saved successfully.")

