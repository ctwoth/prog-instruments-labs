import os
import sys
import time
import multiprocessing as mp
import argparse
from matplotlib import pyplot as plt
from PyQt6.QtWidgets import QApplication, QTextEdit, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QLineEdit
import json
import hashlib
import random
from collections import Counter

class card_manager:
    @staticmethod
    def generate_valid_card(card_type):
# Выбираем BIN для типа карты
        bins = {'visa': ['4'], 'mastercard': ['51', '52', '53', '54', '55', '2221', '2720'], 'amex': ['34', '37'],'mir': ['2200', '2204']}
        bin_prefix = random.choice(bins.get(card_type, ['4']))
# Генерируем остальные цифры (кроме последней - контрольной)
        length = 16 if card_type != 'amex' else 15
        digits = [int(d) for d in bin_prefix]
        digits.extend([random.randint(0, 9) for _ in range(length - len(digits) - 1)])
# Вычисляем контрольную цифру по алгоритму Луна
        check_digit = card_manager.calculate_luhn_check_digit(digits)
        digits.append(check_digit)

        return ''.join(map(str, digits))
    @staticmethod
    def calculate_luhn_check_digit(digits) :
        total = 0
        for i, digit in enumerate(reversed(digits)):
            if i % 2 == 0:
                doubled = digit * 2
                total += doubled if doubled < 10 else doubled - 9
            else:
                total += digit
        return (10 - (total % 10)) % 10

    @staticmethod
    def generate_bulk_with_statistics(self, count = 100):
        cards = []
        first_digit_stats = Counter()

        for _ in range(count):
            card_type = random.choice(list(self.bins.keys()))
            card = self.generate_valid_card(card_type)
            cards.append(card)
            first_digit_stats[card[0]] += 1

# Проверка закона Бенфорда для первых цифр
        benford_law = {str(i): round(count * (0.301 if i == 1 else
                                              0.176 if i == 2 else
                                              0.125 if i == 3 else
                                              0.097 if i == 4 else
                                              0.079 if i == 5 else
                                              0.067 if i == 6 else
                                              0.058 if i == 7 else
                                              0.051 if i == 8 else 0.046), 2) for i in range(1, 10)}

        return { 'cards': cards, 'first_digit_distribution': dict(first_digit_stats), 'benford_expected': benford_law, 'anomaly_score': self.calculate_anomaly_score(first_digit_stats, count)}

    @staticmethod
    def calculate_anomaly_score(self, stats, total):
#Реальная статистика первых цифр карт (примерная)
        expected_ratios = {'4': 0.4,  #Visa
                           '5': 0.3,  #Mastercard
                           '3': 0.15,  #Amex
                           '2': 0.1,  #Мир и другие
                           '6': 0.05  #Discover и др.
        }
        score = 0
        for digit, expected_ratio in expected_ratios.items():
            actual_ratio = stats.get(digit, 0) / total
            score += abs(actual_ratio - expected_ratio)

        return round(score, 4)

    @staticmethod
    def alg_luhn(num_str):
        total = 0

        for i, digit in enumerate(reversed(num_str)):
            num = int(digit)
            if i % 2 == 1:
                num *= 2
                if num > 9:
                    num = (num // 10) + (num % 10)

            total += num

        return total % 10 == 0

    @staticmethod
    def hashing_card(num):
        return hashlib.sha224(num.encode()).hexdigest()
    @staticmethod
    def find_card_from_hash(bins, last_nums, target_hash, free_cores = mp.cpu_count()):
        num_range = 10**(16 - 6 - len(last_nums))
        core_range = num_range // free_cores

        with mp.Pool(processes=free_cores) as p:
            results = []

            for card_bin in bins:
                for iteration in range(free_cores):
                    start = core_range * iteration
                    end = core_range * (iteration + 1) if iteration != free_cores - 1 else num_range

                    results.append(p.apply_async(
                        card_manager.hash_search,
                        (card_bin, last_nums, start, end, target_hash)
                        )
                    )

            for i in range(len(results)):
                r = results[i].get()
                if r:
                    p.terminate()
                    return r

        return None
    @staticmethod
    def hash_search(card_bin, last_nums, start, end, target_hash):
        for middle_nums in range(start, end):
            card = f"{card_bin}{middle_nums}{last_nums}"

            rand_hash = card_bin.hashing_card(card)

            if rand_hash == target_hash:
                return card

        return None

class file_utils:
    @staticmethod
    def load_in_json(path, data):
        with open(path, 'w') as json_file:
            json.dump(data, json_file)
    @staticmethod
    def load_from_json(path):
        with open(path, 'r') as json_file:
            json_data = json.load(json_file)
            return json_data
    @staticmethod
    def load_from_txt(path, enc = 'utf-8'):
        with open(path, 'r', encoding=enc) as file:
            data = file.read()
            return data
    @staticmethod
    def load_in_txt(data, path, enc = 'utf-8'):
        with open(path, 'w', encoding= enc) as file:
            file.write(data)

class Graph:
    @staticmethod
    def draw_plot(data):
        fig = plt.figure(figsize=(30, 5))
        x = [x[0] for x in data]
        y = [x[1] for x in data]

        plt.ylabel('время')
        plt.xlabel('кол-во процессов')
        plt.title('зависимость времени от числа процессов')

        plt.plot(x,y, color='navy', linestyle='--', marker='x', linewidth=1, markersize=4)
        plt.show()
    @staticmethod
    def draw_bar(data):
        fig = plt.figure(figsize=(30, 5))
        x = [x[0] for x in data]
        y = [x[1] for x in data]

        plt.ylabel('время')
        plt.xlabel('кол-во процессов')
        plt.title('зависимость времени от числа процессов')

        plt.bar(x, y, color='blue', width=0.5)
        plt.show()

class Parser:
    @staticmethod
    def validate_args(args):
        if not os.path.isfile(args.settings):
            raise ValueError("setting file not exist")
    @staticmethod
    def parse():
        parser = argparse.ArgumentParser(description="program work settings")

        parser.add_argument("-s", "--settings",type=str, default="settings.json", help="Path to settings in JSON-file")

        args = parser.parse_args()
        Parser.validate_args(args)

        return args

def check_sets(sets) -> None:
    if not os.path.isfile(sets["save_path"]):
        raise ValueError("Wrong path to initial file")
    if len(sets["last_numbers"]) != 4:
        raise ValueError("not 4 numbers")
    if len(sets["hash"]) < 10:
        raise ValueError("Hash doesn't look correct...")
    if len(sets["bins"])  == 0:
        raise ValueError("Empty bank BINs")


class MainWindow(QMainWindow):
    def __init__(self, sets_path: str):
        super().__init__()
        self.sets = file_utils.load_from_json(sets_path)
        check_sets(self.sets)
        self.setWindowTitle("Карточный дешифратор")
        self.setFixedWidth(600)

    #labels
        self.enc_params_label = QLabel("Данные дешифровки:")
        self.card_num_label = QLabel("Номер карточки:")
        self.result_label = QLabel("Результат:")

    #text widgets
        self.enc_params = QTextEdit()
        self.enc_params.setText(file_utils.load_from_txt(sets_path))
        self.enc_params.setReadOnly(True)
        self.result = QTextEdit()
        self.result.setReadOnly(True)
        self.card_num_edit = QLineEdit()

    #buttons
        self.decode_button = QPushButton("найти номер карты")
        self.decode_button.clicked.connect(self.decode)
        self.stat_decode_button = QPushButton("статистика декодирования")
        self.stat_decode_button.clicked.connect(self.stat_decode)
        self.check_button = QPushButton("проверить карту на корректность")
        self.check_button.clicked.connect(self.card_num_check)
        self.generate_button = QPushButton("сгенерировать номер карты")
        self.generate_button.clicked.connect(self.visa_card_gen)

    #construct all widgets into app
        layout = QVBoxLayout()
        layout.addWidget(self.enc_params_label)
        layout.addWidget(self.enc_params)
        layout.addWidget(self.card_num_label)
        layout.addWidget(self.card_num_edit)
        layout.addWidget(self.result_label)
        layout.addWidget(self.result)
        layout.addWidget(self.decode_button)
        layout.addWidget(self.stat_decode_button)
        layout.addWidget(self.check_button)
        layout.addWidget(self.generate_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def visa_card_gen(self):
        card_num = card_manager.generate_valid_card('visa')

        self.card_num_edit.setText(card_num)
        return

    def decode(self):
        number = card_manager.find_card_from_hash(self.sets['bins'], self.sets['last_numbers'], self.sets['hash'])

        if number:
            self.result.setText(number)
            file_utils.load_in_txt(number, self.sets['save_path'])
        else:
            self.result.setText("Не удалось найти карту")

    def stat_decode(self):
        statistic = []

        for cores in range(1, int(1.5*mp.cpu_count())):
            start = time.time()
            card_manager.find_card_from_hash(self.sets['bins'], self.sets['last_numbers'], self.sets['hash'], cores)
            work_time = time.time() - start

            statistic.append((cores, work_time))
        Graph.draw_plot(statistic)
        Graph.draw_bar(statistic)

    def card_num_check(self):
        card_num = self.card_num_edit.text()

        if not card_num.isdigit() or len(card_num) != 16:
            self.result.setText("Некорректный номер карты")
            return

        if card_manager.alg_luhn(card_num):
            self.result.setText("Карта валидна")
        else:
            self.result.setText("Карта невалидна")

def main():
    try:
        args = Parser.parse()

        app = QApplication(sys.argv)
        window = MainWindow(args.settings)
        window.show()
        sys.exit(app.exec())

    except Exception as error:
        print("Error!\n\t", error)

if __name__ == '__main__':
    main()
