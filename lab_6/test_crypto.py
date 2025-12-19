import pytest
import os
import tempfile
import json
from unittest.mock import patch, Mock, MagicMock
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric import rsa

# Импорт тестируемых модулей
from symmetric import TDES
from asymmetric import RSA
from file_utils import FileUtils
from cryptoSystem import CryptoSystem


# ============ ПРОСТЫЕ ТЕСТЫ (5 штук) ============

class TestTDESSimple:
    """Простые тесты для шифрования TripleDES"""
    def test_tdes_generate_key_correct_length(self):
        """Тест 1: Генерация ключа корректной длины"""
        # Arrange
        test_cases = [64, 128, 192]  # Разные длины ключей для 3DES

        for key_len in test_cases:
            # Act
            key = TDES.generate_key(key_len)

            # Assert
            expected_bytes = key_len // 8
            assert len(key) == expected_bytes, f"Для key_len={key_len} ожидалось {expected_bytes} байт, получено {len(key)}"

    def test_tdes_encrypt_decrypt_basic(self):
        """Тест 2: Шифрование и дешифрование возвращают исходные данные"""
        test_data = b"Naruto eto kruto."
        key = TDES.generate_key(192)  # 192 бит = 24 байта для 3DES

        encrypted = TDES.encrypt(test_data, key)
        decrypted = TDES.decrypt(encrypted, key)

        assert decrypted == test_data, "Расшифрованные данные не совпадают с исходными"
        assert encrypted != test_data, "Зашифрованные данные не должны совпадать с исходными"
        assert len(encrypted) > len(test_data), "Зашифрованные данные должны быть длиннее из-за padding и IV"


class TestRSASimple:
    """Простые тесты для асимметричного шифрования RSA"""
    def test_rsa_generate_keys_valid_pair(self):
        """Тест 3: Генерация корректной пары RSA ключей"""
        private_key, public_key = RSA.generate_keys()

        assert isinstance(private_key, rsa.RSAPrivateKey)
        assert isinstance(public_key, rsa.RSAPublicKey)

        # Проверяем, что публичный ключ соответствует приватному
        assert private_key.public_key().public_numbers() == public_key.public_numbers()

    def test_rsa_encrypt_decrypt_basic(self):
        """Тест 4: RSA шифрование/дешифрование короткого сообщения"""
        test_data = b"Cod ot seifa: 1324"
        private_key, public_key = RSA.generate_keys()

        encrypted = RSA.encrypt(test_data, public_key)
        decrypted = RSA.decrypt(encrypted, private_key)

        assert decrypted == test_data
        assert encrypted != test_data


class TestFileUtilsSimple:
    """Простые тесты для проверки работы с файлами"""
    def test_file_utils_json_roundtrip(self, tmp_path):
        """Тест 5: Запись и чтение JSON файла"""
        # Arrange
        test_file = tmp_path / "test.json"
        test_data = {
            "name": "Test",
            "value": 42,
            "nested": {"key": "value"},
            "list": [1, 2, 3]
        }

        # Act
        FileUtils.load_in_json(str(test_file), test_data)
        loaded_data = FileUtils.load_from_json(str(test_file))

        # Assert
        assert loaded_data == test_data
        assert test_file.exists()
        assert test_file.stat().st_size > 0


# ============ СЛОЖНЫЕ ТЕСТЫ (2 штуки) ============

class TestTDESAdvanced:
    """Продвинутые тесты для TDES с параметризацией"""

    @pytest.mark.parametrize("test_data, key_length", [
        # (данные, длина ключа)
        (b"", 192),  # Пустые данные
        (b"A", 192),  # Один байт
        (b"12345678", 192),  # Ровно один блок (8 байт)
        (b"Vsem privet segodnya mi budem pisati unit-testi dlya shifrov RSA i TripleDES.", 192),  # Длинный текст
        (b"\x00\x01\x02\x03\x04\x05", 192),  # Бинарные данные
        (b"A" * 1000, 192),  # 1000 одинаковых байт
        (b"", 128),  # Пустые данные с другим ключом
        (b"Test", 64),  # Короткий ключ
    ])
    def test_tdes_encrypt_decrypt_parametrized(self, test_data, key_length):
        """Тест 6: Параметризованный тест TDES с разными входными данными"""
        key = TDES.generate_key(key_length)

        encrypted = TDES.encrypt(test_data, key)
        decrypted = TDES.decrypt(encrypted, key)

        assert decrypted == test_data, f"Не удалось корректно расшифровать данные для ключа длиной {key_length}"

        # Дополнительные проверки
        assert len(encrypted) >= len(test_data), "Зашифрованные данные должны быть не короче исходных"

        # Проверяем, что зашифрованные данные начинаются с инициализирующего вектора (8 байт)
        assert len(encrypted) >= 8, "Зашифрованные данные должны содержать IV"


class TestCryptoSystemAdvanced:
    """Продвинутые тесты для CryptoSystem с использованием Mock"""
    @patch('cryptoSystem.RSA.generate_keys')
    @patch('cryptoSystem.TDES.generate_key')
    @patch('cryptoSystem.RSA.encrypt')
    @patch('cryptoSystem.FileUtils.load_bytes_in')
    def test_crypto_system_generate_keys_with_mocks(
            self,
            mock_load_bytes_in,
            mock_rsa_encrypt,
            mock_tdes_generate_key,
            mock_rsa_generate_keys
    ):
        """Тест 7: Mock-тест для проверки взаимодействий в CryptoSystem.generate_keys"""
        # Arrange
        # Создаем mock-объекты
        mock_private_key = Mock()
        mock_public_key = Mock()
        mock_rsa_generate_keys.return_value = (mock_private_key, mock_public_key)

        mock_sym_key = b"fake_symmetric_key_24_bytes!!"
        mock_tdes_generate_key.return_value = mock_sym_key

        mock_encrypted_key = b"fake_encrypted_symmetric_key"
        mock_rsa_encrypt.return_value = mock_encrypted_key

        test_key_len = 192
        test_symm_path = "/fake/path/symm.key"
        test_public_path = "/fake/path/public.pem"
        test_private_path = "/fake/path/private.pem"

        # Act
        CryptoSystem.generate_keys(
            test_key_len,
            test_symm_path,
            test_public_path,
            test_private_path
        )

        # 1. Проверяем, что RSA.generate_keys был вызван 1 раз без аргументов
        mock_rsa_generate_keys.assert_called_once()

        # 2. Проверяем, что TDES.generate_key был вызван 1 раз с правильным key_len
        mock_tdes_generate_key.assert_called_once_with(test_key_len)

        # 3. Проверяем, что RSA.encrypt был вызван 1 раз с правильными аргументами
        mock_rsa_encrypt.assert_called_once_with(mock_sym_key, mock_public_key)

        # 4. Проверяем, что FileUtils.load_bytes_in был вызван 3 раза
        assert mock_load_bytes_in.call_count == 3, f"Ожидалось 3 вызова load_bytes_in, получено {mock_load_bytes_in.call_count}"

        # 5. Проверяем аргументы каждого вызова load_bytes_in
        calls = mock_load_bytes_in.call_args_list

        # Первый вызов: сохранение публичного ключа
        assert calls[0][0][1] == test_public_path

        # Второй вызов: сохранение приватного ключа
        assert calls[1][0][1] == test_private_path

        # Третий вызов: сохранение зашифрованного симметричного ключа
        assert calls[2][0][0] == mock_encrypted_key
        assert calls[2][0][1] == test_symm_path

        # 6. Проверяем, что сериализация ключей была вызвана
        mock_public_key.public_bytes.assert_called() if hasattr(mock_public_key, 'public_bytes') else None
        mock_private_key.private_bytes.assert_called() if hasattr(mock_private_key, 'private_bytes') else None

def test_crypto_system_full_integration(tmp_path):
    """Тест полной интеграции всех компонентов CryptoSystem"""
    # Arrange
    # Создаем временные файлы
    symm_path = tmp_path / "symm.key"
    public_path = tmp_path / "public.pem"
    private_path = tmp_path / "private.pem"
    original_text_path = tmp_path / "original.txt"
    encrypted_path = tmp_path / "encrypted.bin"
    decrypted_path = tmp_path / "decrypted.txt"

    original_text = "В кинотеатре было 456 мест. Наркоман выкупил половину - теперь он может сесть по 228."

    # Записываем оригинальный текст в файл
    with open(original_text_path, 'w', encoding='utf-8') as f:
        f.write(original_text)

    # Act
    # 1. Генерируем ключи
    CryptoSystem.generate_keys(
        key_len=192,
        symm_path=str(symm_path),
        public_path=str(public_path),
        private_path=str(private_path)
    )

    # 2. Шифруем текст
    CryptoSystem.encryption(
        text_path=str(original_text_path),
        symm_key_path=str(symm_path),
        private_key_path=str(private_path),
        save_path=str(encrypted_path)
    )

    # 3. Расшифровываем текст
    CryptoSystem.decryption(
        text_path=str(encrypted_path),
        symm_key_path=str(symm_path),
        private_key_path=str(private_path),
        save_path=str(decrypted_path)
    )


    # Читаем расшифрованный текст и проверяем
    with open(decrypted_path, 'r', encoding='utf-8') as f:
        decrypted_text = f.read()

    assert decrypted_text == original_text
    assert os.path.getsize(symm_path) > 0
    assert os.path.getsize(public_path) > 0
    assert os.path.getsize(private_path) > 0
    assert os.path.getsize(encrypted_path) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])