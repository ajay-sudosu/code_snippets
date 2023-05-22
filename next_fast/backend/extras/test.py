import pymysql
import datetime
import csv
endpoint = "nextmed-database.crkwdx8kqlsw.us-east-2.rds.amazonaws.com"
# endpoint = "test-database.crkwdx8kqlsw.us-east-2.rds.amazonaws.com"
username = "admin"
password = "password6969"

connection = pymysql.connect(endpoint, user=username, passwd=password, db="nextmed")

query = open("query.txt", "r").read().splitlines()

cursor = connection.cursor(pymysql.cursors.DictCursor)

def parse_time(t):

    try:
        t = str(t)
        if t == "2400":
            return "12:00 AM"
        if len(t) == 4:
            final = t[0] + t[1] + ":" + t[2] + t[3]
        else:
            final = t[0] + ":" + t[1] + t[2]

        try:
            d = datetime.strptime(final, "%H:%M")
            return d.strftime("%I:%M %p") 
        except:
            return final

    except:
        return "NA"

for i in query:
	cursor.execute(i)
	visits = list(cursor.fetchall())
	print(visits)
	print(f'{len(visits)} results')

# cursor.execute(f'select * from visits')

# final = [["Email", "Phone Number", "First Name", "Last Name", "City", "State", "Country", "Zip Code", "Date of Birth", "Year of Birth", "Gender", "Age"]]
# visits = list(cursor.fetchall())

# for i in visits:

# 	if i["sex"] == 0:
# 		sex = "M"
# 	elif i["sex"] == 1:
# 		sex = "F"
# 	else: 
# 	    sex = "Other"

# 	dob = f'{i["dob_month"]}/{i["dob_date"]}/{i["dob_year"]}'

# 	if dob == "1/1/2000" or dob == "0/0/0":
# 		dob = "N/A"

# 	if i["location"] == "new york":
# 		city = "New York"
# 		state = "NY"
# 	elif i["location"] == "miami":
# 		city = "Miami"
# 		state = "FL"
# 	elif i["location"] == "atlanta":
# 		city = "Atlanta"
# 		state = "GA"
# 	elif i["location"] == "chicago":
# 		city = "Chicago"
# 		state = "IL"
# 	else:
# 		city = "New York"
# 		state = "NY"

# 	name_arr = i["patient_name"].split(" ")

# 	first_name = name_arr[0]

# 	if len(name_arr) > 1:
# 		last_name = name_arr[1]
# 	else:
# 		last_name = ""
	
# 	temp = [i["email"], i["phone"], first_name, last_name, city, state, "US", i["zip_code"], dob, i["dob_year"], sex, i["age"]]

# 	final.append(temp)

# with open('visits.csv', mode='w') as f:
#     writer = csv.writer(f, delimiter=',')

#     for j in final:
#     	writer.writerow(j)

connection.commit()
connection.close()