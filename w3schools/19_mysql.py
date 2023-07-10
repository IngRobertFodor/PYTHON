# Row 18-22
# You have to change the DB name, everytime you run this script.


# MYSQL PURPOSES
import mysql.connector
# pip install mysqlclient


mydb = mysql.connector.connect(
  host="localhost",
  user="Administrator",
  password="Initial0"
)
# Check connection.
print(mydb)


# Create DB.
# You have to change the DB name, everytime you run this script.
mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE my_rf_database")


# Check my_rf_database.
mycursor.execute("SHOW DATABASES")

for x in mycursor:
  print(x)


# Connect to "my_rf_database".
mydb = mysql.connector.connect(
  host="localhost",
  user="Administrator",
  password="Initial0",
  database="my_rf_database"
  )