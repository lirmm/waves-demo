"""
Encryption for Service Adaptors init_params values
"""
from __future__ import unicode_literals
from django.conf import settings
from Crypto.Cipher import XOR
import base64


class EncryptedValue(object):
    """ Encrypt values based on Django settings secret key substring """
    def __init__(self):
        raise RuntimeError('This class is intended to be used statically')

    @staticmethod
    def encrypt(to_encode, secret=settings.SECRET_KEY[0:32]):
        """ Crypt 'to_encode'
        :param secret: secret key use to encode/decode values
        :param to_encode: value to encode
        :return: base64 based encoded string
        """
        cipher = XOR.new(secret)
        encoded = base64.b64encode(cipher.encrypt(to_encode))
        return encoded

    @staticmethod
    def decrypt(to_decode, secret=settings.SECRET_KEY[0:32]):
        """ Decrypt previously encoded 'to_decode'
        :param secret: secret key used to encode/decode values
        :param to_decode: value to decode
        :return: string initial value
        """
        cipher = XOR.new(secret)
        return cipher.decrypt(base64.b64decode(to_decode))
