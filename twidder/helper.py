import os
import binascii
import json
import database_helper
import random

from flask_sockets import Sockets

# generator
g = 3
# divider
p = 17


# implementing Diffie–Hellman key exchange
def compute_public_key():
    y = random.randrange(100, 500)

    public_key = g**y % p

    return {'public_key': public_key, 'secret_variable': y}

def compute_secret_key(client_public, y):
    return client_public**y % p
    

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

    def get_token_by_email(self, email):
        res = []
        for k,v in self.d.iteritems():
            if v == email:
                res.append(k)
        return res

    def remove_token_by_email(self, email):
        for k,v in list(self.d.iteritems())[:]:
            if email == v:
                self.d.pop(k, None)


class SocketPool():
    def __init__(self):
        self.d = {}

    def add_socket(self, email, sock):
        self.d[email] = sock

    def get_socket(self, email):
        return self.d.get(email, None)

    def is_socket_presented(self, email):
        return email in self.d

    def remove_socket(self, email):
        return self.d.pop(email, None)

    def get_all_sockets(self):
        return self.d

    def size(self):
        return len(self.d)

    def change_socket_by_email(self, email, sock):
        self.d[email] = sock


class StatsInfo():
    def __init__(self):
        self.d = {}

    def add_entry(self, token, sock):
        self.d[token] = {'socket': sock, 'prev': {'all_users': None,
                                                  'online': None,
                                                  'posts': None,
                                                  'all_posts': None}}
    
    def is_entry_presented(self, token):
        return token in self.d

    def get_entry(self, token):
        return self.d.get(token, None)

    def remove_entry(self, token):
        return self.d.pop(token)

    def get_all_entries(self):
        return self.d

    def notify_by_token(self, token, data):
        '''
        Also takes care about necessity of notifying
        (sends nothing if nothing changed)
        '''

        if not token in self.d:
            return

        if self.d[token]['prev'] != data:
            try:
                self.d[token]['socket'].send(json.dumps(data))
                self.d[token]['prev'] = data
            except:
                pass

    def all_subscribers(self):
        return self.d.keys()


def generate_random_token():
    token_length = 36
    return binascii.hexlify(os.urandom(token_length))
