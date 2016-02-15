import os
import binascii

def generate_random_token():
    token_length = 36
    return binascii.hexlify(os.urandom(token_length))