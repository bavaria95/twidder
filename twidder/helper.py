import os
import binascii

# to store tokens and corresponded emails to it
class Storage():
    def __init__(self):
        self.d = {}

    def add_user(self, token, email):
        if token in self.d:
            raise 'Token is used.'

        self.d[token] = email

    def remove_user(self, token):
        self.d.pop(token, None)

    def get_user_email(self, token):
        return self.d.get(token)

    def is_token_presented(self, token):
        return token in self.d

    def get_all_storage(self):
        return self.d

    def remove_token_by_email(self, email):
        for k,v in self.d.iteritems():
            self.d.pop(k, None) if email == v

class SocketPool():
    def __init__(self):
        self.d = {}

    def add_socket(self, sock, email):
        self.d[email] = sock

    def get_socket(self, email):
        return self.d.get(email, None)

    def is_socket_presented(self, email):
        return email in self.d

    def remove_socket(self, email):
        return self.d.pop(email, None)


def generate_random_token():
    token_length = 36
    return binascii.hexlify(os.urandom(token_length))
