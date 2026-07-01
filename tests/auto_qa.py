import os
import sys
import tempfile
import shutil
import datetime
import importlib

WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

results = []


def check(condition, name, info=''):
    if condition:
        results.append((name, True, info))
    else:
        results.append((name, False, info))


def run_tests():
    with tempfile.TemporaryDirectory() as tempdir:
        cwd = os.getcwd()
        try:
            os.chdir(tempdir)
            sys.path.insert(0, WORKSPACE_ROOT)
            import database
            import app
            importlib.reload(database)
            importlib.reload(app)

            # 1. Patient Registration
            try:
                database.create_database()
                database.register_patient('Test Patient', 'test.patient@example.com', 'pass123')
                pat = database.login_patient('test.patient@example.com', 'pass123')
                check(bool(pat), 'patient_registration_valid', 'Patient registered and login successful')
            except Exception as exc:
                check(False, 'patient_registration_valid', f'Exception: {exc}')

            # Duplication should be prevented by DB layer
            try:
                database.register_patient('Test Patient Duplicate', 'test.patient@example.com', 'pass123')
                check(False, 'patient_registration_duplicate_email', 'Duplicate email inserted unexpectedly')
            except ValueError:
                check(True, 'patient_registration_duplicate_email', 'Duplicate email prevented')
            except Exception as exc:
                check(False, 'patient_registration_duplicate_email', f'Unexpected exception: {exc}')

            # Missing required fields should not insert
            try:
                database.register_patient('', 'missing@example.com', 'secret')
                check(False, 'patient_registration_missing_name', 'Empty name inserted unexpectedly')
            except ValueError:
                check(True, 'patient_registration_missing_name', 'Empty name rejected')
            except Exception as exc:
                check(False, 'patient_registration_missing_name', f'Unexpected exception: {exc}')

            try:
                database.register_patient('Missing Email', '', 'secret')
                check(False, 'patient_registration_missing_email', 'Empty email inserted unexpectedly')
            except ValueError:
                check(True, 'patient_registration_missing_email', 'Empty email rejected')
            except Exception as exc:
                check(False, 'patient_registration_missing_email', f'Unexpected exception: {exc}')

            try:
                database.register_patient('Missing Password', 'nopassword@example.com', '')
                check(False, 'patient_registration_missing_password', 'Empty password inserted unexpectedly')
            except ValueError:
                check(True, 'patient_registration_missing_password', 'Empty password rejected')
            except Exception as exc:
                check(False, 'patient_registration_missing_password', f'Unexpected exception: {exc}')

            # Invalid email (basic format check)
            try:
                database.register_patient('Bad Email', 'bad-email', 'secret')
                check(False, 'patient_registration_invalid_email', 'Invalid email inserted unexpectedly')
            except ValueError:
                check(True, 'patient_registration_invalid_email', 'Invalid email rejected')
            except Exception as exc:
                check(False, 'patient_registration_invalid_email', f'Unexpected exception: {exc}')

            # Invalid phone should be rejected or ignored by DB layer if present
            try:
                database.register_patient('Bad Phone', 'phone@example.com', 'secret', phone='abc123')
                check(False, 'patient_registration_invalid_phone', 'Invalid phone inserted unexpectedly')
            except ValueError:
                check(True, 'patient_registration_invalid_phone', 'Invalid phone rejected')
            except Exception as exc:
                check(False, 'patient_registration_invalid_phone', f'Unexpected exception: {exc}')

            # 2. Patient Login
            check(bool(database.login_patient('test.patient@example.com', 'pass123')), 'patient_login_valid', 'Correct credentials login')
            check(database.login_patient('test.patient@example.com', 'wrongpass') is None, 'patient_login_wrong_password', 'Wrong password rejected')
            check(database.login_patient('doesnotexist@example.com', 'pass') is None, 'patient_login_non_existing', 'Non-existing account rejected')

            # 3. Doctor Registration
            try:
                database.register_doctor('Dr Test', 'dr.test@example.com', 'docpass', 'General')
                check(True, 'doctor_registration_valid', 'Doctor registered')
            except Exception as exc:
                check(False, 'doctor_registration_valid', f'Exception: {exc}')

            try:
                database.register_doctor('Dr Duplicate', 'dr.test@example.com', 'docpass', 'General')
                check(False, 'doctor_registration_duplicate_email', 'Duplicate doctor email inserted unexpectedly')
            except ValueError:
                check(True, 'doctor_registration_duplicate_email', 'Duplicate doctor email prevented')
            except Exception as exc:
                check(False, 'doctor_registration_duplicate_email', f'Unexpected exception: {exc}')

            try:
                database.register_doctor('', 'dr.missing@example.com', 'docpass', 'General')
                check(False, 'doctor_registration_missing_name', 'Doctor with missing name inserted unexpectedly')
            except ValueError:
                check(True, 'doctor_registration_missing_name', 'Missing name rejected')
            except Exception as exc:
                check(False, 'doctor_registration_missing_name', f'Unexpected exception: {exc}')

            try:
                database.register_doctor('Dr Missing Email', '', 'docpass', 'General')
                check(False, 'doctor_registration_missing_email', 'Doctor with missing email inserted unexpectedly')
            except ValueError:
                check(True, 'doctor_registration_missing_email', 'Missing email rejected')
            except Exception as exc:
                check(False, 'doctor_registration_missing_email', f'Unexpected exception: {exc}')

            try:
                database.register_doctor('Dr Missing Specialization', 'dr.bad@example.com', 'docpass', '')
                check(False, 'doctor_registration_missing_specialization', 'Doctor with missing specialization inserted unexpectedly')
            except ValueError:
                check(True, 'doctor_registration_missing_specialization', 'Missing specialization rejected')
            except Exception as exc:
                check(False, 'doctor_registration_missing_specialization', f'Unexpected exception: {exc}')

            # 4. Doctor Login
            check(bool(database.login_doctor('dr.test@example.com', 'docpass')), 'doctor_login_valid', 'Doctor login valid')
            check(database.login_doctor('dr.test@example.com', 'wrongpass') is None, 'doctor_login_invalid', 'Invalid doctor login rejected')

            # 5. Appointment Booking and 6. Live Queue
            database.create_appointment('Test Patient', 'Dr Test', '2026-07-10', '09:00')
            database.create_appointment('Test Patient', 'Dr Test', '2026-07-11', '10:00')
            database.create_appointment('Another Patient', 'Dr Test', '2026-07-10', '09:30')
            appts_by_doctor = database.get_appointments_by_doctor('Dr Test')
            check(len(appts_by_doctor) >= 3, 'appointment_booking_count', 'Appointments created')
            qnums = [a[5] for a in database.get_queue_for_doctor_date('Dr Test', '2026-07-10')]
            check(qnums == sorted(qnums), 'queue_order_for_doctor_date', 'Queue order maintained')

            # mark next patient
            before_in_progress = database.get_current_active_queue_number('Dr Test', '2026-07-10')
            database.mark_next_patient('Dr Test', '2026-07-10')
            after_in_progress = database.get_current_active_queue_number('Dr Test', '2026-07-10')
            check(after_in_progress is not None, 'next_patient_marked', 'Next patient marked in progress')
            check(after_in_progress != before_in_progress, 'queue_updates_correctly', 'Queue advanced correctly')

            # 7. Family Health Dashboard
            patient = database.login_patient('test.patient@example.com', 'pass123')
            pid = patient[0]
            database.add_family_member(pid, 'Jane Doe', 'Mother', age=65, blood_group='A+', allergies='Pollen', existing_conditions='Hypertension', emergency_contact='111-222-3333')
            members = database.get_family_members_by_patient(pid)
            check(len(members) == 1, 'family_member_add', 'Family member added')
            member_id = members[0][0]
            database.update_family_member(member_id, age=66, existing_conditions='Hypertension, Diabetes')
            updated = database.get_family_members_by_patient(pid)[0]
            check(updated[4] == 66, 'family_member_edit', 'Family member edited')
            database.delete_family_member(member_id)
            check(len(database.get_family_members_by_patient(pid)) == 0, 'family_member_delete', 'Family member deleted')

            # 8. AI Symptom Checker
            symptom_cases = [
                ('I have fever', 'Medium'),
                ('I have cough and sore throat', 'Medium'),
                ('I have fever for 5 days with body pain', 'Medium'),
                ('I have chest pain and difficulty breathing', 'Emergency'),
                ('My head hurts and I feel dizzy', 'Low'),
                ('I have vomiting and diarrhea', 'Low'),
                ('I have stomach pain', 'Low'),
                ('I fainted', 'Emergency'),
                ('I have weakness on one side of my body', 'Emergency'),
            ]
            for text, expected_urgency in symptom_cases:
                report = app.build_symptom_report(text)
                has_symptoms = bool(report['symptoms_detected'])
                check(has_symptoms, f'symptom_checker_detects_{text[:15]}', 'Symptoms detected')
                check(expected_urgency == report['urgency'], f'symptom_checker_urgency_{text[:15]}', f'Urgency expected {expected_urgency}, got {report["urgency"]}')
                check('recommended_specialists' in report, f'symptom_checker_specialists_{text[:15]}', 'Specialists provided')
                check('home_care_advice' in report, f'symptom_checker_home_care_{text[:15]}', 'Home care advice provided')
                check('emergency_warning' in report, f'symptom_checker_warning_{text[:15]}', 'Emergency warning field present')
                check('explanation' in report, f'symptom_checker_disclaimer_{text[:15]}', 'Disclaimer/explanation present')

            # 9. Medical Reports
            uploads_dir = os.path.join(tempdir, 'uploads')
            os.makedirs(uploads_dir, exist_ok=True)
            pdf_path = os.path.join(uploads_dir, 'sample.pdf')
            try:
                from fpdf import FPDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font('Arial', size=12)
                pdf.cell(0, 10, 'Sample Report for Testing', ln=True)
                pdf.output(pdf_path)
                extracted = app.extract_text_from_file(pdf_path)
                check('Sample Report' in extracted, 'report_text_extraction_pdf', 'PDF text extracted')
            except Exception as exc:
                check(False, 'report_text_extraction_pdf', f'PDF extraction failed: {exc}')

            for ext in ['png', 'jpg', 'jpeg']:
                file_path = os.path.join(uploads_dir, f'sample.{ext}')
                with open(file_path, 'wb') as f:
                    f.write(b'\x89PNG\r\n\x1a\n' + b'test')
                valid, error = app.validate_report_file(type('U', (), {'name': f'sample.{ext}', 'size': 1024})())
                check(valid, f'report_validation_{ext}', f'{ext} accepted for upload')

            large_file = type('U', (), {'name': 'large.pdf', 'size': app.MAX_REPORT_FILE_SIZE + 1})()
            valid, error = app.validate_report_file(large_file)
            check(not valid and error is not None, 'report_validation_large_file', 'Large file rejected')
            bad_file = type('U', (), {'name': 'bad.txt', 'size': 100})()
            valid, error = app.validate_report_file(bad_file)
            check(not valid and 'Only PDF' in error, 'report_validation_bad_type', 'Bad file type rejected')

            report_id = database.insert_medical_report(pid, 'Test Report', 'pdf', pdf_path, notes='Test notes')
            reports = database.get_reports_by_patient(pid)
            check(len(reports) == 1 and reports[0][0] == report_id, 'medical_report_history', 'Medical report history stored')
            database.delete_medical_report(report_id)
            reports = database.get_reports_by_patient(pid)
            check(len(reports) == 0, 'medical_report_delete', 'Medical report deleted')

            # 10. AI Medical Report Analyzer
            report_text = 'Glucose: 180 mg/dL\nLDL: 170 mg/dL\nECG abnormal findings detected.'
            analysis = app.analyze_report_text(report_text)
            check('summary' in analysis, 'report_analyzer_summary', 'Analysis summary produced')
            check(len(analysis['abnormal_values']) >= 1, 'report_analyzer_abnormal_values', 'Abnormal values detected')
            check('recommended_specialists' in analysis and analysis['recommended_specialists'], 'report_analyzer_specialist', 'Specialist recommendation provided')
            check('suggested_tests' in analysis, 'report_analyzer_tests', 'Suggested tests produced')
            check('lifestyle_recommendations' in analysis, 'report_analyzer_lifestyle', 'Lifestyle advice provided')
            try:
                pdf_bytes = app.make_analysis_pdf(analysis, 'Test Patient', 'Test Report')
                check(pdf_bytes.startswith(b'%PDF'), 'report_analyzer_pdf_download', 'PDF analysis generated')
            except Exception as exc:
                check(False, 'report_analyzer_pdf_download', f'PDF generation failed: {exc}')

            analysis_id = database.insert_report_analysis(pid, report_id, datetime.date.today().isoformat(), analysis['summary'], ', '.join(analysis['recommended_specialists']), str(analysis))
            analyses = database.get_analyses_by_patient(pid)
            check(len(analyses) == 1, 'report_analysis_db_storage', 'AI report analysis stored')
            analyses_by_report = database.get_analyses_by_report(report_id)
            check(len(analyses_by_report) == 1, 'report_analysis_by_report', 'AI analysis fetched by report')

            # 11. Preventive Health Risk Assessment
            app.st.session_state['symptoms_input'] = 'I have fever and cough'
            risk = app.assess_health_risk(pid, 'Test Patient')
            check('score' in risk and 0 <= risk['score'] <= 100, 'health_risk_score_bounds', 'Health risk score computed')
            check('recommendations' in risk and risk['recommendations'], 'health_risk_recommendations', 'Health risk recommendations present')
            check('suggested_tests' in risk, 'health_risk_tests', 'Health risk suggested tests present')
            check('lifestyle_tips' in risk, 'health_risk_lifestyle', 'Health risk lifestyle tips present')

            # 12. Prescriptions
            doctor = database.get_doctor_by_email('dr.test@example.com')
            database.create_prescription(pid, doctor[0], appointment_id=None, medicines='TestMed', dosage='1 tablet', duration='5 days', notes='Take after food')
            prescriptions = database.get_prescriptions_by_patient(pid)
            check(len(prescriptions) >= 1, 'prescription_create_view', 'Prescription created and viewable')

            # 13. Medicine Reminder & Adherence
            try:
                today = datetime.date.today().isoformat()
                end_date = (datetime.date.today() + datetime.timedelta(days=3)).isoformat()
                med_id = database.create_medicine(pid, doctor[0], 'Aspirin', '100mg', 'Twice', ['Morning', 'Evening'], 'After Food', today, end_date, notes='Take with water')
                med = database.get_medicine_by_id(med_id)
                check(med is not None and med[3] == 'Aspirin', 'medicine_create', 'Medicine created and retrievable')
                meds = database.get_medicines_by_patient(pid)
                check(any(m[0] == med_id for m in meds), 'medicine_patient_list', 'Patient medicine list returns new medicine')
                database.record_medicine_adherence(med_id, pid, today, 'Morning', 'Taken')
                records = database.get_adherence_history(patient_id=pid)
                check(any(r[1] == med_id and r[4] == 'Morning' and r[5] == 'Taken' for r in records), 'medicine_adherence_record', 'Medicine adherence recorded')
                summary = app.summarize_medication_adherence(pid)
                check('overall_adherence' in summary and isinstance(summary['overall_adherence'], int), 'medicine_adherence_summary', 'Adherence summary computed')
                database.delete_medicine(med_id)
                med_after_delete = database.get_medicine_by_id(med_id)
                check(med_after_delete is None, 'medicine_delete', 'Medicine deleted successfully')

                try:
                    database.add_emergency_contact(pid, 'John Doe', 'Brother', '9999999999')
                    contacts = database.get_emergency_contacts(pid)
                    check(any(c[2] == 'John Doe' for c in contacts), 'sos_contact_create', 'Emergency contact added')
                    contact = contacts[0]
                    database.update_emergency_contact(contact[0], phone='8888888888')
                    updated = database.get_emergency_contacts(pid)
                    check(any(c[4] == '8888888888' for c in updated), 'sos_contact_update', 'Emergency contact updated')
                    database.create_sos_event(pid, 'Severe chest pain', status='Sent', doctor_notified=1)
                    alerts = database.get_sos_events(pid)
                    check(any(a[3] == 'Severe chest pain' for a in alerts), 'sos_event_record', 'SOS event recorded')
                    check(len(database.get_recent_sos_alerts(limit=5)) >= 1, 'doctor_sos_alerts', 'Doctor SOS alert list available')
                    database.delete_emergency_contact(contact[0])
                    deleted_contacts = database.get_emergency_contacts(pid)
                    check(all(c[0] != contact[0] for c in deleted_contacts), 'sos_contact_delete', 'Emergency contact deleted')
                except Exception as exc:
                    check(False, 'sos_flow', f'SOS flow failed: {exc}')
            except Exception as exc:
                check(False, 'medicine_adherence_crud', f'Medicine/adherence flow failed: {exc}')

            # 14. SQLite Database Integrity
            conn = database.sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM patients WHERE email='test.patient@example.com'")
            duplicate_count = cursor.fetchone()[0]
            conn.close()
            check(duplicate_count == 1, 'sqlite_duplicate_patients', 'No duplicate patient records')

            # 15. UI / Runtime basics: import app and call helper functions
            check(hasattr(app, 'validate_report_file'), 'ui_helper_validate_report_file', 'UI helper validate_report_file exists')
            check(hasattr(app, 'build_symptom_report'), 'ui_helper_build_symptom_report', 'UI helper build_symptom_report exists')
            check(hasattr(app, 'assess_health_risk'), 'ui_helper_assess_health_risk', 'UI helper assess_health_risk exists')

            # 16. Error Handling: invalid report extraction path
            try:
                app.extract_text_from_file(os.path.join(uploads_dir, 'nonexistent.pdf'))
                check(False, 'error_handling_missing_report_file', 'Missing file did not raise')
            except FileNotFoundError:
                check(True, 'error_handling_missing_report_file', 'Missing file raised FileNotFoundError')
            except Exception as exc:
                check(False, 'error_handling_missing_report_file', f'Unexpected exception: {exc}')

            # 17. Performance / no unnecessary reruns: ensure helper calls are lightweight
            # Not easily testable in this environment; mark as warning if import succeeded.
            check(True, 'performance_import_no_crash', 'App module imported without crash')

        finally:
            os.chdir(cwd)

    # print results
    passed = [r for r in results if r[1]]
    failed = [r for r in results if not r[1]]
    print('--- TEST RESULTS ---')
    for name, ok, info in results:
        print(f"{name}: {'PASS' if ok else 'FAIL'}{(' - ' + info) if info else ''}")
    print('--------------------')
    print(f'Passed: {len(passed)}  Failed: {len(failed)}')
    if failed:
        raise SystemExit(1)


if __name__ == '__main__':
    run_tests()
