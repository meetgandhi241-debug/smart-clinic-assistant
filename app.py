import os
import uuid
from pathlib import Path

import streamlit as st
import sqlite3
import json
from database import (
    create_database,
    register_patient,
    login_patient,
    register_doctor,
    login_doctor,
    create_appointment,
    get_doctors,
    get_appointments_by_doctor,
    get_patient_by_id,
    update_patient_profile,
    get_patient_profile,
    get_appointments_by_patient,
    update_appointment_status,
    add_family_member,
    get_family_members_by_patient,
    delete_family_member,
    update_family_member,
    set_clinic_settings,
    save_clinic_settings,
    get_clinic_settings,
    get_appointments_count_by_doctor_date,
    get_appointments_count_by_doctor_date_status,
    get_queue_for_doctor_date,
    get_current_active_queue_number,
    mark_next_patient,
    create_prescription,
    get_prescriptions_by_patient,
    get_prescriptions_by_doctor,
    get_analyses_by_patient_ids,
    get_doctor_by_email,
    create_notification,
    get_notifications,
    mark_notification_read,
    mark_all_notifications_read,
    get_unread_count,
    create_clinic,
    get_clinics,
    get_clinic_by_id,
    insert_medical_report,
    get_reports_by_patient,
    delete_medical_report,
    insert_report_analysis,
    get_analyses_by_report,
    get_analyses_by_patient,
    delete_report_analysis,
    create_medicine,
    get_medicine_by_id,
    get_medicines_by_patient,
    update_medicine,
    delete_medicine,
    record_medicine_adherence,
    get_adherence_history,
    get_medicine_adherence_summary,
    get_patient_active_medicines,
    get_medicines_by_doctor,
    add_emergency_contact,
    get_emergency_contacts,
    update_emergency_contact,
    delete_emergency_contact,
    create_sos_event,
    get_sos_events,
    get_recent_sos_alerts,
)
from fpdf import FPDF
from io import BytesIO
import datetime

st.set_page_config(page_title="Smart Clinic Assistant", page_icon="🏥", layout="wide")


def load_app_style():
    st.markdown(
        """<style>
        :root {
            --bg: #f3f8ff;
            --surface: #ffffff;
            --surface-strong: #f8fbff;
            --primary: #0b63d5;
            --primary-soft: #dbeafe;
            --success: #10b981;
            --success-soft: #d1fae5;
            --accent: #047857;
            --text: #0f172a;
            --muted: #475569;
            --border: rgba(15, 23, 42, 0.08);
        }
        .main .block-container {
            padding-top: 0.75rem;
            padding-bottom: 0.75rem;
            padding-left: 1.25rem;
            padding-right: 1.25rem;
            max-width: 1600px;
        }
        .page-header {
            background: linear-gradient(180deg, rgba(14,165,233,0.12), rgba(255,255,255,0.95));
            border: 1px solid rgba(14,165,233,0.18);
            border-radius: 24px;
            padding: 20px 28px;
            margin-bottom: 1rem;
            box-shadow: 0 16px 40px rgba(15,23,42,0.06);
        }
        .page-header h1 {
            margin: 0;
            color: var(--text);
            font-size: 2.75rem;
            line-height: 1.05;
        }
        .page-header p {
            margin: 0.5rem 0 0;
            color: var(--muted);
            font-size: 1rem;
            max-width: 780px;
        }
        .section-card {
            border-radius: 22px;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 20px;
            box-shadow: 0 14px 28px rgba(15,23,42,0.04);
            margin-bottom: 0.875rem;
        }
        .section-card h2 {
            margin-top: 0;
        }
        .metric-card {
            border-radius: 22px;
            background: linear-gradient(135deg, rgba(214,234,255,0.8), rgba(236,253,245,0.9));
            border: 1px solid rgba(14,165,233,0.16);
            padding: 16px 18px;
            min-height: 110px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 12px 24px rgba(15,23,42,0.04);
        }
        .metric-card .metric-icon {
            font-size: 1.7rem;
        }
        .metric-card .metric-value {
            font-size: 2rem;
            font-weight: 700;
            margin: 0.4rem 0;
            color: var(--text);
        }
        .metric-card .metric-label {
            color: var(--muted);
            font-size: 0.95rem;
        }
        .sidebar-card {
            border-radius: 20px;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 16px 14px;
            margin-bottom: 0.75rem;
        }
        .sidebar-link {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 14px;
            border-radius: 14px;
            color: var(--text);
            text-decoration: none;
            transition: background 0.2s ease, color 0.2s ease;
            margin-bottom: 6px;
        }
        .sidebar-link:hover {
            background: rgba(14,165,233,0.08);
            color: var(--primary);
        }
        .sidebar-link.active {
            background: rgba(14,165,233,0.16);
            color: var(--primary);
            font-weight: 600;
        }
        .button-primary button {
            background-color: var(--primary) !important;
            color: white !important;
            border-radius: 12px !important;
            padding: 12px 20px !important;
            border: none !important;
        }
        .button-primary button:hover {
            background-color: #0849a1 !important;
        }
        .empty-state {
            border-radius: 22px;
            padding: 18px;
            text-align: center;
            background: rgba(236,249,255,0.8);
            border: 1px dashed rgba(14,165,233,0.24);
            color: var(--text);
        }
        .empty-state h3 {
            margin: 0 0 8px;
            font-size: 1.3rem;
        }
        .empty-state p {
            margin: 0;
            color: var(--muted);
        }
        .stAlert {
            border-radius: 18px !important;
        }
        .card-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 14px;
            margin-bottom: 0.875rem;
        }
        .table-responsive,
        .report-table,
        .stTable {
            overflow-x: auto;
            width: 100%;
        }
        .table-responsive table {
            width: 100%;
            border-collapse: collapse;
        }
        .button-primary button,
        .stButton button,
        button {
            min-height: 48px !important;
            border-radius: 14px !important;
            font-size: 1rem !important;
            padding: 14px 20px !important;
        }
        input,
        textarea,
        select {
            min-height: 44px !important;
            font-size: 1rem !important;
        }
        [data-testid="stSidebar"],
        section[data-testid="stSidebar"],
        div[aria-label="Sidebar"] {
            transition: all 0.25s ease-in-out;
        }
        @media (max-width: 900px) {
            .page-header h1 { font-size: 2rem; }
            .metric-card { min-height: 100px; }
            .main .block-container {
                padding-left: 0.9rem;
                padding-right: 0.9rem;
            }
            .page-header {
                padding: 16px 18px;
            }
            .section-card {
                padding: 16px;
            }
            .sidebar-card {
                padding: 14px;
            }
            .card-grid {
                gap: 10px;
            }
            .empty-state {
                padding: 16px;
            }
            .metric-card {
                min-height: 100px;
            }
            .sidebar-link {
                font-size: 0.95rem;
                padding: 10px 12px;
            }
        }
        @media (max-width: 650px) {
            .page-header h1 { font-size: 1.7rem; }
            .page-header p { font-size: 0.95rem; }
            .metric-card {
                padding: 14px;
            }
        }
        </style>""",
        unsafe_allow_html=True,
    )


def render_page_header(icon, title, subtitle=None):
    header_html = f"""
        <div class='page-header'>
            <div style='display:flex;flex-wrap:wrap;align-items:flex-start;gap:16px;'>
                <div>
                    <h1>{icon} {title}</h1>
                    {f'<p>{subtitle}</p>' if subtitle else ''}
                </div>
            </div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)


def render_metric_cards(metrics):
    if not metrics:
        return
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        icon = metric.get('icon', '')
        title = metric.get('label', '')
        value = metric.get('value', '')
        detail = metric.get('detail', '')
        with col:
            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-icon'>{icon}</div>
                    <div class='metric-value'>{value}</div>
                    <div class='metric-label'>{title}</div>
                    {f'<div style="font-size:0.9rem; color: #475569; margin-top: 0.8rem;">{detail}</div>' if detail else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_empty_state(title, message):
    st.markdown(
        f"""
        <div class='empty-state'>
            <h3>✨ {title}</h3>
            <p>{message}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_navigation(role, current_page):
    with st.sidebar:
        st.markdown("<div class='sidebar-card'><h3>Smart Clinic Navigation</h3></div>", unsafe_allow_html=True)
        items = []
        if role == 'patient':
            items = [
                ('patient_dashboard', 'Dashboard', '🏠'),
                ('patient_health_trends', 'Health Trends', '📈'),
                ('patient_sos', 'Emergency SOS', '🚨'),
                ('patient_profile', 'Profile', '🧾'),
                ('family_dashboard', 'Family Health', '👨‍👩‍👧'),
            ]
        elif role == 'doctor':
            items = [
                ('doctor_dashboard', 'Doctor Dashboard', '🏥'),
            ]
        for page, label, icon in items:
            if st.button(f"{icon} {label}", key=f"nav_{page}"):
                st.session_state.page = page
                st.rerun()
        if role:
            if st.button('🔓 Logout', key='sidebar_logout'):
                if role == 'patient' and 'patient' in st.session_state:
                    del st.session_state['patient']
                if role == 'doctor' and 'doctor' in st.session_state:
                    del st.session_state['doctor']
                st.session_state.page = 'home'
                st.rerun()


load_app_style()

def parse_schedule_slots(schedule_slots):
    if not schedule_slots:
        return []
    if isinstance(schedule_slots, str):
        try:
            slots = json.loads(schedule_slots)
            if isinstance(slots, list):
                return [str(s) for s in slots if s]
        except Exception:
            return [s.strip() for s in schedule_slots.split(',') if s.strip()]
    if isinstance(schedule_slots, (list, tuple)):
        return [str(s) for s in schedule_slots if s]
    return [str(schedule_slots)]


def _parse_date(date_str):
    if not date_str:
        return None
    if isinstance(date_str, datetime.date):
        return date_str
    try:
        return datetime.date.fromisoformat(date_str)
    except Exception:
        return None


def _date_range(start_date, end_date):
    days = []
    try:
        current = start_date
        while current <= end_date:
            days.append(current)
            current += datetime.timedelta(days=1)
    except Exception:
        pass
    return days


def build_expected_doses(medicine, from_date, to_date):
    slots = parse_schedule_slots(medicine[6])
    if not slots:
        return []
    start_date = _parse_date(medicine[8]) or from_date
    end_date = _parse_date(medicine[9]) or to_date
    if end_date < from_date or start_date > to_date:
        return []
    range_start = max(start_date, from_date)
    range_end = min(end_date, to_date)
    expected = []
    for day in _date_range(range_start, range_end):
        for slot in slots:
            expected.append({
                'medicine_id': medicine[0],
                'medicine_name': medicine[3],
                'dosage': medicine[4],
                'frequency': medicine[5],
                'scheduled_time': slot,
                'date': day.isoformat(),
                'food_instruction': medicine[7] or 'No preference',
                'notes': medicine[10] or '',
                'active': bool(medicine[11])
            })
    return expected


def summarize_medication_adherence(patient_id, lookback_days=30):
    today = datetime.date.today()
    medicines = get_medicines_by_patient(patient_id, active_only=False)
    trust_start = today - datetime.timedelta(days=lookback_days)
    adherence_rows = get_adherence_history(patient_id=patient_id, since_date=trust_start.isoformat())
    records = {(r[3], r[4], r[1]): r for r in adherence_rows}

    expected_30 = []
    expected_7 = []
    expected_today = []
    upcoming = []
    missed = []
    completed_today = []

    for med in medicines:
        expected = build_expected_doses(med, trust_start, today + datetime.timedelta(days=7))
        for dose in expected:
            dose_date = _parse_date(dose['date'])
            key = (dose['date'], dose['scheduled_time'], dose['medicine_id'])
            record = records.get(key)
            if dose_date is None:
                continue
            if dose_date <= today:
                expected_30.append((dose, record))
            if dose_date == today:
                expected_today.append((dose, record))
            if today < dose_date <= today + datetime.timedelta(days=7):
                upcoming.append((dose, record))
            if dose_date < today:
                if record is None or record[5] not in ('Taken',):
                    missed.append((dose, record))
            if dose_date == today and record is not None and record[5] == 'Taken':
                completed_today.append((dose, record))

    taken = sum(1 for _, r in expected_30 if r is not None and r[5] == 'Taken')
    expected_total = len(expected_30)
    missed_count = sum(1 for _, r in expected_30 if r is None or r[5] != 'Taken')
    adherence_pct = int((taken / expected_total) * 100) if expected_total else 100

    weekly_dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    weekly_data = {day: {'expected': 0, 'taken': 0} for day in weekly_dates}
    monthly_dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(29, -1, -1)]
    monthly_data = {day: {'expected': 0, 'taken': 0} for day in monthly_dates}

    for dose, record in expected_30:
        if dose['date'] in weekly_data:
            weekly_data[dose['date']]['expected'] += 1
            if record is not None and record[5] == 'Taken':
                weekly_data[dose['date']]['taken'] += 1
        if dose['date'] in monthly_data:
            monthly_data[dose['date']]['expected'] += 1
            if record is not None and record[5] == 'Taken':
                monthly_data[dose['date']]['taken'] += 1

    weekly_chart = [int((weekly_data[d]['taken'] / weekly_data[d]['expected']) * 100) if weekly_data[d]['expected'] else 0 for d in weekly_dates]
    monthly_chart = [int((monthly_data[d]['taken'] / monthly_data[d]['expected']) * 100) if monthly_data[d]['expected'] else 0 for d in monthly_dates]

    return {
        'active_medicines': len([m for m in medicines if m[11]]),
        'overall_adherence': adherence_pct,
        'missed_doses': missed_count,
        'taken_doses': taken,
        'expected_doses': expected_total,
        'today_medicines': expected_today,
        'upcoming_medicines': upcoming,
        'missed_medicines': missed,
        'completed_today': completed_today,
        'weekly_chart_days': weekly_dates,
        'weekly_chart_values': weekly_chart,
        'monthly_chart_days': monthly_dates,
        'monthly_chart_values': monthly_chart,
        'active_medications': [m for m in medicines if m[11]],
        'all_medicines': medicines,
    }


def get_patient_adherence_detail(patient_id):
    summary = summarize_medication_adherence(patient_id)
    return summary


def _week_bucket(date_str):
    date = _parse_date(date_str)
    if not date:
        return None
    start = date - datetime.timedelta(days=date.weekday())
    return start.isoformat()


def _month_bucket(date_str):
    date = _parse_date(date_str)
    if not date:
        return None
    return date.strftime('%Y-%m')


def _parse_datetime(date_str, time_str=None):
    try:
        if time_str:
            return datetime.datetime.fromisoformat(f"{date_str}T{time_str}")
        return datetime.datetime.fromisoformat(date_str)
    except Exception:
        try:
            return datetime.datetime.fromisoformat(date_str)
        except Exception:
            return None


def collect_timeline_events(patient_id, patient_name):
    """Collect appointments, reports, prescriptions, symptom analyses and assessments into events."""
    events = []

    # Appointments
    try:
        appts = get_appointments_by_patient(patient_name) or []
        for a in appts:
            # a: id, patient_name, doctor_name, appointment_date, appointment_time, queue_number, status, clinic_id?
            appt_id = a[0]
            doc = a[2]
            appt_date = a[3]
            appt_time = a[4] if len(a) > 4 else None
            status = a[6] if len(a) > 6 else 'Pending'
            dt = _parse_datetime(appt_date, appt_time)
            events.append({
                'id': f"appt_{appt_id}",
                'dt': dt or datetime.datetime.now(),
                'type': 'Appointment',
                'icon': '🗓️',
                'title': f'Appointment with {doc}',
                'description': f'{appt_date} {appt_time or ""} — {status}',
                'status': status,
                'data': a,
            })
    except Exception:
        pass

    # Reports
    try:
        reps = get_reports_by_patient(patient_id) or []
        for r in reps:
            # r: id, patient_id, report_name, report_type, file_path, upload_date, notes
            rid = r[0]
            rname = r[2] if len(r) > 2 else 'Report'
            rtype = r[3] if len(r) > 3 else 'Report'
            rdate = r[5] if len(r) > 5 else None
            dt = None
            try:
                dt = datetime.datetime.fromisoformat(rdate) if rdate else None
            except Exception:
                dt = None
            events.append({
                'id': f'report_{rid}',
                'dt': dt or datetime.datetime.now(),
                'type': 'Report',
                'icon': '📄',
                'title': f'{rname}',
                'description': f'{rtype} — Uploaded {rdate or ""}',
                'status': 'Uploaded',
                'data': r,
            })
    except Exception:
        pass

    # Prescriptions
    try:
        pres = get_prescriptions_by_patient(patient_id) or []
        for p in pres:
            # p fields: id, patient_id, doctor_id, date, medicines, dosage, duration, notes, created_at, doctor_name
            pid = p[0]
            date = p[3] if len(p) > 3 else None
            created = p[8] if len(p) > 8 else None
            dt = None
            try:
                dt = datetime.datetime.fromisoformat(created) if created else None
            except Exception:
                try:
                    dt = datetime.datetime.fromisoformat(date) if date else None
                except Exception:
                    dt = None
            title = f'Prescription by {p[9] if len(p) > 9 else "Doctor"}'
            desc = f"{p[4] if len(p) > 4 else ''}"
            events.append({
                'id': f'pres_{pid}',
                'dt': dt or datetime.datetime.now(),
                'type': 'Prescription',
                'icon': '💊',
                'title': title,
                'description': desc,
                'status': 'Issued',
                'data': p,
            })
    except Exception:
        pass

    # Symptom analyses (session only)
    try:
        ss = st.session_state.get('last_symptom_report')
        if ss:
            rep = ss.get('report')
            ts = ss.get('timestamp')
            dt = None
            try:
                dt = datetime.datetime.fromisoformat(ts)
            except Exception:
                dt = datetime.datetime.now()
            events.append({
                'id': f'sym_{ts}',
                'dt': dt,
                'type': 'Symptom Analysis',
                'icon': '🩺',
                'title': 'AI Symptom Analysis',
                'description': f"Urgency: {rep.get('urgency')}",
                'status': rep.get('urgency'),
                'data': rep,
            })
    except Exception:
        pass

    # Report analyses (session only)
    try:
        ra = st.session_state.get('last_report_analysis')
        if ra:
            ar = ra.get('analysis')
            ts = ra.get('timestamp')
            rid = ra.get('report_id')
            rname = ra.get('report_name')
            dt = None
            try:
                dt = datetime.datetime.fromisoformat(ts)
            except Exception:
                dt = datetime.datetime.now()
            events.append({
                'id': f'repan_{ts}',
                'dt': dt,
                'type': 'Report Analysis',
                'icon': '🧾',
                'title': f'AI Report Analysis — {rname}',
                'description': ar.get('summary') if ar else 'Report analysis completed',
                'status': 'Analysed',
                'data': ra,
            })
    except Exception:
        pass

    # Medicines and adherence records
    try:
        meds = get_medicines_by_patient(patient_id, active_only=False) or []
        adherence_rows = get_adherence_history(patient_id=patient_id, limit=100) or []
        for m in meds:
            start_date = m[8] if len(m) > 8 else None
            end_date = m[9] if len(m) > 9 else None
            if start_date:
                dt = _parse_datetime(start_date)
                events.append({
                    'id': f'med_start_{m[0]}',
                    'dt': dt or datetime.datetime.now(),
                    'type': 'Medicine',
                    'icon': '💊',
                    'title': f'Medicine Started — {m[3]}',
                    'description': f'Started on {start_date}',
                    'status': 'Started',
                    'data': m,
                })
            if end_date:
                dt = _parse_datetime(end_date)
                events.append({
                    'id': f'med_end_{m[0]}',
                    'dt': dt or datetime.datetime.now(),
                    'type': 'Medicine',
                    'icon': '💊',
                    'title': f'Medicine Completed — {m[3]}',
                    'description': f'Ended on {end_date}',
                    'status': 'Completed',
                    'data': m,
                })
        for r in adherence_rows:
            dt = None
            try:
                dt = datetime.datetime.fromisoformat(f"{r[3]}T00:00:00")
            except Exception:
                dt = datetime.datetime.now()
            med = get_medicine_by_id(r[1])
            med_name = med[3] if med else 'Medicine'
            events.append({
                'id': f'med_record_{r[0]}',
                'dt': dt,
                'type': 'Medicine',
                'icon': '🩹',
                'title': f'{r[5]} — {med_name}',
                'description': f"{r[4]} on {r[3]}",
                'status': r[5],
                'data': r,
            })
    except Exception:
        pass

    # SOS events
    try:
        sos_events = get_sos_events(patient_id=patient_id, limit=20) or []
        for sos in sos_events:
            dt = None
            try:
                dt = datetime.datetime.fromisoformat(sos[4])
            except Exception:
                dt = datetime.datetime.now()
            events.append({
                'id': f'sos_{sos[0]}',
                'dt': dt,
                'type': 'Emergency',
                'icon': '🚨',
                'title': f'SOS Alert — {format_sos_status(sos[5])}',
                'description': sos[3] or 'Emergency assistance requested.',
                'status': format_sos_status(sos[5]),
                'data': sos,
            })
    except Exception:
        pass

    # Preventive assessments (session only)
    try:
        pa = st.session_state.get('last_preventive_assessment')
        if pa:
            # no timestamp saved, use now
            dt = datetime.datetime.now()
            events.append({
                'id': f'assess_{dt.isoformat()}',
                'dt': dt,
                'type': 'Risk Assessment',
                'icon': '📊',
                'title': 'Preventive Health Assessment',
                'description': f"Score: {pa.get('score')}/100 — Level: {pa.get('level')}",
                'status': pa.get('level'),
                'data': pa,
            })
    except Exception:
        pass

    # Sort events chronologically descending
    try:
        events_sorted = sorted(events, key=lambda e: e.get('dt') or datetime.datetime.now(), reverse=True)
    except Exception:
        events_sorted = events

    return events_sorted


def collect_health_trend_data(patient_id, patient_name, weeks=8):
    today = datetime.date.today()
    week_starts = []
    week_keys = []
    for offset in range(weeks - 1, -1, -1):
        start = today - datetime.timedelta(days=today.weekday()) - datetime.timedelta(weeks=offset)
        week_starts.append(start)
        week_keys.append(start.isoformat())

    appointments = get_appointments_by_patient(patient_name) or []
    appointment_counts = {key: {'Completed': 0, 'Pending': 0, 'Cancelled': 0} for key in week_keys}
    for a in appointments:
        week_key = _week_bucket(a[3])
        if week_key in appointment_counts:
            status = (a[6] if len(a) > 6 else 'Pending') or 'Pending'
            if status not in appointment_counts[week_key]:
                status = 'Pending'
            appointment_counts[week_key][status] += 1

    reports = get_reports_by_patient(patient_id) or []
    report_months = {}
    for r in reports:
        month_key = _month_bucket(r[5])
        if month_key:
            report_months[month_key] = report_months.get(month_key, 0) + 1

    start_window = (today - datetime.timedelta(weeks=weeks)).isoformat()
    adherence_rows = get_adherence_history(patient_id=patient_id, since_date=start_window) or []
    adherence_by_week = {key: {'Taken': 0, 'Missed': 0, 'Skipped': 0, 'Total': 0} for key in week_keys}
    for r in adherence_rows:
        week_key = _week_bucket(r[3])
        if week_key in adherence_by_week:
            status = (r[5] or '').strip().capitalize()
            if status not in ['Taken', 'Missed', 'Skipped']:
                status = 'Missed'
            adherence_by_week[week_key]['Total'] += 1
            adherence_by_week[week_key][status] = adherence_by_week[week_key].get(status, 0) + 1

    timeline_events = collect_timeline_events(patient_id, patient_name)
    risk_events = [e for e in timeline_events if e['type'] in ('Symptom Analysis', 'Risk Assessment')]
    risk_by_week = {key: {'Low': 0, 'Medium': 0, 'High': 0} for key in week_keys}
    for e in risk_events:
        dt = e.get('dt')
        if isinstance(dt, datetime.datetime):
            week_key = (dt.date() - datetime.timedelta(days=dt.date().weekday())).isoformat()
        elif isinstance(dt, datetime.date):
            week_key = (dt - datetime.timedelta(days=dt.weekday())).isoformat()
        else:
            week_key = _week_bucket(str(dt))
        if week_key in risk_by_week:
            level = str(e.get('status') or 'Low').capitalize()
            if level not in risk_by_week[week_key]:
                level = 'Low'
            risk_by_week[week_key][level] += 1

    health_scores = []
    for key in week_keys:
        week_report_count = sum(1 for r in reports if _week_bucket(r[5]) == key)
        week_adherence = adherence_by_week[key]
        total = week_adherence['Total']
        taken = week_adherence['Taken']
        adherence_pct = int((taken / total * 100)) if total else 80
        week_risk = risk_by_week[key]
        risk_penalty = 20 if week_risk['High'] > 0 else 10 if week_risk['Medium'] > 0 else 0
        completed = appointment_counts[key]['Completed']
        pending = appointment_counts[key]['Pending']
        cancelled = appointment_counts[key]['Cancelled']
        score = 70 + min(10, completed * 2) - min(20, pending * 2 + cancelled * 3) + min(8, week_report_count * 2) + min(10, adherence_pct // 10) - risk_penalty
        score = max(0, min(100, score))
        health_scores.append(score)

    total_appointments = len(appointments)
    completed_appointments = sum(1 for a in appointments if (a[6] if len(a) > 6 else 'Pending') == 'Completed')
    appointment_completion_rate = int((completed_appointments / total_appointments * 100)) if total_appointments else 0
    total_ai_assessments = len(risk_events)
    current_adherence_summary = summarize_medication_adherence(patient_id)
    current_adherence_pct = int(current_adherence_summary.get('overall_adherence', 0) or 0)
    current_health_score = health_scores[-1] if health_scores else int(75 if total_appointments or reports or adherence_rows or risk_events else 65)

    return {
        'week_labels': [start.strftime('%b %d') for start in week_starts],
        'week_keys': week_keys,
        'appointment_counts': appointment_counts,
        'report_months': report_months,
        'risk_by_week': risk_by_week,
        'adherence_by_week': adherence_by_week,
        'health_scores': health_scores,
        'appointments': appointments,
        'reports': reports,
        'adherence_rows': adherence_rows,
        'risk_events': risk_events,
        'current_health_score': current_health_score,
        'total_reports': len(reports),
        'total_ai_assessments': total_ai_assessments,
        'appointment_completion_rate': appointment_completion_rate,
        'current_adherence_pct': current_adherence_pct,
    }


def is_poor_adherence_summary(summary, threshold=80):
    return summary.get('overall_adherence', 100) < threshold


def format_slot_list(slots):
    return ', '.join(slots) if slots else 'None'


def record_adherence_action(medicine_id, patient_id, date, scheduled_time, action, note=None):
    try:
        record_medicine_adherence(medicine_id, patient_id, date, scheduled_time, action, note)
        return True
    except Exception:
        return False


def format_profile_field(value, default='Not Provided'):
    if value is None:
        return default
    if isinstance(value, str) and not value.strip():
        return default
    return value


def render_emergency_card_pdf(patient, contacts, medicines):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Emergency Medical Card', ln=True, align='C')
    pdf.ln(4)
    pdf.set_font('Arial', '', 12)

    name = format_profile_field(patient[1])
    age = format_profile_field(patient[4])
    blood_group = format_profile_field(patient[5])
    allergies = format_profile_field(patient[10]) if len(patient) > 10 else 'None'
    history = format_profile_field(patient[9]) if len(patient) > 9 else 'None'
    default_contact = format_profile_field(patient[7]) if len(patient) > 7 else 'None'

    pdf.cell(0, 8, f'Name: {name}', ln=True)
    pdf.cell(0, 8, f'Age: {age}', ln=True)
    pdf.cell(0, 8, f'Blood Group: {blood_group}', ln=True)
    pdf.cell(0, 8, f'Allergies: {allergies}', ln=True)
    pdf.multi_cell(0, 8, f'Existing Conditions: {history}')
    pdf.ln(2)
    pdf.cell(0, 8, 'Emergency Contacts:', ln=True)
    if contacts:
        for contact in contacts:
            pdf.cell(0, 7, f"- {contact[2]} ({contact[3]}) — {contact[4]}", ln=True)
    else:
        pdf.cell(0, 7, f'- {default_contact}', ln=True)

    pdf.ln(2)
    pdf.cell(0, 8, 'Current Medicines:', ln=True)
    if medicines:
        for medicine in medicines:
            pdf.multi_cell(0, 7, f"- {medicine[3]} {medicine[4]} | {medicine[5]} | {format_profile_field(medicine[8])} to {format_profile_field(medicine[9])}")
    else:
        pdf.cell(0, 7, '- None recorded', ln=True)

    pdf_data = pdf.output(dest='S')
    if isinstance(pdf_data, bytearray):
        pdf_data = bytes(pdf_data)
    elif isinstance(pdf_data, str):
        pdf_data = pdf_data.encode('latin-1', errors='replace')
    return pdf_data


def build_sos_timeline_event(sos_event):
    return {
        'id': f"sos_{sos_event[0]}",
        'dt': datetime.datetime.fromisoformat(sos_event[4]) if sos_event[4] else datetime.datetime.now(),
        'type': 'Emergency',
        'icon': '🚨',
        'title': f'SOS Alert — {sos_event[5]}',
        'description': sos_event[3] or 'Emergency assistance requested.',
        'status': sos_event[5],
        'data': sos_event,
    }


def format_phone(number):
    return number if number else 'Not Provided'


def format_sos_status(status):
    return status if status else 'Pending'


def build_medicine_event(med, action, date, scheduled_time):
    return {
        'id': f'med_{med[0]}_{action}_{date}_{scheduled_time}',
        'dt': datetime.datetime.fromisoformat(f"{date}T00:00:00"),
        'type': 'Medicine',
        'icon': '💊',
        'title': f"{action} — {med[3]}",
        'description': f"{scheduled_time} on {date}",
        'status': action,
        'data': {
            'medicine': med,
            'action': action,
            'date': date,
            'scheduled_time': scheduled_time,
        }
    }


def analyze_symptoms(symptoms_text: str):
    """Return detected conditions and recommended specialists for backward compatibility."""
    report = build_symptom_report(symptoms_text)
    return report['possible_conditions'], report['recommended_specialists']


def build_symptom_report(symptoms_text: str):
    """Analyze free-text symptoms and return a full clinical support report."""
    import re

    if not symptoms_text or not symptoms_text.strip():
        return {
            'symptoms_detected': [],
            'possible_conditions': [],
            'recommended_specialists': ['General Physician'],
            'urgency': 'Low',
            'home_care_advice': ['Provide rest, hydration and monitor symptoms.'],
            'red_flag_symptoms': [],
            'when_to_visit_doctor': ['If symptoms persist or worsen, consult a healthcare professional.'],
            'explanation': 'No symptoms were provided for analysis.',
            'emergency_warning': False,
        }

    normalized_text = re.sub(r"[^a-z0-9\s]", " ", symptoms_text.lower())

    def has_phrase(phrase):
        return re.search(r"\b" + re.escape(phrase) + r"\b", normalized_text) is not None

    def has_any(phrases):
        return any(has_phrase(p) for p in phrases)

    symptom_keywords = {
        'fever': ['fever', 'temperature', 'hot', 'chills', 'night sweat', 'sweating'],
        'cough': ['cough', 'coughing', 'hack', 'phlegm', 'sputum'],
        'sore throat': ['sore throat', 'throat pain', 'throat hurts', 'scratchy throat'],
        'body pain': ['body pain', 'body ache', 'aches', 'muscle pain', 'joint pain', 'myalgia'],
        'headache': ['headache', 'migraine', 'head pain', 'pressure in head'],
        'cold': ['cold', 'runny nose', 'stuffy nose', 'nasal congestion', 'sneezing'],
        'chest pain': ['chest pain', 'pain in chest', 'tightness in chest', 'pressure in chest'],
        'difficulty breathing': ['difficulty breathing', 'shortness of breath', 'breathlessness', 'cant breathe', 'dyspnea', 'wheezing'],
        'unconsciousness': ['unconscious', 'passed out', 'fainted', 'blackout', 'unresponsive'],
        'severe bleeding': ['severe bleeding', 'heavy bleeding', 'profuse bleeding', 'bleeding heavily'],
        'stroke-like symptoms': ['stroke', 'facial droop', 'slurred speech', 'weakness on one side', 'arm weakness', 'leg weakness', 'sudden confusion', 'vision changes'],
        'nausea': ['nausea', 'nauseous', 'queasy'],
        'vomiting': ['vomit', 'vomiting', 'throwing up'],
        'diarrhea': ['diarrhea', 'loose stool', 'watery stool', 'runny stool'],
        'fatigue': ['fatigue', 'tired', 'exhausted', 'weak', 'weakness'],
        'dizziness': ['dizzy', 'lightheaded', 'vertigo', 'giddy'],
        'rash': ['rash', 'hives', 'red spots', 'skin rash'],
        'abdominal pain': ['abdominal pain', 'stomach pain', 'belly pain', 'tummy ache', 'stomachache'],
        'back pain': ['back pain', 'lower back pain', 'upper back pain'],
        'ear pain': ['ear pain', 'earache'],
        'eye irritation': ['eye irritation', 'red eyes', 'watery eyes', 'itchy eyes'],
        'palpitations': ['palpitations', 'heart racing', 'racing heart', 'irregular heartbeat'],
        'numbness': ['numbness', 'tingling', 'pins and needles'],
    }

    detected_symptoms = []
    for symptom, phrases in symptom_keywords.items():
        if has_any(phrases):
            detected_symptoms.append(symptom)

    red_flag_symptoms = []
    if has_phrase('chest pain'):
        red_flag_symptoms.append('Chest pain')
    if has_any(['difficulty breathing', 'shortness of breath', 'breathlessness', 'dyspnea']):
        red_flag_symptoms.append('Difficulty breathing')
    if has_any(['unconscious', 'passed out', 'fainted', 'blackout', 'unresponsive']):
        red_flag_symptoms.append('Unconsciousness')
    if has_any(['severe bleeding', 'heavy bleeding', 'profuse bleeding']):
        red_flag_symptoms.append('Severe bleeding')
    if has_any(['stroke', 'facial droop', 'slurred speech', 'weakness on one side', 'sudden confusion', 'vision changes']):
        red_flag_symptoms.append('Stroke-like symptoms')

    possible_conditions = []
    if 'chest pain' in detected_symptoms or 'palpitations' in detected_symptoms:
        possible_conditions.append('Cardiac or chest-related concern')
    if 'difficulty breathing' in detected_symptoms:
        possible_conditions.append('Respiratory distress / pneumonia / asthma exacerbation')
    if 'stroke-like symptoms' in detected_symptoms:
        possible_conditions.append('Possible cerebrovascular event')
    if 'fever' in detected_symptoms and 'cough' in detected_symptoms:
        possible_conditions.append('Flu or viral respiratory infection')
    if 'fever' in detected_symptoms and 'sore throat' in detected_symptoms:
        possible_conditions.append('Pharyngitis or upper respiratory infection')
    if 'fever' in detected_symptoms and 'body pain' in detected_symptoms:
        possible_conditions.append('Influenza or systemic viral infection')
    if 'sore throat' in detected_symptoms and 'cold' in detected_symptoms:
        possible_conditions.append('Common cold or viral pharyngitis')
    if 'abdominal pain' in detected_symptoms and ('vomiting' in detected_symptoms or 'diarrhea' in detected_symptoms):
        possible_conditions.append('Gastroenteritis')
    if 'headache' in detected_symptoms and 'nausea' in detected_symptoms:
        possible_conditions.append('Migraine or tension headache')
    if 'rash' in detected_symptoms:
        possible_conditions.append('Dermatologic reaction or allergy')
    if 'ear pain' in detected_symptoms:
        possible_conditions.append('Ear infection or otitis')
    if 'back pain' in detected_symptoms:
        possible_conditions.append('Musculoskeletal strain or pain')
    if 'fatigue' in detected_symptoms and 'dizziness' in detected_symptoms:
        possible_conditions.append('Dehydration or systemic illness')

    if not possible_conditions and detected_symptoms:
        possible_conditions.append('Non-specific symptoms requiring clinical review')
    if not detected_symptoms:
        possible_conditions.append('No clear condition detected with provided symptoms')

    if 'chest pain' in detected_symptoms and 'difficulty breathing' in detected_symptoms:
        possible_conditions.insert(0, 'Potential acute cardiac or respiratory emergency')

    recommended_specialists = set()
    if red_flag_symptoms:
        recommended_specialists.add('Emergency Physician / ER')
    if 'stroke-like symptoms' in detected_symptoms:
        recommended_specialists.add('Neurologist')
    if 'chest pain' in detected_symptoms or 'palpitations' in detected_symptoms:
        recommended_specialists.add('Cardiologist')
    if 'difficulty breathing' in detected_symptoms or 'cough' in detected_symptoms:
        recommended_specialists.add('Pulmonologist')
    if 'sore throat' in detected_symptoms or 'ear pain' in detected_symptoms or 'cold' in detected_symptoms:
        recommended_specialists.add('ENT Specialist')
    if 'abdominal pain' in detected_symptoms or 'vomiting' in detected_symptoms or 'diarrhea' in detected_symptoms:
        recommended_specialists.add('Gastroenterologist')
    if 'rash' in detected_symptoms:
        recommended_specialists.add('Dermatologist')
    if 'headache' in detected_symptoms and 'stroke-like symptoms' not in detected_symptoms:
        recommended_specialists.add('Neurologist')
    if 'back pain' in detected_symptoms or 'body pain' in detected_symptoms:
        recommended_specialists.add('General Physician')
    if 'fever' in detected_symptoms and not recommended_specialists:
        recommended_specialists.add('General Physician')
    if not recommended_specialists:
        recommended_specialists.add('General Physician')

    if red_flag_symptoms:
        urgency = 'Emergency'
    elif 'chest pain' in detected_symptoms or 'difficulty breathing' in detected_symptoms or 'palpitations' in detected_symptoms:
        urgency = 'High'
    elif 'fever' in detected_symptoms and 'body pain' in detected_symptoms:
        urgency = 'Medium'
    elif 'fever' in detected_symptoms or 'cough' in detected_symptoms or 'sore throat' in detected_symptoms:
        urgency = 'Medium'
    else:
        urgency = 'Low'

    home_care_advice = []
    if 'fever' in detected_symptoms:
        home_care_advice.append('Rest, hydrate, and consider antipyretics like acetaminophen if appropriate.')
    if 'cough' in detected_symptoms or 'sore throat' in detected_symptoms:
        home_care_advice.append('Use warm fluids, throat lozenges, and a humidifier to soothe your airway.')
    if 'body pain' in detected_symptoms or 'headache' in detected_symptoms:
        home_care_advice.append('Rest, gentle stretching, and over-the-counter pain relief may help.')
    if 'difficulty breathing' in detected_symptoms:
        home_care_advice.append('Sit upright, avoid exertion, and seek urgent care if breathing worsens.')
    if 'nausea' in detected_symptoms or 'vomiting' in detected_symptoms or 'diarrhea' in detected_symptoms:
        home_care_advice.append('Drink clear fluids regularly and avoid heavy or spicy foods.')
    if 'rash' in detected_symptoms:
        home_care_advice.append('Keep the affected skin area clean, dry, and avoid irritants.')
    if not home_care_advice:
        home_care_advice.append('Monitor symptoms, stay hydrated, and rest as needed.')
    if urgency == 'Emergency':
        home_care_advice = ['Seek immediate emergency medical care. This tool is not a substitute for emergency evaluation.']

    when_to_visit_doctor = [
        'If symptoms worsen, persist beyond 24-48 hours, or new concerning features appear.',
        'If fever continues for more than 3 days or does not respond to home care.',
        'If you develop chest pain, difficulty breathing, confusion, unconsciousness, or severe bleeding.',
    ]
    if urgency == 'Low':
        when_to_visit_doctor.append('Visit a doctor if symptoms do not improve with rest and home care.')
    elif urgency == 'Medium':
        when_to_visit_doctor.append('Schedule a doctor visit soon for evaluation.')
    elif urgency == 'High':
        when_to_visit_doctor.append('Seek medical consultation promptly.')

    explanation_lines = []
    if detected_symptoms:
        explanation_lines.append(f"Detected symptoms: {', '.join(detected_symptoms)}.")
    if red_flag_symptoms:
        explanation_lines.append('Red-flag symptoms were identified, therefore emergency care is advised.')
    else:
        explanation_lines.append('Symptoms were mapped to likely clinical patterns to provide condition and specialist suggestions.')
    explanation_lines.append(f"Urgency is classified as {urgency} based on the severity and clustering of symptoms.")
    explanation_lines.append('This recommendation is clinical decision support, not a medical diagnosis.')

    return {
        'symptoms_detected': detected_symptoms,
        'possible_conditions': possible_conditions,
        'recommended_specialists': sorted(recommended_specialists),
        'urgency': urgency,
        'home_care_advice': home_care_advice,
        'red_flag_symptoms': red_flag_symptoms,
        'when_to_visit_doctor': when_to_visit_doctor,
        'explanation': ' '.join(explanation_lines),
        'emergency_warning': bool(red_flag_symptoms),
    }


UPLOAD_FOLDER = Path("uploads")
ALLOWED_REPORT_EXTENSIONS = {"pdf", "png", "jpg", "jpeg"}
MAX_REPORT_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def ensure_upload_folder():
    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    return UPLOAD_FOLDER


def get_file_extension(file_name: str):
    return Path(file_name).suffix.lower().lstrip('.')


def validate_report_file(uploaded_file):
    if uploaded_file is None:
        return False, "Please choose a file to upload."
    file_size = uploaded_file.size
    if file_size > MAX_REPORT_FILE_SIZE:
        return False, "File size must be 10 MB or less."
    extension = get_file_extension(uploaded_file.name)
    if extension not in ALLOWED_REPORT_EXTENSIONS:
        return False, "Only PDF, PNG, JPG and JPEG files are allowed."
    return True, None


def save_report_file(uploaded_file, patient_id):
    uploads_dir = ensure_upload_folder()
    extension = get_file_extension(uploaded_file.name)
    unique_name = f"report_{patient_id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}.{extension}"
    destination = uploads_dir / unique_name
    with open(destination, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(destination)


def extract_text_from_file(file_path: str) -> str:
    """Try to extract readable text from a PDF or image file.

    Uses PyPDF2 for PDFs and pytesseract for images when available. Raises Exception on failure.
    """
    import os
    import io

    if not os.path.exists(file_path):
        raise FileNotFoundError("Report file not found on server.")

    ext = get_file_extension(file_path)
    if ext == 'pdf':
        try:
            from PyPDF2 import PdfReader
        except Exception as e:
            raise RuntimeError(f"PDF extraction requires PyPDF2: {e}")
        try:
            reader = PdfReader(file_path)
            texts = []
            for p in reader.pages:
                try:
                    t = p.extract_text() or ''
                except Exception:
                    t = ''
                texts.append(t)
            full = "\n\n".join(texts).strip()
            if not full:
                raise RuntimeError("No selectable text found in PDF. It may be a scanned image PDF.")
            return full
        except Exception as e:
            raise RuntimeError(f"PDF parsing/extraction failed: {e}")
    elif ext in {'png', 'jpg', 'jpeg'}:
        try:
            from PIL import Image
        except Exception as e:
            raise RuntimeError(f"Image processing requires Pillow: {e}")
        try:
            try:
                import pytesseract
            except Exception:
                pytesseract = None
            img = Image.open(file_path)
            if pytesseract:
                text = pytesseract.image_to_string(img)
                if not text or not text.strip():
                    raise RuntimeError("OCR produced no readable text. Ensure Tesseract is installed and image quality is sufficient.")
                return text
            else:
                raise RuntimeError("OCR not available: install pytesseract and Tesseract executable to extract text from images.")
        except Exception as e:
            raise
    else:
        raise RuntimeError("Unsupported file type for text extraction.")


def analyze_report_text(report_text: str) -> dict:
    """Simple rule-based report analyzer returning structured findings and recommendations.

    This function is intentionally conservative and rule-based so it works without external AI.
    """
    import re

    if not report_text or not report_text.strip():
        return {
            'summary': 'No readable text extracted from the report.',
            'important_findings': [],
            'abnormal_values': [],
            'possible_concerns': [],
            'recommended_specialists': ['General Physician'],
            'suggested_tests': [],
            'lifestyle_recommendations': [],
            'patient_questions': [],
        }

    lines = [l.strip() for l in report_text.splitlines() if l.strip()]
    summary = ' '.join(lines[:3]) if lines else ''

    # Find lines with keywords indicating abnormality
    abnormal_keywords = re.compile(r"\b(high|low|elevated|reduced|abnormal|critical|increased|decreased)\b", re.I)
    important = [l for l in lines if abnormal_keywords.search(l)]

    # Find simple numeric lab patterns like 'Glucose: 180 mg/dL' or 'Hb: 9.2 g/dL'
    num_pattern = re.compile(r"([A-Za-z0-9 %+-]{2,40})[:\s\-]{0,2}\s*([0-9]+(?:\.[0-9]+)?)\s*(mg/dl|mmol/l|g/dl|%|mmol|mg|cells/ul|x10\^9/L|x10e9/L)?", re.I)
    abnormal_values = []
    for l in lines:
        m = num_pattern.search(l)
        if m:
            name = m.group(1).strip()
            val = float(m.group(2))
            unit = m.group(3) or ''
            severity = 'green'
            concern = None
            nlow = name.lower()
            # Heuristic thresholds for a few common tests
            try:
                if 'glucose' in nlow or 'sugar' in nlow:
                    # mg/dL thresholds (very generic)
                    if unit.lower() == 'mmol/l':
                        val_mg = val * 18.0182
                    else:
                        val_mg = val
                    if val_mg >= 200:
                        severity = 'red'
                        concern = 'Possible diabetic emergency or very high blood sugar'
                    elif val_mg >= 140:
                        severity = 'yellow'
                        concern = 'Elevated blood glucose — consider diabetes follow-up'
                if 'hba1c' in nlow or 'hb1ac' in nlow:
                    if val >= 9:
                        severity = 'red'
                    elif val >= 6.5:
                        severity = 'yellow'
                if 'hemoglobin' in nlow or '\bhb\b' in nlow:
                    if val < 8:
                        severity = 'red'
                    elif val < 11:
                        severity = 'yellow'
                if 'cholesterol' in nlow or 'ldl' in nlow or 'hdl' in nlow or 'triglyceride' in nlow:
                    if 'ldl' in nlow and val >= 160:
                        severity = 'red'
                    elif 'ldl' in nlow and val >= 130:
                        severity = 'yellow'
                    if 'hdl' in nlow and val < 40:
                        severity = 'yellow'
                if 'wbc' in nlow or 'white blood cell' in nlow:
                    if val < 3 or val > 20:
                        severity = 'red'
                    elif val < 4 or val > 11:
                        severity = 'yellow'
            except Exception:
                pass
            abnormal_values.append({'name': name, 'value': val, 'unit': unit, 'severity': severity, 'concern': concern, 'line': l})

    # Possible concerns based on keywords
    concerns = set()
    specialists = set()
    suggested_tests = set()
    lifestyle = set()
    questions = set()

    text_lower = report_text.lower()
    if any(k in text_lower for k in ['cardiac', 'ecg', 'arrhythmia', 'shortness of breath', 'chest pain']):
        specialists.add('Cardiologist')
        suggested_tests.update(['ECG', 'Echo'])
    if any(k in text_lower for k in ['glucose', 'hba1c', 'sugar']):
        specialists.add('Endocrinologist')
        suggested_tests.update(['Blood Sugar', 'HbA1c'])
    if any(k in text_lower for k in ['creatinine', 'bun', 'kidney']):
        specialists.add('Nephrologist')
        suggested_tests.update(['Kidney Function Test'])
    if any(k in text_lower for k in ['cholesterol', 'ldl', 'hdl', 'triglyceride']):
        specialists.add('Cardiologist')
        suggested_tests.add('Lipid Profile')
    if any(k in text_lower for k in ['infection', 'white blood cell', 'wbc', 'neutrophil']):
        specialists.add('Infectious Disease / General Physician')
        suggested_tests.add('CBC')

    # Build lifestyle recommendations and questions
    if abnormal_values:
        lifestyle.add('Follow-up with your healthcare provider to interpret abnormal lab results.')
        questions.add('Which of these findings are immediately concerning?')
        questions.add('Do I need changes to my medications?')

    # Map severity flags for important findings
    important_findings = []
    for l in important:
        sev = 'yellow'
        if re.search(r"\b(critical|emergency|immediate|urgent)\b", l, re.I):
            sev = 'red'
        important_findings.append({'line': l, 'severity': sev})

    # Combine small suggestions
    if not specialists:
        specialists.add('General Physician')
    if suggested_tests and 'CBC' in suggested_tests:
        lifestyle.add('Maintain hydration and a balanced diet prior to tests as advised')

    return {
        'summary': summary,
        'important_findings': important_findings,
        'abnormal_values': abnormal_values,
        'possible_concerns': sorted(list(concerns)) or [f["concern"] for f in abnormal_values if f.get('concern')] or [],
        'recommended_specialists': sorted(list(specialists)),
        'suggested_tests': sorted(list(suggested_tests)),
        'lifestyle_recommendations': sorted(list(lifestyle)),
        'patient_questions': sorted(list(questions)),
    }


def make_analysis_pdf(analysis: dict, patient_name: str, report_name: str) -> bytes:
    """Create a simple PDF from the analysis dict and return bytes.

    Uses `fpdf` if available.
    """
    try:
        from fpdf import FPDF
    except Exception:
        raise RuntimeError('PDF generation requires the `fpdf` package.')

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font('Arial', 'B', 14)

    def _safe_text(text):
        if text is None:
            return ''
        if isinstance(text, (bytes, bytearray)):
            text = text.decode('utf-8', errors='replace')
        elif not isinstance(text, str):
            text = str(text)
        return text.replace('—', '-').replace('–', '-').encode('latin-1', errors='replace').decode('latin-1')

    pdf.cell(0, 8, _safe_text(f'AI Report Analysis - {report_name}'), ln=True)
    pdf.set_font('Arial', size=10)
    pdf.cell(0, 6, _safe_text(f'Patient: {patient_name}'), ln=True)
    pdf.cell(0, 6, _safe_text(f'Date: {datetime.datetime.now().isoformat()}'), ln=True)
    pdf.ln(4)

    def _write_section(title, lines):
        import textwrap

        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 6, _safe_text(title), ln=True)
        pdf.set_font('Arial', size=10)
        max_width = int(pdf.epw)
        for ln in lines:
            wrapped = textwrap.wrap(_safe_text(f'- {ln}'), width=100, replace_whitespace=False, drop_whitespace=False)
            if not wrapped:
                wrapped = [_safe_text(f'- {ln}')]
            for chunk in wrapped:
                pdf.multi_cell(max_width, 6, chunk)
        pdf.ln(2)

    _write_section('Summary', [analysis.get('summary') or 'No summary available'])

    if analysis.get('important_findings'):
        _write_section('Important Findings', [f"[{f.get('severity').upper()}] {f.get('line')}" for f in analysis.get('important_findings')])

    if analysis.get('abnormal_values'):
        _write_section('Abnormal Values', [f"{v.get('name')}: {v.get('value')} {v.get('unit')} ({v.get('severity')})" for v in analysis.get('abnormal_values')])

    if analysis.get('possible_concerns'):
        _write_section('Possible Health Concerns', analysis.get('possible_concerns'))

    if analysis.get('recommended_specialists'):
        _write_section('Recommended Specialists', analysis.get('recommended_specialists'))

    if analysis.get('suggested_tests'):
        _write_section('Suggested Follow-up Tests', analysis.get('suggested_tests'))

    if analysis.get('lifestyle_recommendations'):
        _write_section('Lifestyle Recommendations', analysis.get('lifestyle_recommendations'))

    if analysis.get('patient_questions'):
        _write_section('Questions to Ask Your Doctor', analysis.get('patient_questions'))

    b = pdf.output(dest='S')
    if isinstance(b, str):
        b = b.encode('latin-1')
    elif isinstance(b, bytearray):
        b = bytes(b)
    return b


# Ensure database exists
create_database()


# -----------------
# Preventive Health Risk Assessment
# -----------------

def _normalize_text(s: str):
    """Lowercase and simplify text for keyword matching."""
    if not s:
        return ""
    import re
    return re.sub(r"[^a-z0-9\s]", " ", s.lower())


def collect_patient_data_for_assessment(patient_id: int, patient_name: str):
    """Gather available data sources for the risk assessment.

    Returns a dict containing profile, family_members, reports, appointments and optional recent_symptoms.
    """
    profile = None
    try:
        profile = get_patient_by_id(patient_id)
    except Exception:
        try:
            profile = get_patient_profile(patient_name)
        except Exception:
            profile = None

    family = []
    try:
        family = get_family_members_by_patient(patient_id) if 'get_family_members_by_patient' in globals() else []
    except Exception:
        family = []

    reports = []
    try:
        reports = get_reports_by_patient(patient_id)
    except Exception:
        reports = []

    appointments = []
    try:
        appointments = get_appointments_by_patient(patient_name)
    except Exception:
        appointments = []

    # Try to use any current symptom input in session (if present)
    recent_symptoms = None
    try:
        recent_symptoms = st.session_state.get('symptoms_input') if st.session_state.get('symptoms_input') else None
    except Exception:
        recent_symptoms = None

    return {
        'profile': profile,
        'family': family,
        'reports': reports,
        'appointments': appointments,
        'recent_symptoms': recent_symptoms,
    }


def assess_health_risk(patient_id: int, patient_name: str):
    """Rule-based health risk scoring engine.

    Returns a dict with `score` (0-100), `level`, `color`, `risk_factors`, `recommendations`,
    `suggested_tests`, `lifestyle_tips`, and `emergency` boolean.
    """
    data = collect_patient_data_for_assessment(patient_id, patient_name)
    profile = data['profile']
    family = data['family']
    reports = data['reports']
    appointments = data['appointments']
    recent_symptoms = data['recent_symptoms']

    # Start with full score
    score = 100
    risk_factors = []
    recommendations = set()
    suggested_tests = set()
    lifestyle_tips = set()
    emergency = False

    # Age-based adjustments
    age = None
    if profile and len(profile) > 4:
        try:
            age = int(profile[4]) if profile[4] is not None else None
        except Exception:
            age = None

    if age is not None:
        if age >= 75:
            score -= 30
            risk_factors.append('Advanced age (75+)')
            suggested_tests.update(['Blood Pressure', 'CBC', 'Kidney Function Test', 'ECG'])
        elif age >= 60:
            score -= 25
            risk_factors.append('Age 60+')
            suggested_tests.update(['Blood Pressure', 'CBC', 'Lipid Profile'])
        elif age >= 45:
            score -= 15
            risk_factors.append('Age 45-59')
            suggested_tests.update(['Blood Sugar', 'Lipid Profile'])
        elif age >= 30:
            score -= 5

    # Medical history keywords
    mh_text = _normalize_text(profile[9]) if profile and len(profile) > 9 and profile[9] else ""
    allergies_text = _normalize_text(profile[10]) if profile and len(profile) > 10 and profile[10] else ""
    med_keywords = {
        'diabetes': 20,
        'hypertension': 15,
        'high blood pressure': 15,
        'heart': 20,
        'cardiac': 20,
        'coronary': 20,
        'stroke': 25,
        'asthma': 10,
        'copd': 15,
        'cancer': 20,
        'kidney': 20,
        'chronic kidney': 20,
        'cholesterol': 10,
        'high cholesterol': 10,
        'anemia': 10,
        'thyroid': 10,
        'obesity': 10,
        'overweight': 10,
    }

    for kw, penalty in med_keywords.items():
        if kw in mh_text:
            score -= penalty
            risk_factors.append(f'History: {kw}')
            # map to tests and recommendations
            if 'diabetes' in kw or 'sugar' in kw:
                suggested_tests.update(['Blood Sugar', 'HbA1c'])
                recommendations.add('Monitor blood sugar regularly')
            if 'hypertension' in kw or 'high blood pressure' in kw:
                suggested_tests.add('Blood Pressure')
                recommendations.add('Monitor blood pressure regularly')
            if 'cholesterol' in kw:
                suggested_tests.add('Lipid Profile')
            if 'anemia' in kw:
                suggested_tests.add('CBC')

    # Allergies impact minor
    if allergies_text:
        if ',' in allergies_text or len(allergies_text) > 3:
            score -= 2
            risk_factors.append('Known allergies')

    # Family history
    for fm in family:
        # family member tuple: id, patient_id, member_name, relationship, age, blood_group, allergies, existing_conditions, emergency_contact
        existing = ''
        try:
            existing = _normalize_text(fm[7]) if len(fm) > 7 and fm[7] else ''
        except Exception:
            existing = ''
        for kw in ['diabetes', 'heart', 'cardiac', 'stroke', 'cancer', 'hypertension']:
            if kw in existing:
                score -= 10
                risk_factors.append(f'Family history: {kw}')

    # Analyze uploaded reports for keywords
    for rep in reports:
        # rep: id, patient_id, report_name, report_type, file_path, upload_date, notes
        name = _normalize_text(rep[2]) if rep and len(rep) > 2 and rep[2] else ''
        rtype = _normalize_text(rep[3]) if rep and len(rep) > 3 and rep[3] else ''
        notes = _normalize_text(rep[6]) if rep and len(rep) > 6 and rep[6] else ''
        combined = f"{name} {rtype} {notes}"
        if any(k in combined for k in ['low hb', 'low hemoglobin', 'anemia']):
            score -= 10
            risk_factors.append('Low haemoglobin / Anemia (from reports)')
            suggested_tests.add('CBC')
            recommendations.add('Eat iron-rich foods')
        if any(k in combined for k in ['high cholesterol', 'cholesterol']):
            score -= 10
            risk_factors.append('High cholesterol (from reports)')
            suggested_tests.add('Lipid Profile')
            recommendations.add('Reduce saturated fats and sugar')
        if any(k in combined for k in ['elevated blood sugar', 'high blood sugar', 'hba1c', 'hb1ac', 'glucose']):
            score -= 15
            risk_factors.append('Raised blood sugar (from reports)')
            suggested_tests.update(['Blood Sugar', 'HbA1c'])
            recommendations.add('Reduce sugar intake')
        if any(k in combined for k in ['abnormal ecg', 'ecg abnormal', 'cardiac']):
            score -= 20
            risk_factors.append('Cardiac abnormality (from reports)')
            suggested_tests.update(['ECG', 'Lipid Profile'])
            emergency = True

    # Appointment history (frequent visits may indicate higher risk)
    if appointments:
        try:
            recent_count = len([a for a in appointments if a and len(a) > 3])
            if recent_count > 8:
                score -= 10
                risk_factors.append('Frequent appointments / ongoing healthcare needs')
        except Exception:
            pass

    # Symptoms via AI checker if available
    if recent_symptoms:
        try:
            srep = build_symptom_report(recent_symptoms)
            if srep.get('emergency_warning'):
                emergency = True
                score -= 50
                risk_factors.append('Recent red-flag symptoms (current input)')
            else:
                urg = srep.get('urgency')
                if urg == 'High':
                    score -= 20
                    risk_factors.append('High urgency symptoms')
                elif urg == 'Medium':
                    score -= 10
                    risk_factors.append('Medium urgency symptoms')
                # Map some symptom-driven suggestions
                if any(x in srep.get('possible_conditions', []) for x in ['Influenza or systemic viral infection', 'Flu or viral respiratory infection']):
                    recommendations.add('Rest and hydration')
        except Exception:
            pass

    # Ensure score bounds
    if score < 0:
        score = 0
    if score > 100:
        score = 100

    # Determine level and color
    if score >= 80:
        level = 'Low'
        color = 'green'
    elif score >= 60:
        level = 'Moderate'
        color = 'yellow'
    elif score >= 40:
        level = 'High'
        color = 'orange'
    else:
        level = 'Critical'
        color = 'red'

    # Build friendly recommendations and lifestyle tips
    if not recommendations:
        recommendations.update([
            'Exercise 30 minutes daily',
            'Drink enough water',
            'Sleep 7-8 hours',
            'Maintain a balanced diet',
        ])

    # Default suggested tests for baseline screening based on age / risk
    if age and age >= 45:
        suggested_tests.update(['CBC', 'Blood Sugar', 'Lipid Profile', 'Thyroid Profile'])

    # Map some lifestyle tips
    lifestyle_tips.update([
        'Aim for regular moderate exercise',
        'Reduce processed and sugary foods',
        'Avoid smoking and limit alcohol',
    ])

    return {
        'score': int(score),
        'level': level,
        'color': color,
        'risk_factors': list(dict.fromkeys(risk_factors)),
        'recommendations': sorted(recommendations),
        'suggested_tests': sorted(suggested_tests),
        'lifestyle_tips': sorted(lifestyle_tips),
        'emergency': emergency,
    }


# Initialize navigation state
if "page" not in st.session_state:
    st.session_state.page = "home"

# -----------------
# Home page
# -----------------
if st.session_state.page == "home":
    render_page_header("🏥", "Smart Clinic Assistant", "A modern healthcare experience for patients and clinicians.")

    with st.container():
        st.markdown("<div class='card-grid'>", unsafe_allow_html=True)
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    """
                    <div class='section-card'>
                        <h2>👤 Patient Access</h2>
                        <p>Manage appointments, record medicine adherence, review reports, and get health insights.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Patient Login"):
                    st.session_state.page = "patient_login"
                    st.rerun()
                if st.button("Patient Register"):
                    st.session_state.page = "patient_register"
                    st.rerun()
            with col2:
                st.markdown(
                    """
                    <div class='section-card'>
                        <h2>👨‍⚕️ Doctor Access</h2>
                        <p>View clinic analytics, manage appointments, and track patient care from a professional dashboard.</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("Doctor Login"):
                    st.session_state.page = "doctor_login"
                    st.rerun()
                if st.button("Doctor Register"):
                    st.session_state.page = "doctor_register"
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# -----------------
# Patient Registration
# -----------------
if st.session_state.page == "patient_register":
    render_page_header("👤", "Patient Registration", "Create your patient account to access care tools and health insights.")

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
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
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------
# Doctor Registration
# -----------------
if st.session_state.page == "doctor_register":
    render_page_header("👨‍⚕️", "Doctor Registration", "Register as a clinician and connect to your clinic for patient care management.")
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
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
                selected_index = clinic_options.index(sel)
                selected_clinic_id = clinics[selected_index][0]
                clinic_name = clinics[selected_index][1]
                clinic_address = clinics[selected_index][2] if len(clinics[selected_index]) > 2 else None
            else:
                st.info("No existing clinics. Please create a new clinic.")
                clinic_name = st.text_input("Clinic Name", key="doc_clinic")
                clinic_address = st.text_area("Clinic Address", key="doc_clinic_addr")
                selected_clinic_id = None

        password = st.text_input("Password", type="password", key="doc_password")
        confirm = st.text_input("Confirm Password", type="password", key="doc_confirm")

    if st.button("Register Doctor"):
        # Validation
        if not all([name, email, phone, specialization, password, confirm]):
            st.error("Name, email, phone, specialization, password, and confirmation are required.")
        elif reg_mode == "Create New Clinic" and not all([clinic_name, clinic_address]):
            st.error("Clinic name and address are required when creating a new clinic.")
        elif reg_mode == "Join Existing Clinic" and selected_clinic_id is None:
            st.error("Please select an existing clinic to join.")
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
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------
# Doctor Login
# -----------------
if st.session_state.page == "doctor_login":
    render_page_header("🔐", "Doctor Login", "Sign in to access your clinic dashboard and patient queue.")
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)

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
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------
# Patient Login
# -----------------
if st.session_state.page == "patient_login":
    render_page_header("🔐", "Patient Login", "Access your health dashboard, appointments, and medicine management.")
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)

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
    st.markdown("</div>", unsafe_allow_html=True)


if st.session_state.page == "patient_dashboard":
    # Require logged-in patient
    if "patient" not in st.session_state:
        st.warning("Please login first.")
        st.session_state.page = "patient_login"
        st.rerun()

    patient = st.session_state.patient
    patient_name = patient[1] if len(patient) > 1 else "Patient"

    render_sidebar_navigation('patient', st.session_state.page)
    render_page_header("🏥", "Patient Dashboard", f"Welcome back, {patient_name}. Explore your care, appointments, and health insights.")
    st.success("Login Successful!")

    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.subheader("Quick Actions")
    qa1, qa2 = st.columns(2)
    with qa1:
        if st.button("🚨 Emergency SOS", key='qa_emergency_sos'):
            st.session_state.page = "patient_sos"
            st.rerun()
        if st.button("🧾 Health Profile", key='qa_health_profile'):
            st.session_state.page = "patient_profile"
            st.rerun()
    with qa2:
        if st.button("📈 Health Trends", key='qa_health_trends'):
            st.session_state.page = "patient_health_trends"
            st.rerun()
        if st.button("👨‍👩‍👧 Family Health", key='qa_family_dashboard'):
            st.session_state.page = "family_dashboard"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

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

    st.markdown("---")
    st.subheader("Medicine Reminder & Adherence Tracker")
    patient_id = patient[0]
    adherence_summary = get_patient_adherence_detail(patient_id)
    med_row1, med_row2, med_row3, med_row4 = st.columns(4)
    med_row1.metric('Active Medicines', adherence_summary['active_medicines'])
    med_row2.metric('Adherence', f"{adherence_summary['overall_adherence']}%")
    med_row3.metric('Missed Doses', adherence_summary['missed_doses'])
    med_row4.metric('Today Completed', len(adherence_summary['completed_today']))

    if not st.session_state.get('medicine_notifications_created'):
        if adherence_summary['upcoming_medicines']:
            create_notification('patient', patient_id, 'Upcoming Medicine Reminder', f"You have {len(adherence_summary['upcoming_medicines'])} upcoming medicine dose(s) in the next 7 days.")
        if adherence_summary['missed_medicines']:
            create_notification('patient', patient_id, 'Missed Medicine Alert', f"You have {len(adherence_summary['missed_medicines'])} missed medicine dose(s). Please update your adherence.")
        if adherence_summary['overall_adherence'] < 80 and adherence_summary['expected_doses']:
            create_notification('patient', patient_id, 'Low Adherence Warning', 'Your medicine adherence is below 80%. Please review your treatment plan.')
        st.session_state['medicine_notifications_created'] = True

    with st.expander('Today\'s Medicines', expanded=True):
        if adherence_summary['today_medicines']:
            for dose, record in adherence_summary['today_medicines']:
                cols = st.columns([2, 1, 1, 1, 1])
                with cols[0]:
                    st.write(f"**{dose['medicine_name']}** — {dose['dosage']} ({dose['scheduled_time']})")
                    st.write(f"Food: {dose['food_instruction']} | Notes: {dose['notes']}")
                with cols[1]:
                    st.write(record[5] if record else 'Pending')
                with cols[2]:
                    if st.button('Taken', key=f"taken_{dose['medicine_id']}_{dose['date']}_{dose['scheduled_time']}"):
                        if record_adherence_action(dose['medicine_id'], patient_id, dose['date'], dose['scheduled_time'], 'Taken'):
                            create_notification('patient', patient_id, 'Medicine Taken', f"Marked {dose['medicine_name']} as taken for {dose['scheduled_time']}.")
                            st.success('Marked as taken.')
                            st.rerun()
                with cols[3]:
                    if st.button('Skipped', key=f"skipped_{dose['medicine_id']}_{dose['date']}_{dose['scheduled_time']}"):
                        if record_adherence_action(dose['medicine_id'], patient_id, dose['date'], dose['scheduled_time'], 'Skipped'):
                            create_notification('patient', patient_id, 'Medicine Skipped', f"Marked {dose['medicine_name']} as skipped for {dose['scheduled_time']}.")
                            st.warning('Marked as skipped.')
                            st.rerun()
                with cols[4]:
                    if st.button('Missed', key=f"missed_{dose['medicine_id']}_{dose['date']}_{dose['scheduled_time']}"):
                        if record_adherence_action(dose['medicine_id'], patient_id, dose['date'], dose['scheduled_time'], 'Missed'):
                            create_notification('patient', patient_id, 'Medicine Missed', f"Marked {dose['medicine_name']} as missed for {dose['scheduled_time']}.")
                            st.error('Marked as missed.')
                            st.rerun()
        else:
            st.info('No medicines scheduled for today.')

    with st.expander('Upcoming Medicines', expanded=False):
        if adherence_summary['upcoming_medicines']:
            for dose, record in adherence_summary['upcoming_medicines']:
                st.write(f"{dose['date']} • {dose['medicine_name']} — {dose['dosage']} ({dose['scheduled_time']})")
        else:
            st.info('No upcoming medicines in the next 7 days.')

    with st.expander('Missed Medicines', expanded=False):
        if adherence_summary['missed_medicines']:
            for dose, record in adherence_summary['missed_medicines'][:10]:
                status = record[5] if record else 'Unrecorded'
                st.write(f"{dose['date']} • {dose['medicine_name']} — {dose['scheduled_time']} ({status})")
        else:
            st.info('No missed medicine doses.')

    with st.expander('Manage My Medicines', expanded=True):
        med_action = st.radio('Action', ['Add Medicine', 'Edit Existing'], key='medicine_action')
        if med_action == 'Edit Existing':
            medicine_options = [f"{m[3]} ({m[4]}) [{ 'Active' if m[11] else 'Inactive' }]" for m in adherence_summary['all_medicines']]
            selected_med = st.selectbox('Select Medicine', [''] + medicine_options, key='select_existing_med')
            edit_med = None
            if selected_med:
                index = medicine_options.index(selected_med)
                edit_med = adherence_summary['all_medicines'][index]
        else:
            edit_med = None

        med_name = st.text_input('Medicine Name', value=edit_med[3] if edit_med else '', key='med_name')
        dosage = st.text_input('Dosage', value=edit_med[4] if edit_med else '', key='med_dosage')
        frequency = st.selectbox('Frequency', ['Once', 'Twice', 'Thrice', 'Custom'], index=['Once','Twice','Thrice','Custom'].index(edit_med[5]) if edit_med else 0, key='med_frequency')
        schedule_slots = st.multiselect('Times of Day', ['Morning', 'Afternoon', 'Evening', 'Night'], default=parse_schedule_slots(edit_med[6]) if edit_med else [], key='med_schedule')
        food_instruction = st.selectbox('Food Instruction', ['Before Food', 'After Food', 'No Preference'], index=['Before Food','After Food','No Preference'].index(edit_med[7] if edit_med and edit_med[7] else 'No Preference'), key='med_food')
        start_date = st.date_input('Start Date', value=_parse_date(edit_med[8]) if edit_med and edit_med[8] else datetime.date.today(), key='med_start')
        end_date = st.date_input('End Date', value=_parse_date(edit_med[9]) if edit_med and edit_med[9] else (datetime.date.today() + datetime.timedelta(days=7)), key='med_end')
        notes = st.text_area('Notes', value=edit_med[10] if edit_med else '', key='med_notes')
        active_flag = st.checkbox('Active', value=bool(edit_med[11]) if edit_med else True, key='med_active')

        if st.button('Save Medicine', key='save_medicine'):
            if not med_name.strip():
                st.error('Medicine name is required.')
            elif start_date > end_date:
                st.error('Start date cannot be after end date.')
            else:
                final_slots = schedule_slots or (['Morning'] if frequency == 'Once' else ['Morning', 'Evening'] if frequency == 'Twice' else ['Morning', 'Afternoon', 'Evening'] if frequency == 'Thrice' else [])
                if edit_med:
                    update_medicine(edit_med[0], med_name.strip(), dosage.strip(), frequency, final_slots, food_instruction, start_date.isoformat(), end_date.isoformat(), notes.strip() if notes else None, 1 if active_flag else 0)
                    st.success('Medicine updated successfully.')
                else:
                    create_medicine(patient_id, None, med_name.strip(), dosage.strip(), frequency, final_slots, food_instruction, start_date.isoformat(), end_date.isoformat(), notes.strip() if notes else None, 1)
                    st.success('Medicine added successfully.')
                st.rerun()

        if edit_med and st.button('Delete Medicine', key='delete_medicine'):
            delete_medicine(edit_med[0])
            st.success('Medicine deleted successfully.')
            st.rerun()

    with st.expander('Adherence Analytics', expanded=False):
        st.write(f"Overall adherence: {adherence_summary['overall_adherence']}%")
        st.line_chart({'Weekly Adherence': adherence_summary['weekly_chart_values']}, use_container_width=True)
        st.line_chart({'Monthly Adherence': adherence_summary['monthly_chart_values']}, use_container_width=True)
        st.write(f"Scheduled doses in last 30 days: {adherence_summary['expected_doses']}")
        st.write(f"Taken doses in last 30 days: {adherence_summary['taken_doses']}")
        st.write(f"Missed doses in last 30 days: {adherence_summary['missed_doses']}")

    st.markdown('---')
    st.subheader('Medical Reports')
    report_type = st.selectbox("Report Type", ["PDF Report", "Blood Test Report", "X-ray Image", "Prescription", "Other Medical Document"], key="report_type")
    uploaded_file = st.file_uploader("Upload medical report", type=["pdf", "png", "jpg", "jpeg"], key="report_upload")
    report_name = st.text_input("Report Name", value=uploaded_file.name if uploaded_file else "", key="report_name")
    report_notes = st.text_area("Notes (optional)", key="report_notes")
    if st.button("Upload Report", key="upload_report"):
        is_valid, error_message = validate_report_file(uploaded_file)
        if not is_valid:
            st.error(error_message)
        else:
            try:
                if not report_name:
                    report_name = uploaded_file.name
                saved_path = save_report_file(uploaded_file, patient_id)
                insert_medical_report(patient_id, report_name.strip(), report_type, saved_path, report_notes.strip() if report_notes else None)
                st.success("Report uploaded successfully.")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to upload report: {e}")

    reports = get_reports_by_patient(patient_id)
    st.markdown("### Report History")
    if reports:
        for report_id, _, name, rtype, file_path, upload_date, notes in reports:
            with st.expander(f"{name} ({rtype}) — Uploaded {upload_date}"):
                st.write(f"**Type:** {rtype}")
                st.write(f"**Uploaded:** {upload_date}")
                if notes:
                    st.write(f"**Notes:** {notes}")
                if file_path and os.path.exists(file_path):
                    ext = get_file_extension(file_path)
                    mime_type = "application/pdf" if ext == "pdf" else "image/jpeg" if ext in {"jpg", "jpeg"} else "image/png"
                    with open(file_path, "rb") as file_data:
                        st.download_button(
                            label="Download Report",
                            data=file_data.read(),
                            file_name=os.path.basename(file_path),
                            mime=mime_type,
                            key=f"download_report_{report_id}"
                        )
                else:
                    st.error("Report file missing on server.")
                # Show previous AI analyses for this report
                try:
                    analyses = get_analyses_by_report(report_id)
                except Exception:
                    analyses = []

                if analyses:
                    st.markdown("#### Previous AI Analyses")
                    for a in analyses:
                        aid, pid, rid, a_date, summary, recs, details = a
                        cols = st.columns([6,2])
                        with cols[0]:
                            st.write(f"**{a_date}** — {summary}")
                        with cols[1]:
                            # View details toggle
                            if st.button("View", key=f"view_analysis_{aid}"):
                                try:
                                    payload = json.loads(details) if details else {}
                                except Exception:
                                    payload = {}
                                st.markdown("---")
                                st.write(f"**Analysis Date:** {a_date}")
                                st.write(f"**Summary:** {summary}")
                                if payload.get('important_findings'):
                                    st.write('**Important Findings:**')
                                    for f in payload.get('important_findings'):
                                        sev = f.get('severity','yellow')
                                        if sev == 'red':
                                            st.error(f.get('line'))
                                        elif sev == 'yellow':
                                            st.warning(f.get('line'))
                                        else:
                                            st.success(f.get('line'))
                                if payload.get('abnormal_values'):
                                    st.write('**Abnormal Values:**')
                                    for v in payload.get('abnormal_values'):
                                        sev = v.get('severity','yellow')
                                        text = f"{v.get('name')}: {v.get('value')} {v.get('unit')}"
                                        if sev == 'red':
                                            st.error(text)
                                        elif sev == 'yellow':
                                            st.warning(text)
                                        else:
                                            st.success(text)
                                if st.button('Download Analysis PDF', key=f'download_analysis_{aid}'):
                                    try:
                                        pdf_bytes = make_analysis_pdf(payload, patient[1], name)
                                        st.download_button(label='Download PDF', data=pdf_bytes, file_name=f"analysis_{aid}.pdf", mime='application/pdf')
                                    except Exception as e:
                                        st.error(f"Failed to generate PDF: {e}")

                if st.button("Delete Report", key=f"delete_report_{report_id}"):
                    try:
                        delete_medical_report(report_id)
                        st.success("Report deleted successfully.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete report: {e}")

                # AI analysis action
                if st.button("AI Report Analysis", key=f"analyze_report_{report_id}"):
                    # Extract text
                    try:
                        text = extract_text_from_file(file_path)
                    except Exception as e:
                        st.error(f"Failed to extract text from report: {e}")
                        text = None

                    if text:
                        try:
                            analysis = analyze_report_text(text)
                        except Exception as e:
                            st.error(f"Report analysis failed: {e}")
                            analysis = None

                        if analysis:
                            # Save analysis to DB
                            try:
                                aid = insert_report_analysis(patient_id, report_id, datetime.datetime.now().isoformat(), analysis.get('summary',''), json.dumps(analysis.get('recommended_specialists') or []), json.dumps(analysis))
                                st.success('Analysis saved.')
                            except Exception as e:
                                st.error(f'Failed to save analysis: {e}')
                                aid = None

                            # Add to session timeline for immediate visibility
                            try:
                                st.session_state['last_report_analysis'] = {
                                    'analysis': analysis,
                                    'timestamp': datetime.datetime.now().isoformat(),
                                    'report_id': report_id,
                                    'report_name': name,
                                    'patient_id': patient_id,
                                }
                            except Exception:
                                pass

                            # Display analysis results
                            st.markdown('### AI Analysis Summary')
                            st.write(analysis.get('summary') or 'No summary.')

                            if analysis.get('important_findings'):
                                st.markdown('### Important Findings')
                                for f in analysis.get('important_findings'):
                                    sev = f.get('severity','yellow')
                                    if sev == 'red':
                                        st.error(f.get('line'))
                                    elif sev == 'yellow':
                                        st.warning(f.get('line'))
                                    else:
                                        st.success(f.get('line'))

                            if analysis.get('abnormal_values'):
                                st.markdown('### Abnormal Values')
                                for v in analysis.get('abnormal_values'):
                                    sev = v.get('severity','yellow')
                                    textv = f"{v.get('name')}: {v.get('value')} {v.get('unit')}"
                                    if sev == 'red':
                                        st.error(textv)
                                    elif sev == 'yellow':
                                        st.warning(textv)
                                    else:
                                        st.success(textv)

                            if analysis.get('recommended_specialists'):
                                st.markdown('### Recommended Specialist(s)')
                                for s in analysis.get('recommended_specialists'):
                                    st.write(f"- {s}")

                            if analysis.get('suggested_tests'):
                                st.markdown('### Suggested Follow-up Tests')
                                for t in analysis.get('suggested_tests'):
                                    st.write(f"- {t}")

                            if analysis.get('lifestyle_recommendations'):
                                st.markdown('### Lifestyle Recommendations')
                                for l in analysis.get('lifestyle_recommendations'):
                                    st.write(f"- {l}")

                            if analysis.get('patient_questions'):
                                st.markdown('### Questions to Ask Your Doctor')
                                for q in analysis.get('patient_questions'):
                                    st.write(f"- {q}")

                            # PDF download
                            try:
                                pdf_bytes = make_analysis_pdf(analysis, patient[1], name)
                                st.download_button(label='Download Analysis as PDF', data=pdf_bytes, file_name=f"{os.path.basename(file_path)}_analysis.pdf", mime='application/pdf')
                            except Exception as e:
                                st.error(f"Failed to generate PDF: {e}")
    else:
        st.info("No medical reports uploaded yet.")

    # -----------------
    # Preventive Health Risk Assessment UI
    # -----------------
    st.markdown("---")
    st.subheader("🩺 Preventive Health Risk Assessment")
    st.write("This tool provides a simple, rule-based preventive risk score using available profile, family, reports and recent symptom input.")

    assess_btn = st.button("Run Preventive Health Risk Assessment", key="run_preventive_assessment")
    if assess_btn:
        try:
            result = assess_health_risk(patient_id, patient_name)
            st.session_state['last_preventive_assessment'] = result
        except Exception as e:
            st.error(f"Failed to run assessment: {e}")

    assessment = st.session_state.get('last_preventive_assessment')
    if assessment:
        score = assessment['score']
        level = assessment['level']
        color = assessment['color']
        emergency_flag = assessment['emergency']

        # Metric and progress
        col1, col2 = st.columns([2, 4])
        with col1:
            st.metric("Health Score", f"{score}/100", delta=None)
            st.progress(score)
        with col2:
            if emergency_flag:
                st.error("EMERGENCY: Immediate medical attention recommended based on available data.")
            else:
                if color == 'green':
                    st.success(f"Overall Risk Level: {level}")
                elif color == 'yellow':
                    st.info(f"Overall Risk Level: {level}")
                elif color == 'orange':
                    st.warning(f"Overall Risk Level: {level}")
                else:
                    st.error(f"Overall Risk Level: {level}")

        # Risk factors
        with st.expander("Possible Risk Factors", expanded=True):
            if assessment['risk_factors']:
                for rf in assessment['risk_factors']:
                    st.write(f"- {rf}")
            else:
                st.write("- No specific risk factors detected based on available data.")

        # Recommendations
        with st.expander("Preventive Recommendations", expanded=False):
            for rec in assessment['recommendations']:
                st.write(f"- {rec}")

        # Suggested health checkups
        with st.expander("Recommended Health Checkups", expanded=False):
            if assessment['suggested_tests']:
                for test in assessment['suggested_tests']:
                    st.write(f"- {test}")
            else:
                st.write("- Basic screening tests: CBC, Blood Sugar, Lipid Profile")

        # Lifestyle tips
        with st.expander("Lifestyle Tips", expanded=False):
            for tip in assessment['lifestyle_tips']:
                st.write(f"- {tip}")

        st.markdown("---")
        st.info("This is a clinical decision support aid only and not a medical diagnosis. Consult a qualified healthcare professional.")

    # -----------------
    # Health Timeline
    # -----------------
    def render_timeline(events):
        """Render events list with filters, search and expanders."""
        icon_map = {
            'Appointment': '🗓️',
            'Report': '📄',
            'Prescription': '💊',
            'Symptom Analysis': '🩺',
            'Risk Assessment': '📊',
            'Medicine': '💊',
            'Emergency': '🚨',
        }

        # Filters
        filter_opt = st.selectbox('Filter events', ['All', 'Appointments', 'Reports', 'Symptoms', 'Prescriptions', 'Risk Assessments', 'Medicines', 'Emergency'], key='timeline_filter')
        query = st.text_input('Search timeline', key='timeline_search')

        # Summary metrics
        total_appts = len([e for e in events if e['type'] == 'Appointment'])
        total_reports = len([e for e in events if e['type'] == 'Report'])
        total_sym = len([e for e in events if e['type'] == 'Symptom Analysis'])
        total_pres = len([e for e in events if e['type'] == 'Prescription'])
        last_visit = None
        try:
            appt_dates = [e['dt'] for e in events if e['type'] == 'Appointment' and e.get('dt')]
            last_visit = max(appt_dates).date().isoformat() if appt_dates else None
        except Exception:
            last_visit = None

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric('Total Appointments', total_appts)
        c2.metric('Reports', total_reports)
        c3.metric('AI Assessments', total_sym + (1 if st.session_state.get('last_preventive_assessment') else 0))
        c4.metric('Prescriptions', total_pres)
        c5.metric('Last Visit', last_visit or 'N/A')

        # Apply filter
        def _matches_filter(ev):
            if filter_opt == 'All':
                return True
            if filter_opt == 'Appointments' and ev['type'] == 'Appointment':
                return True
            if filter_opt == 'Reports' and ev['type'] == 'Report':
                return True
            if filter_opt == 'Symptoms' and ev['type'] == 'Symptom Analysis':
                return True
            if filter_opt == 'Prescriptions' and ev['type'] == 'Prescription':
                return True
            if filter_opt == 'Risk Assessments' and ev['type'] == 'Risk Assessment':
                return True
            if filter_opt == 'Medicines' and ev['type'] == 'Medicine':
                return True
            if filter_opt == 'Emergency' and ev['type'] == 'Emergency':
                return True
            return False

        displayed = [e for e in events if _matches_filter(e) and (not query or query.lower() in (e.get('title','')+e.get('description','') ).lower())]

        if not displayed:
            st.info('No timeline events found for the selected filters/search.')
            return

        for ev in displayed:
            dt = ev.get('dt')
            date_str = dt.date().isoformat() if dt else ''
            time_str = dt.time().strftime('%H:%M') if dt and hasattr(dt,'time') else ''
            icon = ev.get('icon') or icon_map.get(ev.get('type'), '')
            with st.expander(f"{icon} {ev.get('title')} — {date_str} {time_str} ({ev.get('status')})", expanded=False):
                st.write(f"**Type:** {ev.get('type')}")
                st.write(f"**When:** {date_str} {time_str}")
                st.write(f"**Short:** {ev.get('description')}")
                st.write('---')
                # Detailed payload
                try:
                    data = ev.get('data')
                    if ev['type'] == 'Appointment':
                        st.write(f"Patient: {data[1]}")
                        st.write(f"Doctor: {data[2]}")
                        st.write(f"Status: {data[6] if len(data)>6 else 'Pending'}")
                    elif ev['type'] == 'Report':
                        st.write(f"Report Name: {data[2]}")
                        st.write(f"Report Type: {data[3]}")
                        st.write(f"Uploaded: {data[5]}")
                        path = data[4] if len(data) > 4 else None
                        if path and os.path.exists(path):
                            with open(path,'rb') as f:
                                ext = get_file_extension(path)
                                mime = 'application/pdf' if ext=='pdf' else 'image/png' if ext=='png' else 'image/jpeg'
                                st.download_button('Download', f.read(), file_name=os.path.basename(path), mime=mime)
                    elif ev['type'] == 'Prescription':
                        st.write(f"Medicines: {data[4] if len(data)>4 else ''}")
                        st.write(f"Dosage: {data[5] if len(data)>5 else ''}")
                        st.write(f"Notes: {data[7] if len(data)>7 else ''}")
                    elif ev['type'] == 'Symptom Analysis':
                        rep = ev.get('data')
                        st.write(f"Urgency: {rep.get('urgency')}")
                        st.write(f"Possible Conditions: {', '.join(rep.get('possible_conditions') or [])}")
                    elif ev['type'] == 'Risk Assessment':
                        rep = ev.get('data')
                        st.write(f"Score: {rep.get('score')}/100")
                        st.write(f"Level: {rep.get('level')}")
                        st.write('Recommendations:')
                        for r in rep.get('recommendations', []):
                            st.write(f"- {r}")
                    elif ev['type'] == 'Medicine':
                        data = ev.get('data')
                        if isinstance(data, tuple):
                            st.write(f"Medicine: {data[3]}")
                            st.write(f"Dosage: {data[4]}")
                            st.write(f"Schedule: {format_slot_list(parse_schedule_slots(data[6]))}")
                            st.write(f"Food Instruction: {data[7]}")
                            st.write(f"Start Date: {data[8]}")
                            st.write(f"End Date: {data[9]}")
                        else:
                            st.write(f"Action: {data.get('action')}")
                            st.write(f"Medicine: {data.get('medicine')[3] if data.get('medicine') else ''}")
                            st.write(f"Scheduled Time: {data.get('scheduled_time')}")
                            st.write(f"Date: {data.get('date')}")
                    elif ev['type'] == 'Emergency':
                        data = ev.get('data')
                        st.write(f"Reason: {data[3] if len(data) > 3 else 'Emergency assistance requested.'}")
                        st.write(f"Status: {data[5] if len(data) > 5 else 'Sent'}")
                        patient_info = get_patient_by_id(data[1])
                        if patient_info:
                            st.write(f"Patient: {patient_info[1]}")
                except Exception as e:
                    st.write(f"Details unavailable: {e}")

    # Render the timeline UI
    try:
        events = collect_timeline_events(patient_id, patient_name)
        st.markdown('---')
        st.subheader('🕘 Health Timeline')
        render_timeline(events)
    except Exception:
        pass

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
    st.write("Enter your symptoms in natural language. Example: 'I have had fever for 3 days with sore throat and body pain.'")
    symptoms_input = st.text_area("Describe your symptoms", value="", height=140, key="symptoms_input")
    if st.button("Analyze Symptoms"):
        if not symptoms_input or not symptoms_input.strip():
            st.error("Please enter symptoms to analyze.")
        else:
            report = build_symptom_report(symptoms_input)
            # Save the last symptom analysis to session state for timeline/history
            try:
                st.session_state['last_symptom_report'] = {
                    'report': report,
                    'timestamp': datetime.datetime.now().isoformat()
                }
            except Exception:
                pass
            if report['emergency_warning']:
                st.error("EMERGENCY WARNING: Seek immediate emergency medical care if you have any of these symptoms:")
                for rf in report['red_flag_symptoms']:
                    st.write(f"- {rf}")

            st.markdown("### Symptoms Detected")
            if report['symptoms_detected']:
                for symptom in report['symptoms_detected']:
                    st.write(f"- {symptom.title()}")
            else:
                st.write("- No clear symptoms detected. Please describe your symptoms in more detail.")

            st.markdown("### Possible Conditions")
            for condition in report['possible_conditions']:
                st.write(f"- {condition}")

            st.markdown("### Recommended Specialist(s)")
            for specialist in report['recommended_specialists']:
                st.write(f"- {specialist}")

            st.markdown("### Urgency Level")
            if report['urgency'] == 'Emergency':
                st.error(report['urgency'])
            elif report['urgency'] == 'High':
                st.warning(report['urgency'])
            else:
                st.info(report['urgency'])

            st.markdown("### Home Care Advice")
            for advice in report['home_care_advice']:
                st.write(f"- {advice}")

            st.markdown("### When to Visit a Doctor")
            for advice in report['when_to_visit_doctor']:
                st.write(f"- {advice}")

            st.markdown("### Explanation")
            st.write(report['explanation'])

            st.markdown("---")
            st.warning("This is not a medical diagnosis. Please consult a qualified healthcare professional.")

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
# Health Trends Page
# -----------------
if st.session_state.page == "patient_health_trends":
    if "patient" not in st.session_state:
        st.warning("Please login first.")
        st.session_state.page = "patient_login"
        st.rerun()

    render_sidebar_navigation('patient', st.session_state.page)
    patient = st.session_state.patient
    patient_id = patient[0]
    patient_name = patient[1] if len(patient) > 1 else "Patient"

    render_page_header("📈", "Health Trends", "Track your health score, appointments, AI risk history, reports, and medicine adherence.")

    trend_data = collect_health_trend_data(patient_id, patient_name)
    has_trend_data = bool(trend_data['appointments'] or trend_data['reports'] or trend_data['adherence_rows'] or trend_data['risk_events'])

    render_metric_cards([
        {'icon': '💚', 'label': 'Current Health Score', 'value': f"{trend_data['current_health_score']}/100"},
        {'icon': '📄', 'label': 'Total Reports', 'value': trend_data['total_reports']},
        {'icon': '🤖', 'label': 'AI Assessments', 'value': trend_data['total_ai_assessments']},
        {'icon': '📊', 'label': 'Appointment Completion', 'value': f"{trend_data['appointment_completion_rate']}%"},
        {'icon': '💊', 'label': 'Medicine Adherence', 'value': f"{trend_data['current_adherence_pct']}%"},
    ])

    if not has_trend_data:
        st.info("No health trend data is available yet. Use the symptom checker, add reports, book appointments, or record medicine adherence to populate this dashboard.")
    else:
        st.markdown('---')
        st.subheader('Health Score Trend')
        if trend_data['health_scores']:
            st.line_chart({'Health Score': trend_data['health_scores']})
            st.caption('Weekly health score trend computed from appointments, reports, medicines, and AI risk signals.')
        else:
            st.info('Health score trend data is not yet available.')

        st.markdown('---')
        appt_chart = {
            'Completed': [trend_data['appointment_counts'][wk]['Completed'] for wk in trend_data['week_keys']],
            'Pending': [trend_data['appointment_counts'][wk]['Pending'] for wk in trend_data['week_keys']],
            'Cancelled': [trend_data['appointment_counts'][wk]['Cancelled'] for wk in trend_data['week_keys']],
        }
        st.subheader('Appointment Trend')
        if any(sum(vals) for vals in appt_chart.values()):
            st.line_chart(appt_chart)
            st.caption('Completed vs Pending vs Cancelled appointments over the last weeks.')
        else:
            st.info('No appointments found for trend analysis.')

        st.markdown('---')
        st.subheader('AI Risk Trend')
        risk_chart = {
            'Low': [trend_data['risk_by_week'][wk]['Low'] for wk in trend_data['week_keys']],
            'Medium': [trend_data['risk_by_week'][wk]['Medium'] for wk in trend_data['week_keys']],
            'High': [trend_data['risk_by_week'][wk]['High'] for wk in trend_data['week_keys']],
        }
        if any(sum(vals) for vals in risk_chart.values()):
            st.bar_chart(risk_chart)
            st.caption('History of AI risk states from symptom and preventive assessments.')
        else:
            st.info('No AI risk assessment history currently available.')

        st.markdown('---')
        st.subheader('Medical Report Trend')
        report_months = sorted(trend_data['report_months'].keys())
        if report_months:
            report_counts = [trend_data['report_months'][m] for m in report_months]
            st.bar_chart({'Reports': report_counts})
            st.write('Months:', ', '.join(report_months))
        else:
            st.info('No reports uploaded yet.')

        st.markdown('---')
        st.subheader('Medicine Adherence Trend')
        adherence_taken = [trend_data['adherence_by_week'][wk]['Taken'] for wk in trend_data['week_keys']]
        adherence_missed = [trend_data['adherence_by_week'][wk]['Missed'] + trend_data['adherence_by_week'][wk]['Skipped'] for wk in trend_data['week_keys']]
        if any(adherence_taken) or any(adherence_missed):
            st.bar_chart({'Taken': adherence_taken, 'Missed': adherence_missed})
            st.caption('Weekly taken versus missed doses based on recent adherence records.')
        else:
            st.info('No medicine adherence records available yet.')

        st.markdown('---')
        related_events = [e for e in collect_timeline_events(patient_id, patient_name) if e['type'] in ('Appointment', 'Report', 'Risk Assessment', 'Symptom Analysis', 'Medicine')]
        if related_events:
            st.subheader('Related Timeline Events')
            event_options = [f"{e['dt'].date() if isinstance(e['dt'], datetime.datetime) else e['dt']} — {e['title']}" for e in related_events]
            selected_index = st.selectbox('Select a related event to inspect', list(range(len(event_options))), format_func=lambda i: event_options[i])
            selected_event = related_events[selected_index]
            st.info(f"**{selected_event['title']}**\n\n{selected_event['description']}\n\nStatus: {selected_event['status']}")
        else:
            st.info('No related timeline events available yet.')

    if st.button('Back to Dashboard', key='back_from_health_trends'):
        st.session_state.page = 'patient_dashboard'
        st.rerun()


# -----------------
# Emergency SOS Page
# -----------------
if st.session_state.page == "patient_sos":
    if "patient" not in st.session_state:
        st.warning("Please login first.")
        st.session_state.page = "patient_login"
        st.rerun()

    render_sidebar_navigation('patient', st.session_state.page)
    patient = st.session_state.patient
    patient_id = patient[0]
    patient_name = patient[1] if len(patient) > 1 else "Patient"
    age = patient[4] if len(patient) > 4 else None
    blood_group = format_profile_field(patient[5] if len(patient) > 5 else None, 'Unknown')
    allergies = format_profile_field(patient[10] if len(patient) > 10 else None, 'None')
    medical_history = format_profile_field(patient[9] if len(patient) > 9 else None, 'None')
    profile_emergency = format_profile_field(patient[7] if len(patient) > 7 else None, 'None')
    contacts = get_emergency_contacts(patient_id) or []
    active_medicines = get_patient_active_medicines(patient_id) or []

    render_page_header("🚨", "Emergency SOS", "Quickly notify your care network and preserve essential emergency details.")
    st.error("Emergency alerts are for urgent use only. Use this page to notify your care team and emergency contacts.")

    left, right = st.columns([3, 1])
    with left:
        st.subheader("Patient Summary")
        st.write(f"**Name:** {patient_name}")
        st.write(f"**Age:** {age or 'Not Provided'}")
        st.write(f"**Blood Group:** {blood_group}")
        st.write(f"**Allergies:** {allergies}")
        st.write(f"**Existing Conditions:** {medical_history}")
        st.write(f"**Primary Emergency Contact:** {profile_emergency}")
        st.write(f"**Current Medicines:** {len(active_medicines)} active medicine(s)")
    with right:
        st.markdown("<div style='padding:20px; border-radius:16px; background:#ffe6e6;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='color:#8a0303;'>🚨 ONE-TAP SOS</h3>", unsafe_allow_html=True)
        st.write("Press only during a real emergency.")
        sos_reason = st.text_area("Reason for SOS", value=st.session_state.get('sos_reason', 'Emergency assistance required.'), key='sos_reason')
        if st.button('🚨 SEND SOS', key='send_sos_button'):
            reason_text = sos_reason.strip() or 'Emergency assistance required.'
            create_sos_event(patient_id, reason_text, status='Sent', doctor_notified=1)
            create_notification('patient', patient_id, 'SOS Triggered', 'Your SOS alert has been sent to your emergency contacts and care team.')
            doctors = get_doctors() or []
            if doctors:
                for doctor in doctors:
                    create_notification('doctor', doctor[0], 'Patient SOS Alert', f'{patient_name} triggered an emergency SOS at {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}.')
            st.success('SOS sent. Notifications have been dispatched to your care team.')
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('---')
    contact_section, summary_section = st.columns([2, 1])
    with contact_section:
        with st.expander('Emergency Contacts', expanded=True):
            if contacts:
                for contact in contacts:
                    cols = st.columns([3, 1, 1])
                    with cols[0]:
                        st.write(f"**{contact[2]}** — {contact[3]}")
                        st.write(f"Phone: {format_phone(contact[4])}")
                    with cols[1]:
                        if st.button('Edit', key=f'edit_sos_contact_{contact[0]}'):
                            st.session_state['edit_sos_contact'] = contact[0]
                            st.session_state['edit_sos_name'] = contact[2]
                            st.session_state['edit_sos_relationship'] = contact[3]
                            st.session_state['edit_sos_phone'] = contact[4]
                            st.rerun()
                    with cols[2]:
                        if st.button('Delete', key=f'delete_sos_contact_{contact[0]}'):
                            delete_emergency_contact(contact[0])
                            st.success('Contact deleted.')
                            st.rerun()
            else:
                st.info('No emergency contacts found. Add one below.')

            st.markdown('#### Add or Update Contact')
            edit_id = st.session_state.get('edit_sos_contact')
            contact_name = st.text_input('Name', value=st.session_state.get('edit_sos_name', ''), key='sos_contact_name')
            contact_relationship = st.text_input('Relationship', value=st.session_state.get('edit_sos_relationship', ''), key='sos_contact_relationship')
            contact_phone = st.text_input('Phone Number', value=st.session_state.get('edit_sos_phone', ''), key='sos_contact_phone')
            if st.button('Save Contact', key='save_sos_contact'):
                if not contact_name.strip() or not contact_relationship.strip() or not contact_phone.strip():
                    st.error('Name, relationship and phone number are required.')
                else:
                    if edit_id:
                        update_emergency_contact(edit_id, name=contact_name.strip(), relationship=contact_relationship.strip(), phone=contact_phone.strip())
                        st.success('Emergency contact updated.')
                        for key in ['edit_sos_contact', 'edit_sos_name', 'edit_sos_relationship', 'edit_sos_phone']:
                            st.session_state.pop(key, None)
                    else:
                        add_emergency_contact(patient_id, contact_name.strip(), contact_relationship.strip(), contact_phone.strip())
                        st.success('Emergency contact added.')
                    st.rerun()
            if edit_id and st.button('Cancel Edit', key='cancel_sos_contact'):
                for key in ['edit_sos_contact', 'edit_sos_name', 'edit_sos_relationship', 'edit_sos_phone']:
                    st.session_state.pop(key, None)
                st.rerun()

    with summary_section:
        st.subheader('Emergency Summary')
        st.metric('SOS Alerts Sent', len(get_sos_events(patient_id=patient_id)))
        st.metric('Primary Contact', profile_emergency)
        st.metric('Active Medicines', len(active_medicines))

    with st.expander('Emergency History', expanded=True):
        sos_history = get_sos_events(patient_id=patient_id)
        if sos_history:
            rows = []
            for event in sos_history:
                date_time = event[4] or ''
                rows.append({
                    'Date': date_time.split(' ')[0] if date_time else '',
                    'Time': date_time.split(' ')[1] if date_time and ' ' in date_time else '',
                    'Reason': event[3] or 'Unspecified',
                    'Status': format_sos_status(event[5]),
                })
            st.table(rows)
        else:
            st.info('No SOS history yet.')

    st.markdown('---')
    with st.expander('Medical Emergency Card', expanded=True):
        pdf_bytes = render_emergency_card_pdf(patient, contacts, active_medicines)
        if isinstance(pdf_bytes, bytearray):
            pdf_bytes = bytes(pdf_bytes)
        elif isinstance(pdf_bytes, str):
            pdf_bytes = pdf_bytes.encode('latin-1', errors='replace')
        st.download_button('Download Emergency Card (PDF)', pdf_bytes, file_name='emergency_card.pdf', mime='application/pdf')

    with st.expander('Nearby Help', expanded=True):
        card_style = 'padding:18px; border-radius:16px; background:#f4f4f4; margin-bottom:12px;'
        h1, h2, h3 = st.columns(3)
        with h1:
            st.markdown(f"<div style='{card_style}'><h4>Hospital</h4><p>🏥 Example General Hospital</p><p>24/7 emergency care</p><p><i>Location placeholder for future maps</i></p></div>", unsafe_allow_html=True)
        with h2:
            st.markdown(f"<div style='{card_style}'><h4>Ambulance</h4><p>🚑 Rapid Response Services</p><p>Call local EMS</p><p><i>Integration with live dispatch coming soon</i></p></div>", unsafe_allow_html=True)
        with h3:
            st.markdown(f"<div style='{card_style}'><h4>Pharmacy</h4><p>💊 24/7 Community Pharmacy</p><p>Nearby urgent medication support</p><p><i>Maps integration coming soon</i></p></div>", unsafe_allow_html=True)

    if st.button('Back to Dashboard', key='back_from_sos'):
        st.session_state.page = 'patient_dashboard'
        st.rerun()


# -----------------
# Patient Profile
# -----------------
if st.session_state.page == "patient_profile":
    if "patient" not in st.session_state:
        st.warning("Please login first.")
        st.session_state.page = "patient_login"
        st.rerun()

    render_sidebar_navigation('patient', st.session_state.page)
    patient = st.session_state.patient
    patient_id = patient[0]

    render_page_header("🧾", "Patient Health Profile", "Review and update your health profile information in one place.")

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

    render_sidebar_navigation('patient', st.session_state.page)
    patient = st.session_state.patient
    patient_id = patient[0]
    patient_name = patient[1] if len(patient) > 1 else "Patient"

    render_page_header("👨‍👩‍👧", "Family Health Dashboard", f"Track family members, live queue status, and support planning for {patient_name}.")
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

    render_sidebar_navigation('doctor', st.session_state.page)
    doctor = st.session_state.doctor
    # doctor tuple: (id, name, email, password, phone, specialization, clinic_name, clinic_address, clinic_id)
    doctor_name = doctor[1] if len(doctor) > 1 else "Doctor"
    doctor_specialization = doctor[5] if len(doctor) > 5 else ""
    clinic_name = doctor[6] if len(doctor) > 6 else ""
    clinic_id = doctor[8] if len(doctor) > 8 else None

    render_page_header("🏥", "Doctor Dashboard", f"Welcome, Dr. {doctor_name}. Manage clinic operations, appointments, and patient care.")
    st.success("Login Successful!")
    # show one-time flash for prescription save
    if "prescription_flash" in st.session_state:
        st.success(st.session_state.pop("prescription_flash"))
    st.markdown("<div class='section-card'>", unsafe_allow_html=True)
    st.write(f"**Name:** {doctor_name}")
    st.write(f"**Specialization:** {doctor_specialization}")
    if clinic_name:
        st.write(f"**Clinic:** {clinic_name}")
    st.markdown("</div>", unsafe_allow_html=True)

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

    st.markdown('---')
    st.subheader('Recent SOS Alerts')
    sos_alerts = get_recent_sos_alerts(limit=8) or []
    if sos_alerts:
        alert_rows = []
        for sos in sos_alerts:
            patient_info = get_patient_by_id(sos[1])
            alert_rows.append({
                'Patient': patient_info[1] if patient_info else 'Unknown',
                'Time': sos[4] or 'Unknown',
                'Reason': sos[3] or 'Unspecified',
                'Status': format_sos_status(sos[5]),
            })
        st.table(alert_rows)
    else:
        st.info('No SOS alerts yet.')

    # Analytics summary for the doctor
    today = datetime.date.today().isoformat()
    appointments_for_doctor = get_appointments_by_doctor(doctor_name, clinic_id=clinic_id)
    unique_patients = set()
    status_counts = {
        'Pending': 0,
        'Completed': 0,
        'Cancelled': 0,
        'In Progress': 0,
    }
    last_7_days = [(datetime.date.today() - datetime.timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
    appointment_trend = {day: 0 for day in last_7_days}
    for a in appointments_for_doctor:
        patient_name = a[1]
        appointment_date = a[3]
        appointment_status = a[6] if len(a) > 6 else 'Pending'
        unique_patients.add(patient_name)
        status_counts[appointment_status] = status_counts.get(appointment_status, 0) + 1
        if appointment_date in appointment_trend:
            appointment_trend[appointment_date] += 1

    total_appointments = sum(status_counts.values())
    completed_appointments = status_counts.get('Completed', 0)
    completion_rate = int((completed_appointments / total_appointments) * 100) if total_appointments else 0
    average_daily_load = round(sum(appointment_trend.values()) / 7, 1)
    recent_prescriptions = get_prescriptions_by_doctor(doctor[0], limit=5)
    patient_ids = []
    for patient_name in unique_patients:
        profile = get_patient_profile(patient_name)
        if profile:
            patient_ids.append(profile[0])
    recent_analyses = get_analyses_by_patient_ids(patient_ids, limit=5)
    total_analyses = len(recent_analyses)

    st.markdown('---')
    st.subheader('Doctor Analytics')
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric('Active Patients', len(unique_patients))
    metric_col2.metric('Completion Rate', f'{completion_rate}%')
    metric_col3.metric('Avg Daily Load', average_daily_load)
    metric_col4.metric('AI Analyses', total_analyses)

    chart_col, quick_action_col = st.columns([3, 1])
    with chart_col:
        st.markdown('#### Appointment Trend (last 7 days)')
        if any(appointment_trend.values()):
            st.line_chart([appointment_trend[day] for day in last_7_days])
            st.write('Dates:', ', '.join(last_7_days))
        else:
            st.info('No appointments in the last 7 days.')

        st.markdown('#### Status Distribution')
        if total_appointments:
            st.bar_chart(status_counts)
        else:
            st.info('No appointment status data yet.')

    with quick_action_col:
        st.markdown('#### Quick Actions')
        if st.button('Start Next Patient', key='doctor_next_patient'):
            try:
                mark_next_patient(doctor_name, today, clinic_id=clinic_id)
                st.success('Advanced to next patient in queue.')
            except Exception as e:
                st.error(f'Unable to advance queue: {e}')
            st.rerun()

        if st.button('Refresh Dashboard', key='doctor_refresh_dashboard'):
            st.rerun()

        if st.button('Toggle Queue View', key='doctor_toggle_queue'):
            st.session_state['show_doctor_queue'] = not st.session_state.get('show_doctor_queue', False)
            st.rerun()

        if st.session_state.get('show_doctor_queue'):
            st.markdown('---')
            st.markdown('#### Today\'s Queue')
            today_queue = get_queue_for_doctor_date(doctor_name, today, clinic_id=clinic_id)
            if today_queue:
                for q in today_queue:
                    q_num = q[5] if len(q) > 5 else None
                    q_status = q[6] if len(q) > 6 else 'Pending'
                    st.write(f'#{q_num} — {q[1]} at {q[4]} ({q_status})')
            else:
                st.info('No queue entries for today.')

    st.markdown('---')
    st.subheader('Recent Activity')
    activity_items = []
    sorted_appointments = sorted(
        appointments_for_doctor,
        key=lambda x: (x[3], x[4]),
        reverse=True
    )
    for appt in sorted_appointments[:5]:
        appt_date = appt[3]
        appt_time = appt[4]
        status = appt[6] if len(appt) > 6 else 'Pending'
        activity_items.append((f'{appt_date} {appt_time}', f'Appointment for {appt[1]} — {status}'))

    for pres in recent_prescriptions:
        pres_date = pres[3] or ''
        patient_name = pres[10] if len(pres) > 10 else 'Patient'
        activity_items.append((pres[8] or pres_date, f'Prescription written for {patient_name}'))

    for analysis in recent_analyses[:5]:
        analysis_date = analysis[3] or ''
        patient_id = analysis[1]
        patient = get_patient_by_id(patient_id)
        patient_name = patient[1] if patient else 'Patient'
        activity_items.append((analysis_date, f'AI analysis saved for {patient_name}'))

    notifications_feed = get_notifications('doctor', doc_id, unread_only=False, limit=5, clinic_id=clinic_id)
    for note in notifications_feed:
        note_date = note[6] if len(note) > 6 else ''
        activity_items.append((note_date, f'Notification: {note[4]}'))

    if activity_items:
        activity_items.sort(reverse=True)
        for _, message in activity_items[:8]:
            st.write(f'- {message}')
    else:
        st.info('No recent activity yet.')

    st.markdown('---')
    st.subheader('Patient Adherence Insights')
    try:
        doctor_meds = get_medicines_by_doctor(doctor[0]) or []
        patient_adherence = {}
        for med in doctor_meds:
            pid = med[1]
            if pid not in patient_adherence:
                patient = get_patient_by_id(pid)
                patient_adherence[pid] = {
                    'name': patient[1] if patient else 'Unknown',
                    'summary': summarize_medication_adherence(pid),
                }
        if patient_adherence:
            low_rows = []
            for pid, details in patient_adherence.items():
                low_rows.append({
                    'Patient': details['name'],
                    'Adherence': f"{details['summary']['overall_adherence']}%",
                    'Active Medicines': details['summary']['active_medicines'],
                    'Missed Doses': details['summary']['missed_doses'],
                })
            st.table(low_rows)
            poor = [p for p in patient_adherence.values() if is_poor_adherence_summary(p['summary'])]
            if poor:
                st.warning(f"{len(poor)} patient(s) have adherence below 80%.")
            else:
                st.success('No patients with low adherence in your panel.')
            patient_names = [f"{details['name']} ({pid})" for pid, details in patient_adherence.items()]
            selected_patient = st.selectbox('Select patient to view detail', [''] + patient_names, key='doctor_adherence_patient')
            if selected_patient:
                selected_pid = int(selected_patient.split('(')[-1].strip(')'))
                summary = patient_adherence[selected_pid]['summary']
                st.write(f"**{patient_adherence[selected_pid]['name']}** adherence: {summary['overall_adherence']}%")
                st.write(f"Active medicines: {summary['active_medicines']}")
                st.write(f"Missed doses: {summary['missed_doses']}")
                st.write('Upcoming medicines:')
                for dose, _ in summary['upcoming_medicines'][:5]:
                    st.write(f"- {dose['date']} {dose['medicine_name']} ({dose['scheduled_time']})")
        else:
            st.info('No medicine records found for your patients yet.')
    except Exception:
        st.info('Unable to load patient adherence insights.')

    st.markdown('---')
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

        st.markdown("---")
        st.subheader("Patient Medical Reports")
        patient_reports_map = {}
        for a in appointments:
            patient_name = a[1]
            profile = get_patient_profile(patient_name)
            if profile:
                pid = profile[0]
                if pid not in patient_reports_map:
                    patient_reports_map[pid] = {
                        'name': patient_name,
                        'reports': get_reports_by_patient(pid),
                        'appointments': []
                    }
                patient_reports_map[pid]['appointments'].append((a[3], a[4], a[6] if len(a) > 6 else 'Pending'))

        if patient_reports_map:
            for pid, info in patient_reports_map.items():
                st.markdown(f"**{info['name']}**")
                st.write("_Appointments:_")
                for appt_date, appt_time, appt_status in info['appointments']:
                    st.write(f"- {appt_date} at {appt_time} ({appt_status})")
                reports = info['reports']
                if reports:
                    for report_id, _, report_name, report_type, file_path, upload_date, notes in reports:
                        with st.expander(f"{report_name} — {report_type} ({upload_date})"):
                            st.write(f"**Report Type:** {report_type}")
                            st.write(f"**Uploaded:** {upload_date}")
                            if notes:
                                st.write(f"**Notes:** {notes}")
                            if file_path and os.path.exists(file_path):
                                ext = get_file_extension(file_path)
                                mime_type = "application/pdf" if ext == "pdf" else "image/jpeg" if ext in {"jpg", "jpeg"} else "image/png"
                                with open(file_path, "rb") as file_data:
                                    st.download_button(
                                        label="Download Report",
                                        data=file_data.read(),
                                        file_name=os.path.basename(file_path),
                                        mime=mime_type,
                                        key=f"doctor_download_{report_id}"
                                    )
                            else:
                                st.error("Report file missing on server.")
                            # Previous AI analyses for this report (doctor view)
                            try:
                                analyses = get_analyses_by_report(report_id)
                            except Exception:
                                analyses = []

                            if analyses:
                                st.markdown('#### Previous AI Analyses')
                                for a in analyses:
                                    aid, pid, rid, a_date, summary, recs, details = a
                                    st.write(f"- {a_date}: {summary}")
                                    if st.button('View Analysis', key=f'doc_view_analysis_{aid}'):
                                        try:
                                            payload = json.loads(details) if details else {}
                                        except Exception:
                                            payload = {}
                                        st.markdown('---')
                                        st.write(f"**Analysis Date:** {a_date}")
                                        st.write(f"**Summary:** {summary}")
                                        if payload.get('abnormal_values'):
                                            st.write('**Abnormal Values:**')
                                            for v in payload.get('abnormal_values'):
                                                sev = v.get('severity','yellow')
                                                textv = f"{v.get('name')}: {v.get('value')} {v.get('unit')}"
                                                if sev == 'red':
                                                    st.error(textv)
                                                elif sev == 'yellow':
                                                    st.warning(textv)
                                                else:
                                                    st.success(textv)
                                        if st.button('Download Analysis PDF', key=f'doc_download_analysis_{aid}'):
                                            try:
                                                pdf_bytes = make_analysis_pdf(payload, info.get('name','Patient'), report_name)
                                                st.download_button(label='Download PDF', data=pdf_bytes, file_name=f"analysis_{aid}.pdf", mime='application/pdf')
                                            except Exception as e:
                                                st.error(f"Failed to generate PDF: {e}")

                            if st.button('AI Report Analysis', key=f'doc_analyze_{report_id}'):
                                try:
                                    text = extract_text_from_file(file_path)
                                except Exception as e:
                                    st.error(f'Failed to extract text: {e}')
                                    text = None
                                if text:
                                    try:
                                        analysis = analyze_report_text(text)
                                    except Exception as e:
                                        st.error(f'Analysis failed: {e}')
                                        analysis = None
                                    if analysis:
                                        try:
                                            insert_report_analysis(pid, report_id, datetime.datetime.now().isoformat(), analysis.get('summary',''), json.dumps(analysis.get('recommended_specialists') or []), json.dumps(analysis))
                                            st.success('Analysis saved.')
                                        except Exception as e:
                                            st.error(f'Failed to save analysis: {e}')
                                        # show abbreviated results
                                        st.markdown('**AI Analysis Summary**')
                                        st.write(analysis.get('summary'))
                                        if analysis.get('abnormal_values'):
                                            for v in analysis.get('abnormal_values'):
                                                sev = v.get('severity','yellow')
                                                textv = f"{v.get('name')}: {v.get('value')} {v.get('unit')}"
                                                if sev == 'red':
                                                    st.error(textv)
                                                elif sev == 'yellow':
                                                    st.warning(textv)
                                                else:
                                                    st.success(textv)
                else:
                    st.info("No reports uploaded for this patient.")
        else:
            st.info("No patient reports available for your scheduled appointments.")

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

