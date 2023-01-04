import psycopg2
from model.model_classes import User
import random
import string
import time
import logging
import os
import shutil

logging.basicConfig()

server_path = "/Users/venkat-16321/Desktop/Cloud"

def connection():
    conn = psycopg2.connect(host="localhost", user="venkat-16321", password='', database='Cloud Apps')
    return conn


def insert_user(user_email, phone_number, password, country, user_name):
    conn = connection()
    my_cursor = conn.cursor()
    query = "INSERT INTO public.app_user (user_email, phone_number, password, country, used_memory, user_name, image_count) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    value = (user_email, phone_number, password, country, 0, user_name, 0,)
    try:
        my_cursor.execute(query, value)
        conn.commit()
    except:
        return -1
    my_cursor.close()
    conn.close()
    if my_cursor.rowcount > 0:
        try:
            path = os.path.join(server_path, user_email)
            os.makedirs(path)
        except Exception:
            return -2
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
                    used_memory=result[0][5], country=result[0][3], image_count=result[0][7])
    except Exception:
        return None
    my_cursor.close()
    conn.close()
    return user


def update_user(email, password, user_name, phone_num):
    conn = connection()
    my_cursor = conn.cursor()
    query = "UPDATE public.app_user SET  phone_number = %s, user_name=%s, password=%s where user_email = %s"
    values = (phone_num, user_name, password, email)
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
    if my_cursor.rowcount > 0:
        path = os.path.join(server_path, email)
        if os.path.exists(path):
            shutil.rmtree(path)
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
    validity = round(time.time() * 1000) + (60 * 60 * 1000)
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


def insert_folder(folder_name, auth_key):
    email_check = get_user_email_from_authkey(auth_key)
    if email_check is None:
        return -1  # authentication failure
    user_path = os.path.join(server_path, email_check)
    folder_path = os.path.join(user_path, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    else:
        return -2


def delete_folder(folder_name, auth_key):
    email_check = get_user_email_from_authkey(auth_key)
    if email_check is None:
        return -1  # authentication failure
    user_path = os.path.join(server_path, email_check)
    folder_path = os.path.join(user_path, folder_name)
    if os.path.exists(folder_path):
        shutil.rmtree(folder_path)
    else:
        return -2


def get_folder(auth_key):
    email_check = get_user_email_from_authkey(auth_key)
    if email_check is None:
        return -1  # authentication failure
    user_path = os.path.join(server_path, email_check)
    user_folders = os.listdir(user_path)
    try:
        user_folders.remove(".DS_Store")
    except:
        pass
    return user_folders


def update_folder(old_folder_name, new_folder_name, authKey):
    email_check = get_user_email_from_authkey(authKey)
    if email_check is None:
        return -1  # authentication failure
    user_path = os.path.join(server_path, email_check)
    folder_path = os.path.join(user_path, old_folder_name)
    replacing_path = os.path.join(user_path, new_folder_name)
    if os.path.exists(folder_path) and not os.path.exists(new_folder_name):
        os.replace(folder_path, replacing_path)
    else:
        return -2


def insert_image(image, folder_name, image_name, authKey, image_size):
    fetching_email = get_user_email_from_authkey(authKey)
    if fetching_email is None:
        return -1  # authentication failure
    user_path = os.path.join(server_path, fetching_email)
    folder_path = os.path.join(user_path, folder_name)
    name = ""
    for ch in image_name:
        if ch == " ":
            name += '_'
        else:
            name += ch
    # name += ".jpg"
    if os.path.exists(folder_path):
        checking_space = updating_user_memory(image_size, fetching_email)
        if checking_space > 0:
            os.chdir(folder_path)
            with open(name, 'wb') as f:
                for i in image:
                    f.write(i)
            return 1
        else:
            return -3
    else:
        return -2


def updating_user_memory(image_size, email):
    conn = connection()
    my_cursor = conn.cursor()
    user = get_User(email)
    memory = user.used_memory+int(image_size)
    if memory <= user.memory:
        query = "UPDATE public.app_user SET used_memory = %s, image_count = %s where user_email = %s"
        values = (memory, user.image_count+1, email,)
        my_cursor.execute(query, values)
        conn.commit()
    my_cursor.close()
    conn.close()
    return my_cursor.rowcount


def get_images_in_folder(authKey, folder_name):
    email_check = get_user_email_from_authkey(authKey)
    if email_check is None:
        return -1  # authentication failure
    user_path = os.path.join(server_path, email_check)
    folder_path = os.path.join(user_path, folder_name)
    user_folders = os.listdir(folder_path)
    try:
        user_folders.remove(".DS_Store")
    except:
        pass
    return user_folders


def delete_images_in_folder(authKey, folder_name, image_name):
    email_check = get_user_email_from_authkey(authKey)
    print(email_check)
    if email_check is None:
        return -1  # authentication failure
    user_path = os.path.join(server_path, email_check)
    folder_path = os.path.join(user_path, folder_name)
    image_path = os.path.join(folder_path, image_name )
    if os.path.exists(folder_path):
        if os.path.exists(image_path):
            os.remove(image_path)
            return 1
        else:
            return -3
    else:
        return -2


def move_image_another_folder(image_name, authKey, folder_name, another_folder_name):
    email_check = get_user_email_from_authkey(authKey)
    if email_check is None:
        return -1  # authentication failure
    user_path = os.path.join(server_path, email_check)
    folder_path = os.path.join(user_path, folder_name)
    another_folder_path = os.path.join(user_path, another_folder_name)
    image_path = os.path.join(folder_path, image_name)
    changing_image_path = os.path.join(another_folder_path, image_name)
    if os.path.exists(another_folder_path):
        if os.path.exists(folder_path):
            if os.path.exists(image_path):
                shutil.move(image_path, changing_image_path)
                return 1
            else:
                return -3
        else:
            return -2
    else:
        return -4


def get_size_folder(folder):
    folder_size = 0
    images_in_folder = os.listdir(folder)
    try:
        images_in_folder.remove(".DS_Store")
    except:
        pass
    count = len(images_in_folder)
    os.chdir(folder)
    for image in images_in_folder:
        with open(image, 'rb') as f:
            folder_size += len(f.read())
    return [folder_size, count]


def folder_metrics(authKey, folder_name):
    email_check = get_user_email_from_authkey(authKey)
    if email_check is None:
        return -1  # authentication failure
    user_path = os.path.join(server_path, email_check)
    folder_path = os.path.join(user_path, folder_name)
    if os.path.exists(folder_path):
        folder_details = get_size_folder(folder_path)
        return folder_details
    else:
        return -2


def user_metrics(authKey):
    email_check = get_user_email_from_authkey(authKey)
    if email_check is None:
        return -1  # authentication failure
    user_path = os.path.join(server_path, email_check)
    if os.path.exists(user_path):
        user_folder_list = os.listdir(user_path)
        try:
            user_folder_list.remove(".DS_Store")
        except:
            pass
        metrics_list = []
        for folder_name in user_folder_list:
            folder_path = os.path.join(user_path, folder_name)
            folder_details = get_size_folder(folder_path)
            folder_details.append(folder_name)
            metrics_list.append(folder_details)
        return metrics_list
    else:
        return -2


