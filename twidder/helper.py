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


def generate_random_token():
    token_length = 36
    return binascii.hexlify(os.urandom(token_length))
