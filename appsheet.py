import mysql.connector

cnx = mysql.connector.connect(user='kriss', password='root',
                              host='34.70.127.41', database='atdata-381118:us-central1:atdata')
cursor = cnx.cursor()
query = ("SELECT * FROM heroic-trilogy-375020.data_algae_tree.device_ID")
cursor.execute(query)

for row in cursor:
    print(row)
