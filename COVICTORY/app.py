from flask import Flask, request, render_template, redirect, url_for, flash
from DB_Operations import *
app = Flask(__name__)

# @app.route("/")
# def helloworld():
#     return render_template('patient_reg.html', text="Working")

@app.route("/home")
def helloworld():
    all_text = get_data()
    return render_template('patient-register.html', all_text = all_text)

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
        check = ifPatientExist(emailAddress_value, password1_value)
        if not check:
            register = patient_register(firstName_value, lastName_value, emailAddress_value, password1_value, gender_value, dob_value, aadhar_value, phone_value)    
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
        Dname_value = request.form["Dname"]
        emailAddress_value = request.form["emailAddress"]
        phone_value = request.form["phone"]
        password1_value = request.form["password1"]

        check = ifDoctorExists(emailAddress_value, password1_value)
        if not check:
            register = doctor_register(DID_value, Dname_value, emailAddress_value, password1_value, phone_value)
            return redirect(url_for('doctor-login'))
    return render_template('doctor-register.html')    


@app.route("/doctor-login/", methods=["POST", "GET"])
def DoctorLogin():
    if request.method == "POST":
        emailAddress_value = request.form["emailAddress"]
        password_value = request.form["password"]

        check = ifDoctorExists(emailAddress_value, password_value)

        if not check:
            flash('Login failed. Check your email and password', 'danger')
            return render_template('patient-login.html')
        else:
            return "Paient List"
    return render_template('patient-login.html')

if __name__ == "__main__":
    app.run(debug=True)


        
        

        

        

       
        