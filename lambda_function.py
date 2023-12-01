import uuid,re,json
from pathlib import Path
import psycopg2
from psycopg2 import sql
# adding connection to the aws db
conn = psycopg2.connect(
            host='database-2.cdrddmhbv4ei.eu-north-1.rds.amazonaws.com',
            database='postgres',
            user='postgres',
            password='adhi1234',
        )

#simple functions for checking validity of input data
def is_valid_mob_num(mob_num):
    return re.match(r'^\d{10}$', mob_num) is not None

def is_valid_pan(pan):
    return re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$',pan) is not None


#creates the user table in the db, if it does not exist
def create_user_table(conn):
    try:
        cursor = conn.cursor() #cursor for querying the db
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
        response = e
        return json.dumps(response,default=str)

#creates a user in the db with the given input
def create_user(event,context):
    try:
        if not event['full_name']:
            return "Full name cannot be empty"
        if not is_valid_mob_num(event['mob_num']):
            return "Please enter a valid mobile number"
        if not is_valid_pan(event['pan_num']):
            return "PAN is invalid"
        
        id = str(uuid.uuid4()) #generating the uuid
        create_user_table(conn)# checking for the table
        cursor = conn.cursor()
        insert_q = sql.SQL("INSERT INTO users (user_id, full_name, mob_num, pan_num) VALUES (%s, %s, %s, %s);")
        cursor.execute(insert_q, (id, event['full_name'], event['mob_num'], event['pan_num'])) #querying and adding the user to the table
        conn.commit()
        cursor.close()
        response = f'User with id->{id} created'
        return json.dumps(response,default=str)
    except Exception as e:
        return json.dumps(e,default=str)

def get_users(event,context): #function to get all users
  try:  
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users;')
    data = cursor.fetchall()
    cursor.close()
    if not data:
        return {"users":[]}#returns empty array if db is empty
    users = [{"user_id": user[0], "full_name": user[1], "mob_num": user[2], "pan_num": user[3]} for user in data]
    return {"users": users}

  except Exception as e:
    return e

def delete_user(event,context):#function for deleting users
    try:
        cursor = conn.cursor()
        id = event['user_id']
        cursor.execute('SELECT * FROM users WHERE user_id = %s',(id,))
        user = cursor.fetchone()
        if not user: #checking if the given user exists in the db
            cursor.close()
            return {"message":"No user found"}
        cursor.execute('DELETE FROM users WHERE user_id = %s',(id,))#querying and deleting the user
        conn.commit()
        cursor.close()
        return {"message":f"User with {id} deleted"}
    except Exception as e:
        return json.dumps(e,default=str)

def update_user(event,context):#function for updating the user in the db
    try:
        user_id = event['user_id']
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE user_id = %s',(user_id,))
        user = cursor.fetchone()
        if not user:#check if the user exists
            cursor.close()
            return {"message":"No user found"}
        if "full_name" in event['update_data']:#check for individual fields if they exist or not and are they valid or not
            new_name = event['update_data']['full_name']
            if not new_name:
               return {"message":"Name cant be empty"}
            update_query = "UPDATE users SET full_name = %s WHERE user_id = %s;"
            cursor.execute(update_query,(new_name,user_id))
        if "mob_num" in event['update_data']:
            new_mob = event['update_data']['mob_num']
            if not is_valid_mob_num(new_mob):
              return {"message":"Enter valid number"}
            update_query = "UPDATE users SET mob_num = %s WHERE user_id = %s;"
            cursor.execute(update_query,(new_mob,user_id))
        if "pan_num" in event['update_data']:
            new_pan = event['update_data']['pan_num']
            if not is_valid_pan(new_pan):
                return {"message":"Enter valid pan"}
            update_query = "UPDATE users SET pan_num = %s WHERE user_id = %s;"
            cursor.execute(update_query,(new_pan,user_id))
        conn.commit()
        cursor.close()
        return {"message":f"Update succes for {user_id}"}
    except Exception as e:
        return json.dumps(e,default=str)