import psycopg2
from model.model_classes import User
import random
import string
import time
import logging

logging.basicConfig()


def connection():
    conn = psycopg2.connect(host="localhost", user="venkat-16321", password='', database='Cloud Apps')
    return conn


def insert_user(user_email, phone_number, password, country, user_name):
    conn = connection()
    my_cursor = conn.cursor()
    query = "INSERT INTO public.app_user (user_email, phone_number, password, country, used_memory, user_name) VALUES (%s, %s, %s, %s, %s, %s)"
    value = (user_email, phone_number, password, country, 0, user_name)
    try:
        my_cursor.execute(query, value)
        conn.commit()
    except:
        return -1
    my_cursor.close()
    conn.close()
    return my_cursor.rowcount


def get_User(email):
    conn = connection()
    my_cursor = conn.cursor()
    query = "SELECT * FROM app_user where user_email = %s"
    value = (email,)
    my_cursor.execute(query, value)
    result = my_cursor.fetchall()
    try:
        user = User(name=result[0][6], phone_no=result[0][1], user_email=result[0][0], user_password=result[0][2],
                    used_memory=result[0][5], country=result[0][4])
    except Exception:
        return None
    print(user)
    print("sucrss")
    my_cursor.close()
    conn.close()
    return user


def update_user(email, password, user_name, phone_num):
    conn = connection()
    my_cursor = conn.cursor()
    query = "UPDATE public.app_user SET user_email = %s, phone_number = %s, user_name=%s, password=%s"
    values = (email, phone_num, user_name, password)
    my_cursor.execute(query, values)
    conn.commit()
    my_cursor.close()
    conn.close()
    return my_cursor.rowcount


def delete_user(email, password):
    conn = connection()
    my_cursor = conn.cursor()
    query = "DELETE FROM app_user where user_email = %s and password = %s"
    value = (email, password)
    my_cursor.execute(query, value)
    conn.commit()
    my_cursor.close()
    conn.close()
    return my_cursor.rowcount


def insert_token(token, email, curr_time):
    conn = connection()
    my_cursor = conn.cursor()
    query = "INSERT INTO public.auth_key (user_email, auth_token, expiry_time) VALUES (%s, %s, %s)"
    value = (email, token, curr_time,)
    my_cursor.execute(query, value)
    conn.commit()
    my_cursor.close()
    conn.close()


def get_tokens():
    conn = connection()
    my_cursor = conn.cursor()
    query = "SELECT auth_token FROM auth_key"
    my_cursor.execute(query)
    result = []
    for token in my_cursor.fetchall():
        result.append(token[0])
    my_cursor.close()
    conn.close()
    return result


def generate_token(email):
    remove_tokens()
    token = ''.join(random.sample(string.hexdigits, int(16)))
    validity = round(time.time() * 1000) + (60 * 30 * 1000)
    tokens = get_tokens()
    while True:
        if token not in tokens:
            insert_token(token, email, validity)
            push = []
            push.append(token)
            push.append(validity)
            return push
        token = ''.join(random.sample(string.hexdigits, int(16)))
    return False


def remove_tokens():
    curr_time = round(time.time() * 1000)
    conn = connection()
    my_cursor = conn.cursor()
    query = "DELETE FROM auth_key where expiry_time <= %s"
    my_cursor.execute(query, (curr_time,))
    conn.commit()
    my_cursor.close()
    conn.close()


def get_user_email_from_authkey(auth_key):
    remove_tokens()
    conn = connection()
    my_cursor = conn.cursor()
    query = "SELECT user_email FROM auth_key where auth_token = %s"
    value = (auth_key,)
    my_cursor.execute(query, value)
    result = my_cursor.fetchone()
    if result is not None:
        return result[0]
    return None


def check_folder_already_exists(folder_name):
    conn = connection()
    my_cursor = conn.cursor()
    query = "SELECT count(*) FROM folder where folder_name = %s"
    value = (folder_name,)
    my_cursor.execute(query, value)
    result = my_cursor.fetchone()[0]
    if result is None:
        return 0
    return result


def insert_folder(folder_name, auth_key):
    conn = connection()
    my_cursor = conn.cursor()
    email_check = get_user_email_from_authkey(auth_key)
    if email_check is None:
        return -1  # authentication failure
    check_folder = check_folder_already_exists(folder_name)
    if check_folder >= 1:
        return -2
    query = "INSERT INTO public.folder (folder_name, user_email) VALUES (%s, %s)"
    value = (folder_name, email_check,)
    my_cursor.execute(query, value)
    conn.commit()
    my_cursor.close()
    conn.close()
    return my_cursor.rowcount


def delete_folder(folder_name, auth_key):
    conn = connection()
    my_cursor = conn.cursor()
    email_check = get_user_email_from_authkey(auth_key)
    if email_check is None:
        return -1  # authentication failure
    check_folder = check_folder_already_exists(folder_name)
    if check_folder == 0:
        return -2
    query = "DELETE FROM folder WHERE folder_name= %s"
    value = (folder_name,)
    my_cursor.execute(query, value)
    conn.commit()
    my_cursor.close()
    conn.close()
    return my_cursor.rowcount


def get_folder(auth_key):
    conn = connection()
    my_cursor = conn.cursor()
    email_check = get_user_email_from_authkey(auth_key)
    if email_check is None:
        return -1  # authentication failure
    query = "SELECT folder_name FROM folder where user_email= %s"
    value = (email_check,)
    my_cursor.execute(query, value)
    output = my_cursor.fetchall()
    my_cursor.close()
    conn.close()
    return output


def update_folder(old_folder_name, new_folder_name, auth_key):
    conn = connection()
    my_cursor = conn.cursor()
    email_check = get_user_email_from_authkey(auth_key)
    if email_check is None:
        return -1  # authentication failure
    check_folder = check_folder_already_exists(new_folder_name)
    if check_folder >= 1:
        return -2
    query = "UPDATE public.folder SET folder_name = %s where user_email = %s and folder_name = %s"
    value = (new_folder_name, email_check, old_folder_name)
    my_cursor.execute(query, value)
    conn.commit()
    my_cursor.close()
    conn.close()
    return my_cursor.rowcount


def insert_image(image_path, folder_name, image_name, image_size, authKey):
    conn = connection()
    my_cursor = conn.cursor()
    fetching_email = get_user_email_from_authkey(authKey)
    if fetching_email is None:
        return -1  # authentication failure
    check_folder = check_folder_already_exists(folder_name)
    if check_folder == 0:
        return -2
    query = "INSERT INTO public.images (image_path, folder_name, image_name, image_size) VALUES (%s, %s, %s, %s)"
    value = (image_path, folder_name, image_name, image_size,)
    my_cursor.execute(query, value)
    conn.commit()
    my_cursor.close()
    conn.close()
    return my_cursor.rowcount


def get_images(folder_name, authKey):
    conn = connection()
    my_cursor = conn.cursor()

    query = "SELECT image_path FROM images where folder_name = %s"
    my_cursor.execute(query)
    result = []
    for token in my_cursor.fetchall():
        result.append(token[0])
    my_cursor.close()
    conn.close()
    return result



print(insert_image("abcd", "Albums", "ooty", 10, '12938eD57f4bBdCa'))


