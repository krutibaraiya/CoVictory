from flask import Flask, request, render_template, redirect, url_for, flash, session
from email_validator import validate_email
from DB_Operations import *

import re
from flask_login import login_required, logout_user, login_user, login_manager, LoginManager
from datetime import datetime, timedelta, date
from flask_mail import Mail, Message


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return user_id

mail= Mail(app)
 
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'developercovictory@gmail.com'
app.config['MAIL_PASSWORD'] = 'covictory_admin21'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

@app.route("/", methods=["GET","POST"])
def home():
    centers = get_total_centers()
    doctors = get_total_doctors()
    patients = get_total_patients()
    if request.method == "POST":
        feedback_value = request.form["feedback"]
        feedback(feedback_value)
    return render_template('home.html', centers = centers, doctors= doctors, patients = patients)

@app.route("/feedback/", methods=["GET","POST"])
def feedback_page():
    f = get_feedback()
    return render_template('feedback-page.html', feedback = f)

@app.route("/admin-login/",methods=["GET", "POST"])
def adminLogin():
    if request.method == "POST":
        email = request.form["emailAddress"]
        password = request.form["password"]

        if email == 'developercovictory@gmail.com' and password == 'admin_covictory21':
            return redirect(url_for('admin'))
        else:
            return redirect(url_for('admin'))
    return render_template('admin-login.html')
@app.route("/admin", methods=["GET","POST"])
def admin():
    return render_template('admin.html')

@app.route("/developer/",methods=["GET","POST"])
def developer():
    return render_template('developer.html')


@login_required
@app.route("/doctor-home/",methods=["GET", "POST"])
def DoctorHome():
    did = session['did']
    name = get_doctor_name(did)
    return render_template('doctor-home.html', name = name)

@app.route("/mail-report/",methods=["GET","POST"])
def mailReport():
   msg = Message('CoVictory Vaccination Report', sender = 'developercovictory@gmail.com', recipients = [session['p_email']])
   pid = get_pid(session['p_email'])
   patient = get_patient_report_details(pid)
   dob = get_age(patient[4])
   did = get_did_from_pid(pid)
   phno = get_doctor_phno(did)
   doctor = get_doctor_report_details(did)
   vid = get_vid(session['p_email'])
   center = get_center_report_details(vid)
   date1 = get_date(pid)
   date2 = datetime.strptime(date1, "%Y-%m-%d")+timedelta(days=28)
   date2 = date2.date()
   status = get_status(pid)
   print("Mailing")
   messageBody = f"""
   Vaccination Report for {patient[0]} {patient[1]}
   Center Name: {center[1]}
   Doctor Name: {doctor[0]}
   City: {center[0]}
   Doctor's email: {doctor[1]}
   

   Age: {dob}
   Gender: {patient[3]}
   Date of 1st Dose: {date1}
   Date of 2nd Dose: {date2}



   Sent to you by the CoVictory Team
   """
   
   msg.body = messageBody
   mail.send(msg)
   return render_template('vaccination-report.html',status = status, patient = patient,center = center, doctor=doctor, date1 = date1, date2 = date2, dob = dob)

@app.route("/vaccination-center/", methods=["GET", "POST"])
def VaccinationCenter():
    centers = get_centers()
    if request.method == 'POST':
        session['vid_value'] = request.form["vid"]
        return redirect(url_for('Slot'))
    return render_template('vaccination-center.html', centers = centers)

@app.route("/patient-update/", methods=["GET, POST"])
def PatientUpdate():
    did = session['did']
    patients = get_patient_details(did)
    if request.method == 'POST':
        session['pid'] = request.form["pid"]
        return "Patient Report"
    return render_template('select-patient.html', patients = patients)


@app.route("/slot/", methods=["GET","POST"])
def Slot():
    slots = get_slots(session['vid_value'])
    dropdown_slots = get_dropdown_slots(session['vid_value'])
    if request.method == "POST":
        slot_value = request.form["slot"]
        slots = slot_value.split(',')     
        session['slot_date'] = slots[1]
        session['slot_time'] = slots[0]
        session['did'] = get_slot_did(session['vid_value'], session['slot_date'], session['slot_time'])
        return redirect(url_for('PatientRegister'))
    return render_template('slot.html', slots = slots, dropdown_slots=dropdown_slots)


@app.route("/patient-register/", methods=["POST", "GET"])
def PatientRegister():
    if request.method == 'POST':
        firstName_value = request.form["firstName"]
        lastName_value = request.form["lastName"]
        emailAddress_value = request.form["emailAddress"]
        gender_value = request.form["inlineRadioOptions"]
        dob_value = request.form["dob"]
        aadhar_value = request.form["aadhar"]
        phone_value = request.form["phone"]
        password1_value = request.form["password1"]

        check1 = ifPatientEmailRegistered(emailAddress_value)
        check2 = ifPatientAadharRegistered(aadhar_value)
        check = check1 and check2 

        if not check:
            patient_register(firstName_value, lastName_value, emailAddress_value, password1_value, gender_value, dob_value, aadhar_value, phone_value)
            pid = get_pid(emailAddress_value)
            patient_vaccination(pid, session['vid_value'], session['did'], session['slot_time'], session['slot_date'])
            vaccination_report(pid, session['did'], 'registered')
            return redirect(url_for('PatientLogin'))    
        else:
            if check1:
                flash('Email already registered. Please login or enter the correct email')
            if check2:
                flash('Aadhar already registered. Please login or enter the correct aadhar number')
            return render_template('patient-register.html')
    return render_template('patient-register.html')


@app.route("/patient-login/", methods=["POST", "GET"])
def PatientLogin():
    check = True
    if request.method == "POST":
        emailAddress_value = request.form["emailAddress"]
        session['p_email'] = emailAddress_value
        password_value = request.form["password"]
        check = ifPatientExist(emailAddress_value, password_value)

        if not check:
            flash('Login failed. Check your email and password', 'danger')
            return render_template('patient-login.html')
        else:
            return redirect(url_for('vaccinationReport'))
    return render_template('patient-login.html')

@app.route("/vaccination-report/",methods=["GET","POST"])
def vaccinationReport():
    msg = Message('CoVictory Vaccination Report', sender = 'developercovictory@gmail.com', recipients = [session['p_email']])
    pid = get_pid(session['p_email'])
    patient = get_patient_report_details(pid)
    dob = get_age(patient[4])
    did = get_did_from_pid(pid)
    doctor = get_doctor_report_details(did)
    vid = get_vid(session['p_email'])
    phno = get_doctor_phno(did)
    center = get_center_report_details(vid)
    date1 = get_date(pid)
    date2 = datetime.strptime(date1, "%Y-%m-%d")+timedelta(days=28)
    date2 = date2.date()
    status = get_status(pid)

    if request.method == "POST":
        messageBody = f"""
        Vaccination Report for {patient[0]} {patient[1]}
        Center Name: {center[1]}
        Doctor Name: {doctor[0]}
        City: {center[0]}
        Doctor's email: {doctor[1]}
        Doctor's phone number: {phno}

        Age: {dob}
        Gender: {patient[3]}
        Date of 1st Dose: {date1}
        Date of 2nd Dose: {date2}



        Sent to you by CoVictory Team
        """

        msg.body = messageBody
        mail.send(msg)

    return render_template('vaccination-report.html',status = status, patient = patient,center = center, doctor=doctor, date1 = date1, date2 = date2, dob = dob)


@app.route("/doctor-register/", methods=["POST", "GET"])
def DoctorRegister():
    if request.method == "POST":
        DID_value = request.form["DID"]
        VID_value = request.form["VID"]
        Dname_value = request.form["Dname"]
        emailAddress_value = request.form["emailAddress"]
        qualifications_value = request.form["qualifications"]
        phone_value = request.form["phone"]
        password1_value = request.form["password1"]

        check1 = ifDoctorEmailRegistered(emailAddress_value)
        check2 = ifDoctorIdRegistered(DID_value)
        check = check1 and check2
        if not check:
            doctor_register(DID_value, Dname_value, emailAddress_value, password1_value, phone_value, VID_value)
            did = get_did(emailAddress_value)
            qualifications = qualifications_value.split(',')
            for qualification in qualifications:
                doctor_qualification(did,qualification)
            return redirect(url_for('DoctorLogin'))
        else:
            if check1:
                flash('Email already registered. Please login or enter the correct email')
            if check2:
                flash('Doctor ID already registered. Please login or enter the correct Doctor Id')
            return render_template('doctor-register.html')
    return render_template('doctor-register.html')


@app.route("/doctor-login/", methods=["POST", "GET"])
def DoctorLogin():
    check = True
    if request.method == "POST":
        emailAddress_value = request.form["emailAddress"]
        password_value = request.form["password"]
        did = get_did(emailAddress_value)
        session['emailAddress'] = emailAddress_value
        session['did'] = did
        check = ifDoctorExists(emailAddress_value, password_value)

        if not check:
            flash('Login failed. Check your email and password', 'danger')
            return render_template('doctor-login.html')
        else:
            return redirect(url_for('DoctorHome'))
    return render_template('doctor-login.html')

@login_required
@app.route("/doctor-slot/", methods=["GET", "POST"])
def DoctorSlot():
    if request.method == 'POST':
       slot_date = request.form["slot_date"]
       slot_time = request.form["slot_time"]
       vid = get_vid(session['emailAddress'])
       check = ifSlotAssigned(vid, slot_date, slot_time)
       date = datetime.strptime(slot_date, "%Y-%m-%d")+timedelta(days=28) 
       if not check:
           AssignSlot(vid, slot_date, slot_time, session['did'])
           #AssignSlot(vid, date.date(),slot_time, session['did'])
           return render_template('doctor-slot.html')
       else:
            flash('This slot is already assigned to other doctor. Please select a different slot.')
            return render_template('doctor-slot.html')
    return render_template('doctor-slot.html')


#@login_required
#@app.route

@login_required
@app.route("/patient-list/",methods=["GET","POST"])
def PatientList():
    patients = get_patients(session['did'])
    if request.method == 'POST':
        session['pid'] = request.form['pid']
        pid = session['pid']
        patient = get_patient_report_details(pid)
        dob = get_age(patient[4])
        did = get_did_from_pid(pid)
        doctor = get_doctor_report_details(did)
        vid = get_vid(session['p_email'])
        phno = get_doctor_phno(did)
        center = get_center_report_details(vid)
        date1 = get_date(pid)
        date2 = datetime.strptime(date1, "%Y-%m-%d")+timedelta(days=28)
        date2 = date2.date()
        status = get_status(pid)
        return render_template('patient-data.html',status = status, patient = patient,center = center, doctor=doctor, date1 = date1, date2 = date2, dob = dob)
    return render_template('patient-list.html', patients = patients)

@app.route('/patient-data/', methods=["GET", "POST"])
def patientData():
    pid = session['pid']
    patient = get_patient_report_details(pid)
    dob = get_age(patient[4])
    did = get_did_from_pid(pid)
    doctor = get_doctor_report_details(did)
    vid = get_vid(session['p_email'])
    phno = get_doctor_phno(did)
    center = get_center_report_details(vid)
    date1 = get_date(pid)
    date2 = datetime.strptime(date1, "%Y-%m-%d")+timedelta(days=28)
    date2 = date2.date()
    status = get_status(pid)
    if request.method == "POST":
        status = request.form['status']
        remarks = request.form['remarks']
        pid = session['pid']
        update_report(int(pid), status, remarks)
        return render_template('patient-data.html',remark = status[1], status = status[0], patient = patient,center = center, doctor=doctor, date1 = date1, date2 = date2, dob = dob)
    return render_template('patient-data.html',remark = status[1], status = status[0], patient = patient,center = center, doctor=doctor, date1 = date1, date2 = date2, dob = dob)



@login_required
@app.route("/patient-logout/",methods=["GET","POST"])
def PatientLogout():
    logout_user()
    return redirect(url_for('PatientLogin'))

@login_required
@app.route("/doctor-logout/",methods=["GET","POST"])
def DoctorLogout():
    logout_user()
    return redirect(url_for('DoctorLogin'))

@login_required
@app.route("/admin-logout/",methods=["GET","POST"])
def AdminLogout():
    logout_user()
    return redirect(url_for('adminLogin'))

@app.route("/vaccination-center-details/", methods=["GET","POST"])
def vaccintionCenterDetails():
    centers = get_centers()
    return render_template('vaccination-center-details.html',centers=centers)

@app.route("/patient-details",methods=["GET","POST"])
def patientDetails():
    patients = get_patient_details()
    return render_template('patient-details.html',patients=patients)

@app.route("/doctor-details", methods=["GET","POST"])
def doctorDetails():
    doctors = get_doctor_details()
    all_did = get_did_for_all_doctors()
    total_doctors = get_total_doctors()
    qualifications = [[total_doctors]]
    qualifications = get_qualification(all_did, qualifications, total_doctors)
    # print(qualifications)
    x = len(doctors)
    return render_template('doctor-details.html',doctors=doctors, qualifications=qualifications,x=x)


@app.route("/statistics/",methods=["GET", "POST"])
def statistics():
    males = get_males()
    females = get_females()
    vid_covishield = get_vid_for_vaccine('Covishield')
    covishield_count = get_patients_of_each_vaccine(vid_covishield, 0)
    vid_covaxin = get_vid_for_vaccine('Covaxin')
    covaxin_count = get_patients_of_each_vaccine(vid_covaxin, 0)
    vid_comirnaty = get_vid_for_vaccine('Comirnaty')
    comirnaty_count = get_patients_of_each_vaccine(vid_comirnaty, 0)
    registered_count = get_status_count('registered')
    phase1_count = get_status_count('phase 1')
    vaccinated_count = get_status_count('vaccinated')
    age60 = 0
    age30 = 0
    age40 = 0
    age50 = 0
    age70 = 0
    age80 = 0
    dob = get_dob()

    for d in dob:
        age = get_age(d[0])
        print(age)
        if age >= 30 and age < 40:
            age30 = age30 + 1
        elif age >=40 and age < 50:
            age40 = age40 + 1
        elif age >= 50 and age < 60:
            age50 = age50 + 1
        elif age >= 60 and age < 70:
            age60 = age60 + 1
        elif age >= 70 and age < 80:
            age70 = age70 + 1
        elif age >= 80 and age < 90:
            age80 = age80 + 1
        print(age60)
    return render_template('statistics.html', registered = registered_count, phase1 = phase1_count, vaccinated = vaccinated_count, males= males, females=females, covishield= covishield_count, covaxin=covaxin_count, comirnaty=comirnaty_count, age30 = age30, age40 = age40, age50 = age50, age60 = age60, age70 = age70, age80 = age80)



if __name__ == "__main__":
    app.run(debug=True)