#!/usr/bin/env python
# coding:utf-8

import urllib
import json
from flask import *
import json,requests,sys
import apiai
import sqlite3
import datetime
import os
import mysql.connector
import webbrowser
from tabulate import tabulate
new=2

app = Flask(__name__)

CLIENT_ACCESS_TOKEN = '27f2781372f64d5191947020e6930446'

ai= apiai.ApiAI(CLIENT_ACCESS_TOKEN)

conn = mysql.connector.connect(user='root',password='newrootpassword',
							   host='127.0.0.1',database='ita'
							   )
c = conn.cursor()

@app.route('/')
def main():
	return render_template('main.html')
@app.route('/home')
def index():
    return render_template('console.html')


@app.route('/webhook',methods=["POST"])
def webhook():
	req = request.get_json(silent=True, force=True)
	#print "Request:"
	#print json.dumps(req, indent=4)
	res = makeWebhookResult(req)
	res = json.dumps(res, indent=4)
	#print res
	r = make_response(res)
	r.headers['Content-Type'] = 'application/json'
	return r


def makeWebhookResult(req):
	#if req.get("result").get("action")!="interest":
	#	return {}
	stri = req.get("result")
	if stri.get("action")=="interest":
		result = req.get("result")
		parameters = result.get("parameters")
		zone = parameters.get("bank-name")
		bank = {'Federal bank': '6.4%', 'Andhra bank': '10.56'}
		speech = "the intrest rate of " + zone + " " +str(bank[zone])
		print("Response:")
		print(speech)
		return {
			"speech" : speech,
			"displayText": speech,
			"source": "NITK_Management"
		}
	if stri.get("action")=="places":
		parameters = stri.get("parameters")
		location = str(parameters.get("locations"))
		print(location)
		location=location.lower()
		dictionary = {"mangalore" : 1, "panaji" : 2, "jaipur" : 3, "salem" : 4, "vijayawada" : 5}		
		if location in dictionary.keys():
			hid = dictionary[location.lower()]
			print(hid)
			#conn = sqlite3.connect('hospital1.db')
			#cursor = c.execute("SELECT HLOCATION, HPHONE FROM HOSPITAL WHERE HID = " + str(hid))
			#data = cursor.fetchone()
			sql="SELECT HLOCATION,HPHONE from HOSPITAL where HID=%s"
			c.execute(sql,(hid,))
			data=c.fetchall()
			print(data[0][0])
			print(data[0][1])
			speech = "Hospital is located at: " + str(data[0][0]) + "\nContact Details: " + str(data[0][1])
		else:
			speech = "There is no hospital in the given location."
		print("Response:")
		print(speech)
		return {
			"speech" : speech,
			"displayText": speech,
			"source": "NITK_Management"
		}
	if stri.get("action")=="medicine.availability":
		#conn = sqlite3.connect('hospital1.db')
		parameters = stri.get("parameters")
		medicine = str(parameters.get("M_name"))
		print(medicine)
		#cursor = c.execute("SELECT MAVAIL FROM MEDICINE WHERE MNAME = \"" + medicine + "\"")
		#data = cursor.fetchone()
		sql="SELECT MAVAIL from MEDICINE where MNAME=%s"
		c.execute(sql,(medicine,))
		data=c.fetchall()
		if int(data[0][0]) == 1:
			speech = "The requested medicine is available."
		else:
			speech = "The requested medicine is currently unavailable."
		print("Response:")
		print(speech)
		return {
			"speech" : speech,
			"displayText": speech,
			"source": "NITK_Management"
		}
	if stri.get("action")=="doctor.speciality":
		#conn = sqlite3.connect('hospital1.db')
		parameters = stri.get("parameters")
		location = str(parameters.get("locations")).lower()
		dictionary = {"mangalore" : 1, "panaji" : 2, "jaipur" : 3, "salem" : 4, "vijayawada" : 5}
		if location.lower() in dictionary.keys():
			hid = dictionary[location.lower()]
			speciality = str(parameters.get("Doc_type"))
			#cursor = c.execute("SELECT DID, DNAME, DFEE FROM DOCTOR WHERE HID = " + str(hid) + " AND DSPECIAL = \"" + speciality + "\"")
			#data = cursor.fetchall()
			sql="SELECT DID,DNAME,DFEE from DOCTOR where HID=%s and DSPECIAL=%s"
			c.execute(sql,(hid,speciality,))
			data=c.fetchall()
			print(data)
			if len(data) == 0:
				speech = "No doctors available for the given input."
			else: 
				speech = ""
				for did, name, fee in data:
					speech = speech + str(did) + "\t" + name + "\t" + str(fee)
					print(speech)
					#cursor = conn.execute("SELECT WEEKDAY, TIME FROM AVAILABLE WHERE DID = " + str(did))
					#output = cursor.fetchall()
					sql="SELECT WEEKDAY,TIME from AVAILABLE where DID=%s"
					c.execute(sql,(str(did),))
					data=c.fetchall()
					speech = speech + ". The doctor is available on "
					print(data)
					for i in range(len(data)):
						speech = speech + data[i][0] + " on " + data[i][1] + ", "
					speech = speech + "."

		else:
			speech = "No doctors available for the given location."
		print("Response:")
		print(speech)
		return {
			"speech" : speech,
			"displayText": speech,
			"source": "NITK_Management"
		}
	
	if stri.get("action")=="medicine.info":
		#conn = sqlite3.connect('hospital1.db')
		parameters = stri.get("parameters")
		medicine = str(parameters.get("medicines"))
		#cursor = c.execute("SELECT MDOSAGE, MPRICE FROM MEDICINE WHERE MNAME = \"" + medicine+"\"")
		#data = cursor.fetchone()
		sql="SELECT MDOSAGE, MPRICE FROM MEDICINE WHERE MNAME=%s"
		c.execute(sql,(medicine,))
		data=c.fetchall()
		print(data)
		if len(data) == 0:
			speech = "The requested medicine is not present in the records."
		else:
			speech = medicine + " is to be taken " + str(data[0][0]) + " and costs Rs. " + str(data[0][1]) + "."
		print("Response:")
		print(speech)
		return {
			"speech" : speech,
			"displayText": speech,
			"source": "NITK_Management"
		}
	
	if stri.get("action")=="symptom":
		#conn = sqlite3.connect('hospital1.db')
		parameters = stri.get("parameters")
		symptom = str(parameters.get("symptoms"))
		print(symptom)
		#cursor = c.execute("SELECT MNAME, MDOSAGE, MPRICE FROM MEDICINE WHERE MID = (SELECT SMED FROM SYMPTOMS WHERE SNAME = \"" + symptom.lower() + "\" LIMIT 1)")
		#data = cursor.fetchone()
		sql="SELECT MNAME, MDOSAGE, MPRICE FROM MEDICINE WHERE MID = (SELECT SMED FROM SYMPTOMS WHERE SNAME =%s limit 1)"
		c.execute(sql,(symptom,))
		data=c.fetchall()
		print(data)
		if len(data) == 0:
			speech = "Sorry but I am unable to help you with this health problem. Consider consulting an appropriate doctor."
		else:
			speech = "Please take " + str(data[0][0]) + " " + str(data[0][1]).lower() + ". The medicine will cost Rs. " + str(data[0][2]) + "."
		print("Response:")
		print(speech)
		return {
			"speech" : speech,
			"displayText": speech,
			"source": "NITK_Management"
		}
	
	if stri.get("action")=="Register.new":
		#conn = sqlite3.connect('hospital1.db')
		parameters = stri.get("parameters")
		name = str(parameters.get("name"))
		age = str(parameters.get("age"))
		sex = str(parameters.get("sex"))
		#cursor = c.execute("SELECT PID FROM PATIENT WHERE PNAME = \"" + name + "\" AND PAGE = " + age + " AND PSEX = \"" + sex + "\"")
		#data = cursor.fetchall()
		sql="SELECT PID FROM PATIENT WHERE PNAME =%s and PAGE=%s and PSEX=%s"
		c.execute(sql,(name,age,sex,))
		data=c.fetchall()
		print(data)
		if len(data) == 0:
			#cursor = conn.execute("INSERT INTO PATIENT (PNAME, PAGE, PSEX) VALUES (\'" + name + "\', " + age + ", \'" + sex + "\')")
			#cursor = conn.execute("SELECT PID FROM PATIENT WHERE PNAME = \"" + name + "\" AND PAGE = " + age + " AND PSEX = \"" + sex + "\"")
			#data = cursor.fetchone()
			c.execute("""INSERT INTO PATIENT (PNAME, PAGE, PSEX) VALUES (%s,%s,%s)""",(name,age,sex))
			sql="SELECT PID FROM PATIENT WHERE PNAME=%s and PAGE=%s and PSEX=%s"
			c.execute(sql,(name,age,sex,))
			data=c.fetchall()
			speech = "New patient profile created. Your patient id is: " + str(data[0][0]) + "."
		else: 
			speech = "Profile already exists. Your patient id is: " + str(data[0][0]) + "."
		print("Response:")
		print(speech)
		conn.commit()
		return {
			"speech" : speech,
			"displayText": speech,
			"source": "NITK_Management"
		}
	
	if stri.get('action')=="appointment.book":
		#conn = sqlite3.connect('hospital1.db')
		parameters = stri.get("parameters")
		pid = str(parameters.get("pid"))
		time = str(parameters.get("time"))
		date = str(parameters.get("date"))
		did = str(parameters.get("did"))
		purpose = str(parameters.get("purpose"))
		location = str(parameters.get("location")).lower()
		dictionary = {"mangalore" : 1, "panaji" : 2, "jaipur" : 3, "salem" : 4, "vijayawada" : 5}
		if location in dictionary.keys():
			hid = str(dictionary[location.lower()])
			#cursor = c.execute("SELECT * FROM DOCTOR WHERE DID = " + did + " AND HID = " + hid)
			#data = cursor.fetchall()
			sql="SELECT * FROM DOCTOR WHERE DID =%s and HID=%s"
			c.execute(sql,(did,hid,))
			data=c.fetchall()
			if len(data) != 0:
				#cursor = conn.execute("SELECT * FROM PATIENT WHERE PID = " + pid)
				#data = cursor.fetchall()
				sql="SELECT * FROM PATIENT WHERE PID =%s"
				c.execute(sql,(pid,))
				data=c.fetchall()
				if len(data) != 0:
					DateTime = date + "-" + time
					print(DateTime)
					#cursor = conn.execute("SELECT PID FROM APPOINTMENT WHERE DID = " + did + " AND ADATETIME = \"" + DateTime + "\" AND HID = " + hid)
					#data = cursor.fetchone()
					sql="SELECT * FROM APPOINTMENT where DID=%s and ADATETIME=%s and HID=%s"
					c.execute(sql,(did,DateTime,hid,))
					data=c.fetchall()
					if len(data) != 0:
						if pid in data:
							speech = "Your appointment is already booked for the given time and doctor."
						else:
							speech = "The requested doctor already has appointment in the given time. Please book for another time."
					
					else:
						m = datetime.datetime.strptime(date,'%Y-%m-%d').strftime('%A')
						print(m)
						#cursor = conn.execute("SELECT TIME FROM AVAILABLE WHERE WEEKDAY = \""+m+"\"")
						sql="SELECT TIME FROM AVAILABLE WHERE WEEKDAY =%s and DID=%s"
						c.execute(sql,(m,did,))
						data=c.fetchall()
						print('Time available ---')
						print(data)
						if len(data)== 0:
							speech = "The requested doctor is unavailable at the requested time. Please book for another time."
						else:
							time_variable = data[0][0]
							time_variable= str(time_variable)				
							time1, time2 = time_variable.split("-")
							time1=str(time1)
							timeA = datetime.datetime.strptime(time1, "%H:%M:%S")
							timeB = datetime.datetime.strptime(time2, "%H:%M:%S")
							timeC = datetime.datetime.strptime(time, "%H:%M:%S")
						if timeC >timeA and timeC < timeB:
							#cursor = conn.execute("INSERT INTO APPOINTMENT(PID, DID, HID, PURPOSE, ADATETIME, AFEE) VALUES(" + pid + ", " + did + ", " + hid + ", \"" + purpose + "\", \"" + DateTime + "\", 0)")
							c.execute("""INSERT INTO APPOINTMENT(PID, DID, HID, PURPOSE, ADATETIME) VALUES(%s,%s,%s,%s,%s)""",(pid,did,hid,purpose,DateTime))
							speech = "Your appointment is booked at "+ time +" on "+ date
						else:
							speech = "The requested doctor is unavailable at the requested time. Please book for another time."
				else:
					speech="The patient does not exist in the records. Please try again or register before booking an appointment."
			else:
				speech = "The doctor does not exist in the records and/or the doctor does not work in the given hospital. Please try again."
		else:
			speech = "The location does not exist in the records. Please try again."			
		print("Response:")
		print(speech)
		conn.commit()
		return {
			"speech" : speech,
			"displayText": speech,
			"source": "NITK_Management"
		}
	
	if stri.get("action")=="restaurant.menu":
		parameters = stri.get("parameters")
		webbrowser.open("file:///C:/Users/user/Desktop/ITA%20project/web/standard.html",new=new)
	 	#speech = "OK RESPONSE ARRIVED"
		speech_resp="Did you check out the menu? Now please order"
		print("Response:")
		print(speech_resp)
		return {
			"speech" : speech_resp,
			"displayText": speech_resp ,
			"source": "NITK_Management"
		}
	
	if stri.get("action")=="order.item":
		parameters = stri.get("parameters")
		quantity = str(parameters.get("number"))
		hostel = str(parameters.get("hostel_block"))
		food = str(parameters.get("food-product"))
		name = str(parameters.get("name"))
		phone = int(parameters.get("phone"))
		print(name)
		print(phone)
		quantity = quantity.replace("[","")
		quantity = quantity.replace("]","")
		quantity = quantity.replace(",","")
		quantity = quantity.split(" ")
		for i in range(len(quantity)):
			quantity[i] = int(quantity[i])
		food=str(food)
		
		food = food.replace("u'","")
		food = food.replace("[","")
		food = food.replace("]","")
		food = food.replace(",","")
		#food = food.replace("'","")
		food = food.split("'")
		food = food[:-1]
		for i in range(len(food)):
			if i!=0 :
				food[i]=food[i][1:]		
		price=[]
		sql="SELECT Price from mainorder where Dish=%s"
		for i in food:
			c.execute(sql,(i,))
			data = c.fetchall()
			print(data)
			price.append(data[0][0])
		bill_amt=0
		for i in range(len(price)):
			bill_amt+=quantity[i]*price[i]
		print(bill_amt)
		#sql= """INSERT INTO orderitem (order_amount,Name,phone) values (%s,%s,%s)"""
		c.execute("""INSERT INTO orderitem (order_amount,Name,phone) values (%s,%s,%s)""",(bill_amt,name,phone))
		conn.commit()
		sql= "SELECT max(orderid) FROM orderitem WHERE Name=%s"
		c.execute(sql,(name,))
		id = c.fetchall()
		id=id[0][0]
		for i in range(len(food)):
			c.execute("""INSERT INTO items (orderid,item_name,quantity) values (%s,%s,%s)""",(id,food[i],quantity[i]))
			conn.commit()
			sql="select max(orderid) from orderitem";
			c.execute(sql)
			data=c.fetchall()
			print(data)
			data=int(data[0][0])
		speech="Thanks for ordering with us.Your bill amount is "+str(bill_amt)+". Remember your bill id for future reference:"+str(data)
		return {
			"speech" : speech,
			"displayText": speech,
			"source": "NITK_Management"
		}
		
	if stri.get("action")=="order.check":
		print('hi')
		parameters = stri.get("parameters")
		orderid = parameters.get("orderid")
		print(orderid)
		sql="SELECT item_name,quantity from items where orderid=%s"
		
		c.execute(sql,(orderid,))
		data = c.fetchall()
		speech=data
		if speech == []:
			speech="Sorry !! Your order id does not exist"
		else:
			for i in range(len(speech)):
				speech[i] = list(speech[i])

			#speech = "OK RESPONSE ARRIVED"
			print("Response:")
			speech = tabulate(speech,headers=['Item','Quantity'])
			print(speech)
			
			sql="select distinct order_amount from orderitem inner join items on orderitem.orderid=items.orderid where orderitem.orderid=%s"
			c.execute(sql,(orderid,))
			data=c.fetchall()
			speech=speech+"       "+"Bill amount : "+str(data[0][0])
		return {
			"speech" : speech,
			"displayText": speech ,
			"source": "NITK_Management"
		}
	
		
	if stri.get("action")=="library.book.search":
		parameters = stri.get("parameters")
		bookname = parameters.get("bookname")
	
		sql="SELECT Availability from library where bookname=%s"
		
		c.execute(sql,(bookname,))
		data = str(c.fetchall())
		avail_flag=int(data[2])
		if avail_flag == 0:
			speech = "Sorry the book is not available in the library.Please try again later."
		else:
			sql="SELECT bookname,Author,floor_no,shelf_no from library where bookname=%s"
			c.execute(sql,(bookname,))
			data = c.fetchall()
			speech=data
			
			for i in range(len(speech)):
				speech[i] = list(speech[i])
			#speech = "OK RESPONSE ARRIVED"
			print("Response:")
			speech = tabulate(speech,headers=['Book Name','Author','Floor no.','Shelf no.'])
			print(speech)
		return {
			"speech" : speech,
			"displayText": speech ,
			"source": "NITK_Management"
		}
		
	if stri.get("action")=="library.author.search":
		parameters = stri.get("parameters")
		authorname = parameters.get("Author")
	
		sql="SELECT Availability from library where Author=%s"
		
		c.execute(sql,(authorname,))
		data = str(c.fetchall())
		print(data)
		avail_flag=int(data[2])
		if avail_flag == 0:
			speech = "Sorry the book related to the author is not available currently in the library.Please try again later."
		else:
			sql="SELECT Author,bookname,floor_no,shelf_no from library where Author=%s"
			c.execute(sql,(authorname,))
			data = c.fetchall()
			speech=data
			
			for i in range(len(speech)):
				speech[i] = list(speech[i])
			#speech = "OK RESPONSE ARRIVED"
			print("Response:")
			speech = tabulate(speech,headers=['Author','Book Name','Floor no.','Shelf no.'])
			print(speech)
		return {
			"speech" : speech,
			"displayText": speech ,
			"source": "NITK_Management"
		}
	
	## our work starts here-module 1	
	if stri.get("action")=="academic.calendar":
		parameters = stri.get("parameters")
		year = str(parameters.get("academic_calendar-year")) 
		semester= str(parameters.get("calendar_semester"))
		print("\n")
		print(year+'\n'+semester+'\n')
		sql= "SELECT calendar_link FROM calendar WHERE year = %s AND semester = %s "
		c.execute(sql,(year,semester))
		data = str(c.fetchall())
		speech = data[4:-4] ;
		webbrowser.open(speech,new=new)
	 	#speech = "OK RESPONSE ARRIVED"
		speech_resp="Did you check out the calendar? Is there anything else that i can do for you?"
		print("Response:")
		print(data)
		print(speech_resp)
		return {
			"speech" : speech_resp,
			"displayText": speech_resp ,
			"source": "NITK_Management"
		}
		
	# module-2 block_wardens
    	
	if stri.get("action")=="hostel.wardens":
		parameters = stri.get("parameters")
		block = str(parameters.get("hostel_block")) 
		print("\n")
		print(block,type(block))
		sql= "SELECT Warden,Contact_no FROM warden WHERE Block=%s"
		c.execute(sql,(block,))
		data = str(c.fetchall())
		speech = data[4:-4];
	 	#speech = "OK RESPONSE ARRIVED"
		print("Response:")
		print(speech)
		#print(speech)
		return {
			"speech" : speech,
			"displayText": speech ,
			"source": "NITK_Management"
		}
		
		
	# module-3 faculty-search by depts.
    	
	if stri.get("action")=="faculty.search":
		parameters = stri.get("parameters")
		dept = str(parameters.get("faculty_dept")) 
		post = str(parameters.get("faculty_post"))
		if post == "Faculty":
			sql="SELECT * FROM faculty WHERE Department=%s"
			c.execute(sql,(dept,))
			print('\n')
		else:
			#print(dept,type(dept))
			sql= "SELECT * FROM faculty WHERE Department=%s and post=%s"
			c.execute(sql,(dept,post))
			print('\n')
		data = c.fetchall()
		speech=data
		for i in range(len(speech)):
			speech[i] = list(speech[i])
		#speech = "OK RESPONSE ARRIVED"
		print("Response:")
		speech = tabulate(speech,headers=['Name','Department','Qualification','Post'])
		print(speech)
		#print(speech)
		return {
			"speech" : speech,
			"displayText": speech ,
			"source": "NITK_Management"
		}
		
	
		
	# module-3 timing search.
    	
	if stri.get("action")=="timings.search":
		print('in action')
		parameters = stri.get("parameters")
		building = str(parameters.get("building")) 
		#print(dept,type(dept))
		sql= "SELECT open_timing,close_timing FROM timings WHERE Building=%s"
		c.execute(sql,(building,))
		print('\n')
		data = c.fetchall()
		speech=data
		
		for i in range(len(speech)):
			speech[i] = list(speech[i])
		#speech = "OK RESPONSE ARRIVED"
		print("Response:")
		print(speech)
		speech1="opening time : "+str(speech[0][0])
		speech2="closing time : "+str(speech[0][1])
		speech=speech1+"\n \n"+speech2
		#speech = tabulate(speech,headers=['Opening Time','Closing Time'])
		
		print(speech)
		return {
			"speech" : speech,
			"displayText": speech ,
			"source": "NITK_Management"
		}
		
	if stri.get("action")=="gpa.calculator":
		parameters = stri.get("parameters")
		pointer = str(parameters.get("pointer"))
		credits = str(parameters.get("credits"))
		no_courses = str(parameters.get("no_courses"))
		no_courses = int(no_courses)

		pointer = pointer.replace("[","")
		pointer = pointer.replace("]","")
		pointer = pointer.replace(",","")
		pointer = pointer.split(" ")
		for i in range(len(pointer)):
			pointer[i] = int(pointer[i])
			
		credits = credits.replace("[","")
		credits = credits.replace("]","")
		credits = credits.replace(",","")
		credits = credits.split(" ")
		for i in range(len(credits)):
			credits[i] = int(credits[i])
		print(pointer)
		print(credits)
		sum=0
		sgpa=0
		credit_sum=0
		for i in range(len(credits)):
			credit_sum+=credits[i]
		for i in range(no_courses):
			sum+=credits[i]*pointer[i]
		sum=float(sum)
		sgpa = sum/credit_sum
		sgpa = round(sgpa,2)
		speech="Your pointer is "+str(sgpa)
		return {
			"speech" : speech,
			"displayText": speech,
			"source": "NITK_Management"
		}
		
	

			
	else:
		return {
			"speech" : "Try again",
			"displayText": "Try again",
			"source": "NITK_Management"
		}
		

conn.commit()
if __name__ == '__main__':
    port=int(os.getenv('PORT',5000))
    app.run(debug=True)#,ssl_context='adhoc')
