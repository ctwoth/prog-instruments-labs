import re
import csv
from typing import Dict, List

from consts import *
from checksum import serialize_result, calculate_checksum

def read_csv(path: str, enc: str, delim: str) -> list[dict]:
    """
    считывание csv файла
    :param path: путь к файлу
    :param enc: кодировка файла
    :param delim: разделитель строк
    :return: Лист словарей формата 'тип_данных': 'значение'
    """
    with open(path, 'r', encoding=enc) as f:
        data = csv.DictReader(f, delimiter=delim)
        return list(data)


def is_valid_row(row: dict, i: int) -> bool:
    """
    Проверяет строку на валидность. Т.к строка это словарь
    то достаточно пройтись по всем типам данных и проверить соответствие значений с паттернами
    :param row: словарь вида 'тип_данных': 'значение'
    :return: Валидна ли строка
    """
    for data_type in row.keys():
        if not re.fullmatch(PATTERNS[data_type], row[data_type]):
            return False
    return True

def find_invalid_rows(rows: List[dict]) -> List[int]:
    """
    среди строк ищет те, в которых есть хотя бы одно не соответствие паттерну
    :param rows: строки для поиска
    :return: массив номеров невалидных строк
    """
    invalid_rows = []

    for i, row in enumerate(rows):
        if is_valid_row(row, i): continue
        invalid_rows.append(i)
    return invalid_rows

def main() -> None:
    """
    загружает csv файла строки, находит невалидные строки и получает их контрольную сумму
    :return: None
    """
    rows = read_csv(CSV_PATH, 'utf-16', ';')
    invalid_rows = find_invalid_rows(rows)
    control_sum = calculate_checksum(invalid_rows)

    serialize_result(VARIANT, control_sum)

if __name__ == "__main__":
    main()
