import pymysql

conn = pymysql.connect(
    host="localhost",
    port=3306,
    user="root",
    password="aryanyuvi5",
    database="users"
)

email = 'aryannaithani1089@gmail.com'
password = 'aryanyuvi5'
cursor = conn.cursor()
cursor.execute("SELECT * FROM uinfo;")
rows = cursor.fetchall()
cursor.execute(f"INSERT INTO uinfo VALUES(\"{email}\", \"{password}\");")
print('Inserted')

cursor.close()
conn.close()
