import mysql.connector
import os


def get_device_list_data():
    cnx = mysql.connector.connect(
        user=os.environ['MYSQL_USER'],
        password=os.environ['MYSQL_PASS'],
        host=os.environ['MYSQL_HOST'],
        database=os.environ['MYSQL_DB'],
    )

    cursor = cnx.cursor()
    query = ("""
select r.name, co2, air_temp, air_humid, left_water_temp, right_water_temp, tower_led_pwm, timestamp
from reactor_data rd
         inner join (select max(rd.id) id
                     from reactor_data rd
                     group by rd.device_id) x on x.id = rd.id
inner join reactors r on rd.device_id = r.id
order by r.name asc
    """)

    cursor.execute(query)

    return cursor.fetchall()
