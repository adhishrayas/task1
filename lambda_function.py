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
    users = [{"user_id": user[0], "full_name": user[1], "mob_num": user[2], "pan_num": user[3]} for user in data]
    return {"users": users}

  except Exception as e:
    return e

def delete_user(conn,data):
    try:
        cursor = conn.cursor()
        id = data.get('user_id')
        cursor.execute('SELECT * FROM users WHERE user_id = %s',(id,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            return "No user found"
        cursor.execute('DELETE FROM users WHERE user_id = %s',(id,))
        conn.commit()
        cursor.close()
        return f"User with id->{id} deleted"
    except Exception as e:
        return e

def update_user(conn,user_id,data):
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s',(user_id,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            return "No user exists"
        if "full_name" in data:
            new_name = data.get("full_name")
            if not new_name:
               return "Name cannot be empty"
            update_query = "UPDATE users SET full_name = %s WHERE user_id = %s;"
            cursor.execute(update_query,(new_name,user_id))
        if "mob_num" in data:
            new_mob = data.get("mob_num")
            if not is_valid_mob_num(new_mob):
              return "Enter a valid mobile number"
            update_query = "UPDATE users SET mob_num = %s WHERE user_id = %s;"
            cursor.execute(update_query,(new_mob,user_id))
        if "pan_num" in data:
            new_pan = data.get("pan_num")
            if not is_valid_pan(new_pan):
                return "Enter a valid PAN"
            update_query = "UPDATE users SET pan_num = %s WHERE user_id = %s;"
            cursor.execute(update_query,(new_pan,user_id))
        conn.commit()
        cursor.close()
        return f"Update succesful for user with id->{user_id}"
    except Exception as e:
        return e