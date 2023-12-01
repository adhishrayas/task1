import uuid,os,environ,re
from pathlib import Path
import psycopg2
from psycopg2 import sql

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env()

conn = psycopg2.connect(
             host='database-1.cdrddmhbv4ei.eu-north-1',
             port=5432,  
             user='postgres',
             password='adhi1234',
             database='postgres'
        )

def is_valid_mob_num(mob_num):
    return re.match(r'^\d{10}$', mob_num) is not None

def is_valid_pan(pan):
    return re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$',pan) is not None



def create_user_table(conn):
    try:
        cursor = conn.cursor()
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS users (
                user_id UUID PRIMARY KEY,
                full_name VARCHAR(255) NOT NULL,
                mob_num VARCHAR(10) NOT NULL,
                pan_num VARCHAR(10) NOT NULL
            );
        '''
        cursor.execute(create_table_query)
        conn.commit()
        cursor.close()

    except Exception as e:
        print(f'Error creating table: {e}')

def create_user(data):
    try:
        if not data.get('full_name'):
            return "Full name cannot be empty"
        if not is_valid_mob_num(data.get('mob_num')):
            return "Please enter a valid mobile number"
        if not is_valid_pan(data.get('pan_num')):
            return "PAN is invalid"
        
        id = str(uuid.uuid4())
        create_user_table(conn)
        cursor = conn.cursor()
        insert_q = sql.SQL("INSERT INTO users (user_id, full_name, mob_num, pan_num) VALUES (%s, %s, %s, %s);")
        cursor.execute(insert_q, (id, data.get('full_name'), data.get('mob_num'), data.get('pan_num')))
        conn.commit()
        cursor.close()
        return f"User created with id-{id}"
    except Exception as e:
        return e

def get_users(conn):
  try:  
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users;')
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return {"users":[]}
    users = [{"user_id": user[0], "full_name": user[1], "mob_num": user[2], "pan_num": user[3]} for user in users_data]
    return {"users": users}

  except Exception as e:
    return {"error": "Internal server error"}
