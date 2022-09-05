from datetime import datetime
import os, psycopg2

def get_db_connection():
    # print(os.environ['DB_USERNAME'],os.environ['DB_PASSWORD'])
    return psycopg2.connect(
                host='localhost',
                database='flask_db',
                user=os.environ['DB_USERNAME'],
                password=os.environ['DB_PASSWORD']
            )

def __db_init():
    try:
        conn = get_db_connection()
        curr = conn.cursor()
        curr.execute(
            """ CREATE TABLE IF NOT EXISTS user_table(
                username CHARACTER VARYING(32) NOT NULL,
                email CHARACTER VARYING(64) NOT NULL,
                firstname CHARACTER VARYING(32) NOT NULL,
                middlename CHARACTER VARYING(32),
                lastname CHARACTER VARYING(32) NOT NULL,
                birthdate DATE NOT NULL,
                priviledge INT NOT NULL,
                password CHARACTER VARYING(256) NOT NULL,
                CONSTRAINT "username" UNIQUE ("username")
            )
            """
        )
        curr.execute(
            """ CREATE TABLE IF NOT EXISTS session_table(
                susername CHARACTER VARYING(32) NOT NULL,
                ipaddress INET NOT NULL,
                logindatetime TIMESTAMP WITH TIME ZONE NOT NULL,
                CONSTRAINT "susername" UNIQUE ("susername")
            )
            """
        )
        curr.execute(
            """ CREATE TABLE IF NOT EXISTS log_table(
                lusername CHARACTER VARYING(32) NOT NULL,
                logdatetime TIMESTAMP WITH TIME ZONE NOT NULL,
                activity CHARACTER VARYING(32)
            )
            """
        )
        curr.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def insert_user(args):
    try:
        conn = get_db_connection()
        curr = conn.cursor()
        qu = """INSERT INTO user_table VALUES (%(username)s, %(email)s, %(firstname)s, %(middlename)s, %(lastname)s, %(birthdate)s, %(priviledge)s, %(password)s)"""
        curr.execute(qu, args)
        __log_act(args["username"],"REGISTER",curr, conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def get_user(username=None, email=None):
    result = ()
    if not username and email:
        return result
    else:
        try:
            conn = get_db_connection()
            curr = conn.cursor()
            curr.execute(f"SELECT username, email, firstname, middlename, lastname, birthdate FROM user_table WHERE username = '{username}'")
            result = curr.fetchone()
            curr.close()
            conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            return result

def check_user(username, email=None, enc_passwd=None):
    result = -1
    try:
        conn = get_db_connection()
        curr = conn.cursor()
        if enc_passwd:
            result = True
            curr.execute(f"SELECT password FROM user_table WHERE username = '{username}'")
            db_passwd = curr.fetchone()
            if db_passwd == None:
                result = False
            elif db_passwd[0] != enc_passwd:
                result = False
        elif email:
            result = False
            curr.execute("SELECT username, email FROM user_table")
            rows = curr.fetchall()
            for row in rows:
                if username in row or email in row:
                    result = True
                    break

        curr.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        return result

def delete_user(username):
    try:
        conn = get_db_connection()
        curr = conn.cursor()
        curr.execute(f"DELETE FROM user_table WHERE username = '{username}'")
        __log_act(username,"DELETE",curr,conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def update_user(username, args):
    try:
        conn = get_db_connection()
        curr = conn.cursor()
        qu = "UPDATE user_table SET "
        for k in args:
            qu+=f"{k} = '{args[k]}', "
        qu=qu[:-2]+f" WHERE username = '{username}'"
        curr.execute(qu)
        __log_act(username,"UPDATE",curr,conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def is_admin(username):
    try:
        result = False
        conn = get_db_connection()
        curr = conn.cursor()
        curr.execute(f"SELECT priviledge FROM user_table WHERE username = '{username}'")
        priv = curr.fetchone()
        if priv != None:
            if int(priv[0]) > 1:
                result = True
        curr.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        return result

def login_user(username, IP):
    try:
        conn = get_db_connection()
        curr = conn.cursor()
        qu = """INSERT INTO session_table VALUES (%(susername)s, %(ipaddress)s, %(logindatetime)s)"""
        curr.execute(qu,{"susername": username, "ipaddress":IP, "logindatetime": datetime.now()})
        __log_act(username,"LOGIN",curr,conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def logout_user(username):
    try:
        conn = get_db_connection()
        curr = conn.cursor()
        curr.execute(f"DELETE FROM session_table WHERE susername = '{username}'")
        __log_act(username,"LOGOUT",curr,conn)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

def list_table(table, model):
    result = []
    try:
        conn = get_db_connection()
        curr = conn.cursor()
        curr.execute(f"SELECT * FROM {table}")
        result = __parse_dict(model, curr.fetchall())
        curr.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        return result

def __parse_dict(keys, lst):
    result = []
    if not len(lst):
        pass
    else:
        for val in lst:
            elem = {}
            for i in range(len(keys)):
                elem[keys[i]] = val[i]
            result.append(elem)
    return result

def __get_salt(username):
    salt = ""
    try:
        conn = get_db_connection()
        curr = conn.cursor()
        curr.execute(f"SELECT password FROM user_table WHERE username='{username}'")
        salt = curr.fetchone()[0].split(":")[1]
        curr.close()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
        return salt

def __log_act(username, activity, curr, conn):
    logs = """INSERT INTO log_table VALUES (%(lusername)s, %(logdatetime)s, %(activity)s)"""
    curr.execute(logs,{"lusername": username, "logdatetime": datetime.now(), "activity": activity})
    curr.close()
    conn.commit()