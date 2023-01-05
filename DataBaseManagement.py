import psycopg2
from model.model_classes import User
import random
import string
import time
import logging
import os
import shutil
from PIL import Image
import io

logging.basicConfig()

server_path = "/Users/venkat-16321/Desktop/Cloud"


def connection():
    conn = psycopg2.connect(host="localhost", user="venkat-16321", password='', database='Cloud Apps')
    return conn


def checking_name(name):
    valid_name = ""
    for ch in name:
        if ch == " ":
            valid_name += '_'
        else:
            valid_name += ch
    return valid_name


class UserManagement:

    def __init__(self):
        self.conn = connection()
        self.my_cursor = self.conn.cursor()

    def insert_user(self, user_email, phone_number, password, country, user_name):
        query = "INSERT INTO public.app_user (user_email, phone_number, password, country, used_memory, user_name, image_count) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        value = (user_email, phone_number, password, country, 0, user_name, 0,)
        try:
            self.my_cursor.execute(query, value)
            self.conn.commit()
        except:
            return -1
        # self.my_cursor.close()
        # self.conn.close()
        if self.my_cursor.rowcount > 0:
            try:
                path = os.path.join(server_path, user_email)
                os.makedirs(path)
            except Exception:
                return -2
        return self.my_cursor.rowcount

    def get_User(self, email):
        query = "SELECT * FROM app_user where user_email = %s"
        value = (email,)
        self.my_cursor.execute(query, value)
        result = self.my_cursor.fetchall()
        try:
            user = User(name=result[0][6], phone_no=result[0][1], user_email=result[0][0], user_password=result[0][2],
                        used_memory=result[0][5], country=result[0][3], image_count=result[0][7])
        except Exception:
            return None
        # self.my_cursor.close()
        # self.conn.close()
        return user

    def update_user(self, email, password, user_name, phone_num):
        query = "UPDATE public.app_user SET  phone_number = %s, user_name=%s, password=%s where user_email = %s"
        values = (phone_num, user_name, password, email)
        self.my_cursor.execute(query, values)
        self.conn.commit()
        # self.my_cursor.close()
        # self.conn.close()
        return self.my_cursor.rowcount

    def delete_user(self, email, password):
        query = "DELETE FROM app_user where user_email = %s and password = %s"
        value = (email, password)
        self.my_cursor.execute(query, value)
        self.conn.commit()
        # self.my_cursor.close()
        # self.conn.close()
        if self.my_cursor.rowcount > 0:
            path = os.path.join(server_path, email)
            if os.path.exists(path):
                shutil.rmtree(path)
        return self.my_cursor.rowcount

    def updating_user_memory(self, image_size, email, count):
        conn = connection()
        my_cursor = conn.cursor()
        user = self.get_User(email)
        memory = user.used_memory + int(image_size)
        if memory <= user.memory:
            query = "UPDATE public.app_user SET used_memory = %s, image_count = %s where user_email = %s"
            values = (memory, user.image_count + count, email,)
            my_cursor.execute(query, values)
            conn.commit()
        # my_cursor.close()
        # conn.close()
        return my_cursor.rowcount


class AuthManagament:

    def __init__(self):
        self.conn = connection()
        self.my_cursor = self.conn.cursor()

    def insert_token(self, token, email, curr_time):
        query = "INSERT INTO public.auth_key (user_email, auth_token, expiry_time) VALUES (%s, %s, %s)"
        value = (email, token, curr_time,)
        self.my_cursor.execute(query, value)
        self.conn.commit()
        # self.my_cursor.close()
        # self.conn.close()

    def get_tokens(self):
        query = "SELECT auth_token FROM auth_key"
        self.my_cursor.execute(query)
        result = []
        for token in self.my_cursor.fetchall():
            result.append(token[0])
        # self.my_cursor.close()
        # self.conn.close()
        return result

    def generate_token(self, email):
        self.remove_tokens()
        token = ''.join(random.sample(string.hexdigits, int(16)))
        validity = round(time.time() * 1000) + (60 * 60 * 1000)
        tokens = self.get_tokens()
        while True:
            if token not in tokens:
                self.insert_token(token, email, validity)
                push = []
                push.append(token)
                push.append(validity)
                return push
            token = ''.join(random.sample(string.hexdigits, int(16)))

    def remove_tokens(self):
        curr_time = round(time.time() * 1000)
        query = "DELETE FROM auth_key where expiry_time <= %s"
        self.my_cursor.execute(query, (curr_time,))
        self.conn.commit()

    def get_user_email_from_authkey(self, auth_key):
        self.remove_tokens()
        query = "SELECT user_email FROM auth_key where auth_token = %s"
        value = (auth_key,)
        self.my_cursor.execute(query, value)
        result = self.my_cursor.fetchone()
        if result is not None:
            return result[0]
        return None


class FolderManagement:

    def __init__(self):
        self.auth_obj = AuthManagament()

    def insert_folder(self, folder_name, auth_key):
        folder_name = checking_name(folder_name)
        email_check = self.auth_obj.get_user_email_from_authkey(auth_key)
        if email_check is None:
            return -1  # authentication failure
        user_path = os.path.join(server_path, email_check)
        folder_path = os.path.join(user_path, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        else:
            return -2

    def delete_folder(self, folder_name, auth_key):
        folder_name = checking_name(folder_name)
        email_check = self.auth_obj.get_user_email_from_authkey(auth_key)
        if email_check is None:
            return -1  # authentication failure
        user_path = os.path.join(server_path, email_check)
        folder_path = os.path.join(user_path, folder_name)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
        else:
            return -2

    def get_folder(self, auth_key):
        email_check = self.auth_obj.get_user_email_from_authkey(auth_key)
        if email_check is None:
            return -1  # authentication failure
        user_path = os.path.join(server_path, email_check)
        user_folders = os.listdir(user_path)
        try:
            user_folders.remove(".DS_Store")
        except:
            pass
        return user_folders

    def update_folder(self, old_folder_name, new_folder_name, authKey):
        old_folder_name = checking_name(old_folder_name)
        new_folder_name = checking_name(new_folder_name)
        email_check = self.auth_obj.get_user_email_from_authkey(authKey)
        if email_check is None:
            return -1  # authentication failure
        user_path = os.path.join(server_path, email_check)
        folder_path = os.path.join(user_path, old_folder_name)
        replacing_path = os.path.join(user_path, new_folder_name)
        if os.path.exists(folder_path):
            if not os.path.exists(replacing_path):
                os.replace(folder_path, replacing_path)
            else:
                return -3
        else:
            return -2


class ImageManagement:

    def __init__(self):
        self.user_obj = UserManagement()
        self.auth_obj = AuthManagament()

    def insert_image(self, image, folder_name, image_name, authKey):
        print(1)
        folder_name = checking_name(folder_name)
        image_name = checking_name(image_name)
        fetching_email = self.auth_obj.get_user_email_from_authkey(authKey)
        if fetching_email is None:
            return -1  # authentication failure
        user_path = os.path.join(server_path, fetching_email)
        folder_path = os.path.join(user_path, folder_name)
        if os.path.exists(folder_path):
            os.chdir(folder_path)
            bytearr = bytearray(image.file.read())
            picture = Image.open(io.BytesIO(bytearr))
            image_size = len(bytearr)
            if not os.path.exists(image_name):
                checking_space = self.user_obj.updating_user_memory(image_size, fetching_email, 1)
            else:
                checking_space = 1
            if checking_space > 0:
                picture.save(image_name)
                return image_size
            else:
                return -3
        else:
            return -2

    def get_images_in_folder(self, authKey, folder_name):
        folder_name = checking_name(folder_name)
        email_check = self.auth_obj.get_user_email_from_authkey(authKey)
        if email_check is None:
            return -1  # authentication failure
        user_path = os.path.join(server_path, email_check)
        folder_path = os.path.join(user_path, folder_name)
        if os.path.exists(folder_path):
            user_folders = os.listdir(folder_path)
        else:
            return -2
        try:
            user_folders.remove(".DS_Store")
        except:
            pass
        return user_folders

    def delete_images_in_folder(self, authKey, folder_name, image_name):
        folder_name = checking_name(folder_name)
        image_name = checking_name(image_name)
        email_check = self.auth_obj.get_user_email_from_authkey(authKey)
        if email_check is None:
            return -1  # authentication failure
        user_path = os.path.join(server_path, email_check)
        folder_path = os.path.join(user_path, folder_name)
        image_path = os.path.join(folder_path, image_name)
        if os.path.exists(folder_path):
            if os.path.exists(image_path):
                image_size = os.stat(image_path).st_size * -1
                self.user_obj.updating_user_memory(image_size, email_check, -1)
                os.remove(image_path)
                return 1
            else:
                return -3
        else:
            return -2

    def move_image_another_folder(self, image_name, authKey, folder_name, another_folder_name):
        folder_name = checking_name(folder_name)
        another_folder_name = checking_name(another_folder_name)
        email_check = self.auth_obj.get_user_email_from_authkey(authKey)
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


class MetricsManagement:

    def __init__(self):
        self.auth_obj = AuthManagament()

    def get_size_folder(self, folder):
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

    def folder_metrics(self, authKey, folder_name):
        folder_name = checking_name(folder_name)
        email_check = self.auth_obj.get_user_email_from_authkey(authKey)
        if email_check is None:
            return -1  # authentication failure
        user_path = os.path.join(server_path, email_check)
        folder_path = os.path.join(user_path, folder_name)
        if os.path.exists(folder_path):
            folder_details = self.get_size_folder(folder_path)
            return folder_details
        else:
            return -2

    def user_metrics(self, authKey):
        email_check = self.auth_obj.get_user_email_from_authkey(authKey)
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
                folder_details = self.get_size_folder(folder_path)
                folder_details.append(folder_name)
                metrics_list.append(folder_details)
            return metrics_list
        else:
            return -2
