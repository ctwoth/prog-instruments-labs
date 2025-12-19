from cryptography.hazmat.primitives.serialization import load_pem_private_key

from symmetric import TDES
from asymmetric import RSA
from file_utils import FileUtils


class CryptoSystem:
    @staticmethod
    def generate_keys(key_len: int, symm_path: str, public_path: str, private_path: str) -> None:
        """
        generate rsa_key, generate symmetric_key with lenght = key_len, and encrypt with rsa symmetric_key.
        Then save rsa_key-public part, sra_key-private part and rsa-encrypted_symmetric_key.

        :param key_len:
        :param symmetric_key_path:
        :param public_path:
        :param private_path:
        :return None:
        """
        private_key, public_key = RSA.generate_keys()
        sym_key =                 TDES.generate_key(key_len)

        RSA.public_key_serialization(public_key, public_path)
        RSA.private_key_serialization(private_key, private_path)

        encr_sym_key = RSA.encrypt(sym_key, public_key)

        FileUtils.load_bytes_in(encr_sym_key, symm_path)

    @staticmethod
    def encryption(text_path: str, symm_key_path: str, private_key_path: str, save_path: str) -> None:
        """
        decrypt with private_rsa_key symmetric_key, then encrypt text with TDES. save result in file

        :param text_path:
        :param symm_key_path:
        :param private_key_path:
        :param save_path:
        :return None:
        """
        encrypted_symm_key = FileUtils.load_bytes_from(symm_key_path)
        private_key =        load_pem_private_key(FileUtils.load_bytes_from(private_key_path),None)
        text =               FileUtils.load_from_txt(text_path)

        symmetric_key = RSA.decrypt(encrypted_symm_key, private_key)

        encrypted_text = TDES.encrypt(text.encode('utf-8'), symmetric_key)
        FileUtils.load_bytes_in(encrypted_text, save_path)

    @staticmethod
    def decryption(text_path: str, symm_key_path: str, private_key_path: str, save_path: str) -> None:
        """
        decrypt with private_rsa_key symmetric_key, then decrypt text with TDES. save result in file

        :param text_path:
        :param symmetric_key_path:
        :param private_key_path:
        :param save_path:
        :return None:
        """
        encrypted_symm_key = FileUtils.load_bytes_from(symm_key_path)
        private_key =        load_pem_private_key(FileUtils.load_bytes_from(private_key_path),None)
        text =               FileUtils.load_bytes_from(text_path)

        symmetric_key = RSA.decrypt(encrypted_symm_key, private_key)

        decrypted_text = TDES.decrypt(text, symmetric_key)
        FileUtils.load_in_txt(decrypted_text.decode('utf-8'), save_path)