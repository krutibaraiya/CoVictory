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

def get_patients(did):
    cursor.execute("SELECT pid, s_date, s_time FROM VACCINATION WHERE did = %s",(did))
    patients = cursor.fetchall()
    return patients


def get_slots(vid):
    cursor.execute("SELECT vid,s_date,s_time FROM SLOT WHERE vid = %s",(vid))
    slots = cursor.fetchall()
    return slots


def get_dropdown_slots(vid):
    cursor.execute("SELECT SLOT.vid, SLOT.s_time, SLOT.s_date, VACCINATION.vid, VACCINATION.s_time, VACCINATION.s_date, VACCINATION.pid FROM SLOT LEFT JOIN VACCINATION USING (vid,s_date,s_time) WHERE pid IS NULL")
    slots = cursor.fetchall()
    return slots

def get_assigned_slots(vid, slot_date):
    cursor.execute("SELECT s_time FROM SLOT WHERE vid = %s AND s_date = %s", (vid, slot_date))
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

def get_males():
    cursor.execute("SELECT count(*) from PATIENT WHERE gender='Male'")
    males =  [v for v in cursor.fetchone()][0]
    return males

def get_females():
    cursor.execute("SELECT count(*) from PATIENT WHERE gender='Female'")
    females = [v for v in cursor.fetchone()][0]
    return females

def patient_list_search_bar(query):
    cursor.execute("SELECT pid, s_date, s_time FROM VACCINATION WHERE pid = %s OR s_date = %s OR s_time = %s",(query,query,query))
    patients = cursor.fetchall()
    return patients

def vaccination_center_search_bar(query):
    cursor.execute("SELECT vid,vname,vloc,vac_name FROM VACCINATION_CENTER WHERE vid = %s OR vname = %s OR vloc = %s OR vac_name = %s",(query,query,query,query))
    centers = cursor.fetchall()
    return centers

def doctor_search_bar(query):
    cursor.execute("SELECT did, dname, d_email, d_phone FROM DOCTOR WHERE did=%s OR dname = %s OR d_email = %s OR d_phone=%s",(query,query,query,query))
    doctors = cursor.fetchall()
    return doctors

def get_vid_for_vaccine(vaccine):
    cursor.execute("SELECT vid FROM VACCINATION_CENTER WHERE vac_name = %s",(vaccine))
    centers = cursor.fetchall()
    return centers


def get_patients_of_each_centers(centers, sum):
    for center in centers:
        cursor.execute("SELECT COUNT(*) FROM VACCINATION WHERE vid = %s", (center))
        count = [v for v in cursor.fetchone()][0]
        sum = sum + count
    return sum


def get_status(status):
    cursor.execute("SELECT COUNT(*) FROM VACCINATION_REPORT WHERE status = %s",(status))
    status = [v for v in cursor.fetchone()][0]
    return status

def get_total_centers():
    cursor.execute("SELECT COUNT(*) FROM VACCINATION_CENTER")
    centers = [v for v in cursor.fetchone()][0]
    return centers

def get_total_doctors():
    cursor.execute("SELECT COUNT(*) FROM DOCTOR")
    doctors = [v for v in cursor.fetchone()][0]
    return doctors

def get_total_patients():
    cursor.execute("SELECT COUNT(*) FROM PATIENT")
    patients = [v for v in cursor.fetchone()][0]
    return patients

def get_doctor_name(did):
    cursor.execute("SELECT dname FROM DOCTOR WHERE did = %s",(did))
    name = cursor.fetchone()
    return name