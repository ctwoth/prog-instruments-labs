from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, modes
from cryptography.hazmat.decrepit.ciphers.algorithms import TripleDES

import os

class TDES:
    @staticmethod
    def generate_key(key_len):
        """
        generate key with key_len bits (what means key_len//8 bytes)

        :param key_len:
        :return generated_key:
        """
        return os.urandom(key_len//8)

    @staticmethod
    def encrypt(data: bytes, key: bytes):
        """
        encrypt data with 3DES algorythm in cipher_block_chaining (CBC) mode with random initialization vector (iv)

        :param data:
        :param key:
        :return encrypted data:
        """
        iv = os.urandom(8)

        padder = padding.PKCS7(TripleDES.block_size).padder()
        padded_data = padder.update(data) + padder.finalize()

        encryptor = Cipher(TripleDES(key), modes.CBC(iv)).encryptor()
        encrypted_data = iv + encryptor.update(padded_data) + encryptor.finalize()

        return encrypted_data

    @staticmethod
    def decrypt(encrypted_data: bytes, key: bytes) -> bytes:
        """
        decrypt data with same TDES algorithm with same key

        :param encrypted_data:
        :param key:
        :return decrypted_data:
        """
        iv = encrypted_data[:8]
        encrypted_data = encrypted_data[8:]

        decryptor = Cipher(TripleDES(key), modes.CBC(iv)).decryptor()
        decrypted_text = decryptor.update(encrypted_data) + decryptor.finalize()

        unpadder = padding.PKCS7(TripleDES.block_size).unpadder()
        decrupted_data = unpadder.update(decrypted_text) + unpadder.finalize()

        return decrupted_data