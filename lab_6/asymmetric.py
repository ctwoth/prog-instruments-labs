from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding

from file_utils import FileUtils


class RSA:
    @staticmethod
    def generate_keys() -> (rsa.RSAPrivateKey, rsa.RSAPublicKey):
        """
        generate rsa-key with 2048 len and default bucket

        :return private_key, public_key:
        """
        key = rsa.generate_private_key(public_exponent=65537,
                                       key_size=2048)

        return key, key.public_key()

    @staticmethod
    def encrypt(data: bytes, public_key: rsa.RSAPublicKey) -> bytes:
        """
        encrypt data with public rsa-key with using OAEP encrypting standard
        with SHA256 hash-algorithm

        :param data:
        :param public_key:
        :return encrypted_data:
        """
        return public_key.encrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None)
        )

    @staticmethod
    def decrypt(data: bytes, private_key: rsa.RSAPrivateKey) -> bytes:
        """
        decrypt encrypted with OAEP-SHA256 standart data with private rsa-key

        :param data:
        :param private_key:
        :return decrypted_data:
        """
        return private_key.decrypt(
            data,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None)
        )

    @staticmethod
    def public_key_serialization(key: rsa.RSAPublicKey, save_path: str) -> None:
        """
        return needed for serialization pyblic bytes of rsa-key

        :param key:
        :param save_path:
        :return None:
        """
        serialization_data = key.public_bytes(encoding=serialization.Encoding.PEM,
                                              format=serialization.PublicFormat.SubjectPublicKeyInfo)

        FileUtils.load_bytes_in(serialization_data, save_path)

    @staticmethod
    def private_key_serialization(key: rsa.RSAPrivateKey, save_path: str) -> None:
        """
        return needed for serialization private bytes of rsa-key

        :param key:
        :param save_path:
        :return None:
        """
        serialization_data = key.private_bytes(encoding=serialization.Encoding.PEM,
                                               format=serialization.PrivateFormat.TraditionalOpenSSL,
                                               encryption_algorithm=serialization.NoEncryption())

        FileUtils.load_bytes_in(serialization_data, save_path)
