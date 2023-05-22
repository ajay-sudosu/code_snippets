import pymysql

endpoint = "nextmed-database.crkwdx8kqlsw.us-east-2.rds.amazonaws.com"
username = "admin"
password = "password6969"

connection = pymysql.connect(endpoint, user=username, passwd=password, db="nextmed")

cursor = connection.cursor()

cursor.execute("select * from errors")

k = list(cursor.fetchall())

for i in k:
	print(i)