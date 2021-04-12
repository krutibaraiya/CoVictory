from flask import Flask, request, render_template, redirect, url_for, flash, session
from email_validator import validate_email
from DB_Operations import *
import re
from flask_login import login_required, logout_user
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


@app.route("/")
def home():
    males = get_males()
    females = get_females()
    return render_template('home.html',males=males, females=females)

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
    if request.method == "POST":
        slot_value = request.form["slot"]
        slots = slot_value.split(',')
        session['slot_date'] = slots[0]
        session['slot_time'] = slots[1]
        return redirect(url_for('PatientRegister'))
    return render_template('slot.html', slots = slots)


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

        valid = validate_email(emailAddress_value)
        if not valid:
            flash(u'Enter a valid email address', 'error')
        
        aadhar_valid = re.search("[0-9]{12}", aadhar_value)
        if not aadhar_valid:
            flash(u'Enter a 12 digit aadhar number', 'error')
        
        phone_valid = re.search("[0-9]{10}", phone_value)
        if not phone_valid:
            flash(u'Enter a 10 digit phone number', 'error')
        
        if password1_value != password2_value:
            flash(u'Password and Re-enter password field should match','error')


        check = ifPatientRegistered(emailAddress_value)
        if not check:
            patient_register(firstName_value, lastName_value, emailAddress_value, password1_value, gender_value, dob_value, aadhar_value, phone_value)
            pid = get_pid(emailAddress_value)
            did = get_slot_did(session['vid_value'], session['slot_date'], session['slot_time'])
            patient_vaccination(pid, session['vid_value'], did, session['slot_date'], session['slot_time'])
            return redirect(url_for('PatientLogin'))    
        else:
            return render_template('patient-register.html')
    return render_template('patient-register.html')


@app.route("/patient-login/", methods=["POST", "GET"])
def PatientLogin():
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

        check = ifDoctorRegistered(emailAddress_value)
        if not check:
            doctor_register(DID_value, Dname_value, emailAddress_value, password1_value, phone_value, VID_value)
            did = get_did(emailAddress_value)
            qualifications = qualifications_value.split(',')
            for qualification in qualifications:
                doctor_qualification(did,qualification)
            return redirect(url_for('DoctorLogin'))
    return render_template('doctor-register.html')    


@app.route("/doctor-login/", methods=["POST", "GET"])
def DoctorLogin():
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
            return redirect(url_for('PatientList'))
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

if __name__ == "__main__":
    app.run(debug=True)


        
        

        

        

       
        