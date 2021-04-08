import pymysql


#database connection
connection = pymysql.connect(host="localhost", 
                            user="root", 
                            passwd="123456**oK", 
                            database="COVICTORY")
cursor = connection.cursor()



def get_centers():
    cursor.execute("SELECT * FROM VACCINATION_CENTER")
    centers = cursor.fetchall()    
    return centers


def get_slots(vid):
    cursor.execute("SELECT vid,s_date,s_time FROM SLOT WHERE vid = %s",(vid))
    slots = cursor.fetchall()
    return slots

def get_vid(emailAddress_value):
    cursor.execute("SELECT vid FROM DOCTOR WHERE d_email = %s",(emailAddress_value))
    vid = cursor.fetchone()
    return vid


def get_did(emailAddress_value):
    cursor.execute("SELECT did FROM DOCTOR WHERE d_email = %s",(emailAddress_value))
    did = cursor.fetchone()
    return did


def get_pid(emailAddress_value):
    cursor.execute("SELECT pid FROM PATIENT WHERE p_email = %s", (emailAddress_value))
    pid = cursor.fetchone()
    return pid

def get_slot_did(vid, slot_date, slot_time):
    cursor.execute("SELECT did FROM SLOT WHERE vid = %s AND s_date = %s AND s_time = %s", (vid, slot_date, slot_time))
    did = cursor.fetchone()
    return did


def ifSlotAssigned(vid, slot_date, slot_time):
    cursor.execute("SELECT * FROM SLOT where vid = %s AND s_date = %s AND s_time = %s",(vid, slot_date, slot_time))
    slot = cursor.fetchone()
    return slot


def patient_register(firstName_value, lastName_value, emailAddress_value, password1_value, gender_value, dob_value, aadhar_value, phone_value):
    cursor.execute("INSERT INTO PATIENT(pid,fname,lname,p_email,p_pwd,gender,dob,aadhar_id,p_phone) VALUES (DEFAULT, %s, %s, %s, %s, %s, %s, %s, %s)",(firstName_value, lastName_value, emailAddress_value, password1_value, gender_value, dob_value, aadhar_value, phone_value))
    connection.commit()
    return 1

def ifPatientRegistered(emailAddress_value):
    cursor.execute("SELECT * FROM PATIENT WHERE p_email = %s", (emailAddress_value))
    account = cursor.fetchone()
    return account

def ifPatientExist(emailAddress_value, password_value):
    cursor.execute("SELECT * FROM PATIENT WHERE p_email = %s AND p_pwd = %s", (emailAddress_value, password_value))
    account = cursor.fetchone()
    return account


def doctor_register(DID_value, Dname_value, emailAddress_value, password1_value, phone_value, VID_value):
    cursor.execute("INSERT INTO DOCTOR(did, dname, d_email, d_pwd, d_phone, vid) VALUES (%s,%s,%s,%s,%s,%s)", (DID_value, Dname_value, emailAddress_value, password1_value, phone_value, VID_value)) 
    connection.commit()
    return 1

def ifDoctorRegistered(emailAddress_value):
    cursor.execute("SELECT * FROM DOCTOR WHERE d_email = %s", (emailAddress_value))
    account = cursor.fetchone()
    return account

def ifDoctorExists(emailAddress_value, password1_value):
    cursor.execute("SELECT * FROM DOCTOR WHERE d_email = %s AND d_pwd = %s", (emailAddress_value, password1_value))
    account = cursor.fetchone()
    return account


def AssignSlot(vid, slot_date, slot_time, did):
    cursor.execute("INSERT INTO SLOT(vid, s_date, s_time, did) VALUES (%s, %s, %s, %s)", (vid, slot_date, slot_time, did))
    connection.commit()
    return 1


def patient_vaccination(pid, vid, did, slot_date, slot_time):
    cursor.execute("INSERT INTO VACCINATION(pid,vid,did,s_time,s_date) VALUES (%s, %s, %s, %s, %s)",(pid,vid,did,slot_time,slot_date))
    connection.commit()
    return 1

def doctor_qualification(did, qualification):
    cursor.execute("INSERT INTO QUALIFICATION(did, qualification) VALUES (%s, %s)",(did, qualification))
    connection.commit()
    return 1