import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

cnx = mysql.connector.connect(
    user=os.environ['MYSQL_USER'],
    password=os.environ['MYSQL_PASS'],
    host=os.environ['MYSQL_HOST'],
    database=os.environ['MYSQL_DB'],
)


def get_device_list_data():
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


def get_device_chart_data(device_id):
    cursor = cnx.cursor()
    query = ("""
        select 
            device_id,
            avg(co2) co2,
            avg(air_temp) air_temp,
            avg(air_humid) air_humid,
            avg(left_water_temp) left_water_temp,
            avg(right_water_temp) right_water_temp,
            avg(tower_led_pwm) tower_led_pwm,
            date_format(timestamp, '%Y-%m-%d %H:%i') time
        from reactor_data
        where device_id = %s
        group by time
    """)

    cursor.execute(query, (device_id,))

    return cursor.fetchall()


def get_device_data(device_id: str):
    cursor = cnx.cursor()
    query = ("""
        select 
            device_id,
            co2,
            air_temp,
            air_humid,
            left_water_temp,
            right_water_temp,
            tower_led_pwm,
            timestamp
        from reactor_data
        where device_id = %s
        order by id desc
        limit 1
    """)

    cursor.execute(query, (device_id,))

    return cursor.fetchone()


def get_device_exists(device_id: str) -> bool:
    cursor = cnx.cursor()
    query = ("""
            select 
                id, name
            from reactors
            where name = %s
            limit 1
        """)

    cursor.execute(query, (device_id,))

    res = cursor.fetchone()

    return res is not None


def insert_device_data(
        device_id,
        co2,
        air_temp,
        air_humid,
        left_water_temp,
        right_water_temp,
        tower_led_pwm,
        timestamp,
) -> None:
    cursor = cnx.cursor()

    query = ("""
        insert into reactor_data 
        (device_id, co2, air_temp, air_humid, left_water_temp, right_water_temp, tower_led_pwm, timestamp)
        values (%s, %s, %s, %s, %s, %s, %s, %s)
    """)

    cursor.execute(
        query,
        (device_id, co2, air_temp, air_humid, left_water_temp, right_water_temp, tower_led_pwm, timestamp)
    )

    cnx.commit()

    return None
