from flask import Flask, request, render_template, redirect, url_for, flash, session
from email_validator import validate_email
from DB_Operations import *
import re
from flask_login import login_required, logout_user, login_user, login_manager, LoginManager
from datetime import datetime, timedelta, date

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return user_id



@app.route("/")
def home():
    centers = get_total_centers()
    doctors = get_total_doctors()
    patients = get_total_patients()
    return render_template('home.html', centers = centers, doctors= doctors, patients = patients)


@app.route("/admin", methods=["GET","POST"])
def admin():
    return render_template('admin.html')


@login_required
@app.route("/doctor-home/",methods=["GET", "POST"])
def DoctorHome():
    did = session['did']
    name = get_doctor_name(did)
    return render_template('doctor-home.html', name = name)


@app.route("/vaccination-center/", methods=["GET", "POST"])
def VaccinationCenter():
    centers = get_centers()
    if request.method == 'POST':
        session['vid_value'] = request.form["vid"]
        return redirect(url_for('Slot'))
    return render_template('vaccination-center.html', centers = centers)


@app.route("/slot/", methods=["GET","POST"])
def Slot():
    slots = get_slots(session['vid_value'])
    dropdown_slots = get_dropdown_slots(session['vid_value'])
    if request.method == "POST":
        slot_value = request.form["slot"]
        slots = slot_value.split(',')     
        session['slot_date'] = slots[0]
        session['slot_time'] = slots[1]
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
        password2_value = request.form["password2"]

        check1 = ifPatientEmailRegistered(emailAddress_value)
        check2 = ifPatientAadharRegistered(aadhar_value)
        check = check1 and check2 

        if not check:
            patient_register(firstName_value, lastName_value, emailAddress_value, password1_value, gender_value, dob_value, aadhar_value, phone_value)
            pid = get_pid(emailAddress_value)
            did = get_slot_did(session['vid_value'], session['slot_date'], session['slot_time'])
            patient_vaccination(pid, session['vid_value'], did, session['slot_date'], session['slot_time'])
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
        password_value = request.form["password"]
        check = ifPatientExist(emailAddress_value, password_value)

        if not check:
            flash('Login failed. Check your email and password', 'danger')
            return render_template('patient-login.html')
        else:
            return "Vaccination Report"
    return render_template('patient-login.html')


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
           AssignSlot(vid, date.date(),slot_time, session['did'])
           return render_template('doctor-slot.html')
       else:
            flash('This slot is already assigned to other doctor. Please select a different slot.', 'error')
            return render_template('doctor-slot.html') 
    return render_template('doctor-slot.html')


@login_required
@app.route("/patient-list/",methods=["GET","POST"])
def PatientList():
    patients = get_patients(session['did'])
    if request.method == 'POST':
        query = request.form['search']
        data = patient_list_search_bar(query)
        return render_template('patient-list.html', patients = data)
    return render_template('patient-list.html', patients = patients)


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
    # qualifications = [[total_doctors]]
    # qualifications = get_qualification(all_did, qualifications, total_doctors)
    return render_template('doctor-details.html',doctors=doctors)


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
    # dob = get_dob()
    age60 = 0
    age30 = 0
    age40 = 0
    age50 = 0
    age70 = 0
    age80 = 0
    # for dob in dob:
    #     dob = datetime.strptime(dob, '%Y-%m-%d')
    #     dob = dob.date()
    #     today = date.today()
    #     age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    #     if age >= 30 and age < 40:
    #         age30 = age30 + 1
    #     elif age >=40 and age < 50:
    #         age40 = age40 + 1
    #     elif age >= 50 and age < 60:
    #         age50 = age50 + 1
    #     elif age >= 60 and age < 70:
    #         age60 = age60 + 1
    #     elif age >= 70 and age < 80:
    #         age70 = age70 + 1
    #     elif age >= 80 and age < 90:
    #         age80 = age80 + 1

    

    print(age60) 
    print(age50)
    print(age70)
    return render_template('statistics.html', males= males, females=females, covishield= covishield_count, covaxin=covaxin_count, comirnaty=comirnaty_count)

if __name__ == "__main__":
    app.run(debug=True)