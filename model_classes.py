class User:
    memory = 500000

    def __init__(self, name, phone_no, user_email, user_password, country, used_memory):
        self.user_name = name
        self.phone_no = phone_no
        self.user_email = user_email
        self.user_password = user_password
        self.country = country
        self.used_memory = used_memory


class Authorization:

    def __init__(self, token, email):
        self.auth_token = token
        self.user_email = email
