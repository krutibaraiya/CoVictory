from flask import Flask, render_template, url_for, redirect, request, session
from flask_mysqldb import MySQL
from forms import RegistrationForm, LoginForm
import pymysql.cursors

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123456**oK',
                             db='CoVictory',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

@app.route("/")
def Home():
	return "<h1>Home Page</h1>"

@app.route("/login/", methods = ['GET','POST'])
def PatientLogin():
	form = LoginForm()
	if form.validate_on_submit():
		email = request.form['email']
		password = request.form['password']
		with connection.cursor() as cursor:
			cursor.execute('SELECT * FROM PatientAccount WHERE email = %s AND password = %s', (email,password))
			account = cursor.fetchone()
			cursor.close()
			connection.close()

		if account:
		       return "Vaccine Registeration"
		
	return render_template('login.html',title='Login',form=form)
  	
	




@app.route("/register/", methods = ['GET','POST'])
def PatientRegister():
	form = RegistrationForm()
	if form.validate_on_submit():
		email = request.form['email']
		password = request.form['password']
		cursor = connection.cursor()
		cursor.execute('SELECT * FROM PatientAccount WHERE email = %s', (email))
		account = cursor.fetchone()
		cursor.close()
			
	# with connection.cursor() as cursor:
	# 	cursor.execute('SELECT * FROM PatientAccount WHERE email = %s', (email))
	# 	account = cursor.fetchone()
		if not account:
			cursor = connection.cursor()
			cursor.execute('INSERT INTO PatientAccount VALUES (%s, %s)', (email,password))
			connection.commit()				
			cursor.close()
			connection.close()
			msg = 'You have registered successfully!'
		return "Registeration Done"
	
	return render_template('register.html', title='Register', form=form)



if __name__ == '__main__':
	app.run(debug = True)