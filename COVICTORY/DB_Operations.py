import pymysql


#database connection
connection = pymysql.connect(host="localhost", 
                            user="root", 
                            passwd="123456**oK", 
                            database="COVICTORY")
cursor = connection.cursor()


#fetching and showing data from db
def get_data():
    cursor.execute("SELECT * FROM PATIENT")
    rows = cursor.fetchall()    
    return rows


#inserting data to db
def patient_register(firstName_value, lastName_value, emailAddress_value, password1_value, gender_value, dob_value, aadhar_value, phone_value):
    cursor.execute("INSERT INTO PATIENT(pid,fname,lname,p_email,p_pwd,gender,dob,aadhar_id,p_phone) VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s)",(firstName_value, lastName_value, emailAddress_value, password1_value, gender_value, dob_value, aadhar_value, phone_value))
    connection.commit()
    return 1


def ifPatientExist(emailAddress_value, password_value):
    cursor.execute("SELECT * FROM PATIENT WHERE p_email = %s AND p_pwd = %s", (emailAddress_value, password_value))
    account = cursor.fetchone()
    return account


def doctor_register(DID_value, Dname_value, emailAddress_value, password1_value, phone_value):
    cursor.execute("INSERT INTO DOCTOR(did, dname, d_email, d_pwd, d_phone) VALUES (%s,%s,%s,%s,%s)", (DID_value, Dname_value, emailAddress_value, password1_value, phone_value)) 
    connection.commit()
    return 1


def ifDoctorExists(emailAddress_value, password1_value):
    cursor.execute("SELECT * FROM DOCTOR WHERE d_email = %s AND d_pwd = %s", (emailAddress_value, password1_value))
    account = cursor.fetchone()
    return account