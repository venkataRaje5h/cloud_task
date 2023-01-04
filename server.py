import cherrypy
import json
import os
from model import DataBase


def bad_request():
    output = {
        "status": "error",
        "code": "INVALID_REQUEST",
        "message": "invalid request body"
    }
    cherrypy.response.status = 400
    return output


def authorizing():
    output = {
        "status": "error",
        "code": "UNAUTHENTICATED",
        "message": "invalid user credentials"
    }
    cherrypy.response.status = 401
    return output


def authorizing_failed():
    output = {
        "status": "error",
        "code": "UNAUTHENTICATED",
        "message": "authentication failure"
    }
    cherrypy.response.status = 401
    return output


def user_not_found():
    output = {
        "status": "error",
        "code": "USER_NOT_FOUND",
        "message": "user not found"
    }
    cherrypy.response.status = 404
    return output


def internal_server_error():
    output = {
        "status": "failure",
        "code": "INTERNAL_SERVER_FAILURE",
        "message": "internal server failure"
    }
    cherrypy.response.status = 500
    return output


def folder_already_exist():
    output = {
        "status": "error",
        "code": "INVALID_REQUEST",
        "message": "folder already exists"
    }
    cherrypy.response.status = 404
    return output


def folder_does_not_exist():
    output = {
        "status": "error",
        "code": "INVALID_REQUEST",
        "message": "folder does not exists"
    }
    cherrypy.response.status = 404
    return output


class users_controller:

    @cherrypy.expose
    def index(self):
        return """
                Welcome to Cloud App
                !!User URLs!!
                Create - https://localhost:8443/cloud/users/sign_up
                Login  - https://localhost:8443/cloud/users/login
                Delete - https://localhost:8443/cloud/users/delete
                Update - https://localhost:8443/cloud/users/update
                !!Folder URLs!!
                [Create,GET,Delete,Update] - https://localhost:8443/cloud/application/folder
                !!Image URLs!!
                [Create,GET,Delete,Update]- https://localhost:8443/cloud/application/{folder_name}/images
                """

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def sign_up(self, user_name=None, phone_number=None, email=None, country=None, password=None):
        if user_name is None or phone_number is None or email is None or country is None or password is None or cherrypy.request.method != 'POST':
            return bad_request()
        try:
            result = DataBase.insert_user(user_name=user_name, phone_number=phone_number, user_email=email,
                                          country=country,
                                          password=password)
            if result == -1:
                output = {
                    "status": "error",
                    "code": "USER_ALREADY_EXISTS",
                    "message": "email already exists"
                }
                return output
            elif result == -2:
                return internal_server_error()
            cherrypy.response.status = 201
        except:
            return internal_server_error()

    @cherrypy.tools.json_out()
    @cherrypy.expose
    def login(self, email, password):
        if email is None or password is None or cherrypy.request.method != 'POST':
            return bad_request()
        try:
            user = DataBase.get_User(email)
            if user is None:
                return user_not_found()
            if user.user_password == password:
                auth_token, expiry_time = DataBase.generate_token(email)
                output = {
                    "status": "success",
                    "code": "SUCCESS",
                    "response": {
                        "user_name": user.user_name,
                        "user_mail": email,
                        "auth_token": auth_token,
                        "expiry_time": expiry_time
                    }
                }
                cherrypy.response.status = 200
                return output
            else:
                return authorizing()
        except:
            return internal_server_error()

    @cherrypy.expose
    def delete(self, email, password):
        if email is None or password is None or cherrypy.request.method != 'DELETE':
            return bad_request()
        try:
            user = DataBase.get_User(email)
            if user is None:
                return user_not_found()
            if user.user_password == password:
                DataBase.delete_user(email, password)
                cherrypy.response.status = 204
            else:
                return authorizing()
        except:
            return internal_server_error()

    @cherrypy.expose
    def update(self, email, password, user_name, phone_number):
        if user_name is None or phone_number is None or email is None or password is None or cherrypy.request.method != 'PUT':
            return bad_request()
        try:
            user = DataBase.get_User(email)
            if user is None:
                return user_not_found()
            if user.user_password == password:
                DataBase.update_user(email=email, password=password, user_name=user_name, phone_num=phone_number)
                cherrypy.response.status = 204
            else:
                return authorizing()
        except:
            return internal_server_error()


@cherrypy.expose
class Folder(object):

    @cherrypy.tools.json_out()
    def POST(self, authKey=None, folder_name=None):
        if authKey is None or folder_name is None:
            return bad_request()
        try:
            db_output = DataBase.insert_folder(auth_key=authKey, folder_name=folder_name)
            if db_output == -1:
                return authorizing_failed()
            elif db_output == -2:
                return folder_already_exist()
            return {
                "status": "success",
                "code": "SUCCESS",
                "response": {
                    "folder_name": folder_name
                }
            }
        except:
            internal_server_error()

    @cherrypy.tools.json_out()
    def DELETE(self, authKey=None, folder_name=None):
        if authKey is None or folder_name is None:
            return bad_request()
        try:
            db_output = DataBase.delete_folder(auth_key=authKey, folder_name=folder_name)
            if db_output == -1:
                return authorizing_failed()
            elif db_output == -2:
                return folder_does_not_exist()
            cherrypy.response.status = 204
        except:
            internal_server_error()

    @cherrypy.tools.json_out()
    def GET(self, authKey=None):
        if authKey is None:
            return bad_request()
        try:
            output = DataBase.get_folder(auth_key=authKey)
            if output == -1:
                return authorizing_failed()
            return {
                "status": "success",
                "code": "SUCCESS",
                "message": {
                    "folders_list": output
                }
            }
        except:
            internal_server_error()

    @cherrypy.tools.json_out()
    def PUT(self, authKey=None, folder_name=None, new_folder_name=None):
        if authKey is None or folder_name is None or new_folder_name is None:
            return bad_request()
        try:
            db_output = DataBase.update_folder(auth_key=authKey, old_folder_name=folder_name,
                                               new_folder_name=new_folder_name)
            if db_output == -1:
                return authorizing_failed()
            elif db_output == -2:
                return folder_already_exist()
            cherrypy.response.status = 204
        except:
            internal_server_error()


class Image(object):
    @cherrypy.tools.json_out()
    def insert_image(self, image=None, authKey=None, folder_name=None):
        if image is None or authKey is None or folder_name is None:
            return bad_request()
        try:
            image_size = len(image.file.read())
            output = DataBase.insert_image(image, folder_name, image.filename, authKey, image_size)
            if output == -1:
                return authorizing_failed()
            elif output == -2:
                return folder_does_not_exist()
            elif output == -3:
                return {
                    "status": "error",
                    "code": "INVALID_REQUEST",
                    "message": "run out of memory"
                }
            cherrypy.response.status = 200
            return {
                "status": "success",
                "code": "SUCCESS",
                "response": {
                    "image_name": image.filename,
                    "image_size": image_size
                }
            }
        except:
            return internal_server_error()

    @cherrypy.tools.json_out()
    def get_images(self, authKey, folder_name):
        if authKey is None or folder_name is None:
            return bad_request()
        try:
            output = DataBase.get_images_in_folder(authKey, folder_name,)
            if output == -1:
                return authorizing_failed()
            elif output == -2:
                return folder_does_not_exist()
            cherrypy.response.status = 200
            return {
                "status": "success",
                "code": "SUCCESS",
                "response": {
                    "images_list": output
                }
            }
        except:
            return internal_server_error()

    @cherrypy.tools.json_out()
    def delete_image(self, authKey, folder_name, image_name):
        if authKey is None or folder_name is None or image_name is None:
            return bad_request()
        try:
            output = DataBase.delete_images_in_folder(authKey, folder_name, image_name)
            if output == -1:
                return authorizing_failed()
            elif output == -2:
                return folder_does_not_exist()
            elif output == -3:
                cherrypy.response.status = 404
                return {
                    "status": "error",
                    "code": "INVALID_REQUEST",
                    "message": f"image-{image_name} does not exists"
                }
            cherrypy.response.status = 204
        except:
            return internal_server_error()

    @cherrypy.tools.json_out()
    def change_location(self, image_name, authKey, folder_name, another_folder_name):
        if authKey is None or folder_name is None or image_name is None:
            return bad_request()
        try:
            output = DataBase.move_image_another_folder(image_name, authKey, folder_name, another_folder_name)
            if output == -1:
                return authorizing_failed()
            elif output == -2:
                return folder_does_not_exist()
            elif output == -3:
                cherrypy.response.status = 404
                return {
                    "status": "error",
                    "code": "INVALID_REQUEST",
                    "message": f"image- '{image_name}' does not exists"
                }
            elif output == -4:
                cherrypy.response.status = 404
                return {
                    "status": "error",
                    "code": "INVALID_REQUEST",
                    "message": f"folder- '{another_folder_name}' does not exists"
                }
            cherrypy.response.status = 204
        except:
            return internal_server_error()


class Metrics:

    @cherrypy.tools.json_out()
    def folder_metrics_operations(self, authKey, folder_name):
        if authKey is None or folder_name is None:
            return bad_request()
        try:
            output = DataBase.folder_metrics(authKey, folder_name)
            if output == -1:
                return authorizing_failed()
            elif output == -2:
                return folder_does_not_exist()
            cherrypy.response.status = 200
            return {
                "status": "success",
                "code": "SUCCESS",
                "response": {
                    "image_count": output[1],
                    "folder_size": output[0]
                }
            }
        except:
            return internal_server_error()

    @cherrypy.tools.json_out()
    def user_metrics_operations(self, authKey):
        if authKey is None :
            return bad_request()
        try:
            output = DataBase.user_metrics(authKey)
            if output == -1:
                return authorizing_failed()
            elif output == -2:
                return folder_does_not_exist()
            json_list = []
            total_count = 0
            total_size = 0
            for item in output:
                total_size += item[0]
                total_count += item[1]
                folder_details = {
                    "folder_name": item[2],
                    "folder_image_count": item[1],
                    "folder_size": item[0]
                }
                json_list.append(folder_details)

            cherrypy.response.status = 200
            return {
                "status": "success",
                "code": "SUCCESS",
                "response": {
                    "total_image_count": total_count,
                    "total_size_occupied": total_size,
                    "folder_details":  [name for name in json_list]
                }
            }
        except:
            return internal_server_error()


def jsonify_error(status, message, traceback, version):
    cherrypy.response.headers['Content-Type'] = 'application/json'
    response_body = json.dumps(
        {
            'error': {
                'http_status': status,
                'message': message,
            }
        })
    cherrypy.response.status = status
    return response_body


if __name__ == "__main__":
    cherrypy.config.update({
        "server.socket_host": "localhost",
        "server.socket_port": 8443,
        'error_page.default': jsonify_error,
    })

    conf = {
        '/cloud/application/folder': {
            'tools.sessions.on': True,
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
        },
    }

    start = users_controller()
    start.cloud = users_controller()
    start.cloud.users = users_controller()
    start.cloud.users.sign_up = users_controller().sign_up
    start.cloud.users.login = users_controller().login
    start.cloud.users.delete = users_controller().delete
    start.cloud.users.update = users_controller().update
    start.cloud.application = Folder()
    start.cloud.application.folder = Folder()
    dispatcher = cherrypy.dispatch.RoutesDispatcher()

    # insert image
    dispatcher.connect(name='',
                       route='/cloud/application/{folder_name}/images',
                       action='insert_image',
                       controller=Image(),
                       conditions={'method': ['POST']})
    # get image
    dispatcher.connect(name='',
                       route='/cloud/application/{folder_name}/images',
                       action='get_images',
                       controller=Image(),
                       conditions={'method': ['GET']})

    # delete image
    dispatcher.connect(name='',
                       route='/cloud/application/{folder_name}/images',
                       action='delete_image',
                       controller=Image(),
                       conditions={'method': ['DELETE']})
    # put image
    dispatcher.connect(name='',
                       route='/cloud/application/{folder_name}/images',
                       action='change_location',
                       controller=Image(),
                       conditions={'method': ['PUT']})

    # # metrics_folder
    # dispatcher.connect(name='',
    #                    route='/cloud/application/{folder_name}/metrics',
    #                    action='folder_metrics_operations',
    #                    controller=Metrics(),
    #                    conditions={'method': ['GET']})
    # # metrics user
    # dispatcher.connect(name='',
    #                    route='/cloud/application/usage/metrics',
    #                    action='user_metrics_operations',
    #                    controller=Metrics(),
    #                    conditions={'method': ['GET']})

    config = {
        '/': {
            'request.dispatch': dispatcher,
            'error_page.default': jsonify_error,
            'cors.expose.on': True,
        },
    }

    cherrypy.tree.mount(root=None, config=config)
    # cherrypy.tree.mount(start, '/', conf)

    cherrypy.engine.start()
    cherrypy.engine.block()
