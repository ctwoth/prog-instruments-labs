import json


class FileUtils:
    @staticmethod
    def load_in_json(path: str, data: dict) -> None:
        """
        convert dict into json data and load it into file

        :param path:
        :param data:
        :return None:
        """
        with open(path, 'w') as fp:
            json.dump(data, fp)

    @staticmethod
    def load_from_json(path: str) -> dict:
        """
        load data from json file

        :param path:
        :return dict dase on json data:
        """
        with open(path, 'r') as json_file:
            json_data = json.load(json_file)
            return json_data

    @staticmethod
    def load_from_txt(path: str, enc: str = 'utf-8')-> str:
        """
        load data of .txt file

        :param path:
        :param txt_encoding:
        :return file_data:
        """
        with open(path, 'r', encoding=enc) as file:
            data = file.read()
            return data

    @staticmethod
    def load_in_txt(data: str, path: str, enc: str = 'utf-8')-> None:
        """
        load data into .txt file

        :param data:
        :param path:
        :param txt_encoding:
        :return None:
        """
        with open(path, 'w', encoding= enc) as file:
            file.write(data)

    @staticmethod
    def load_bytes_in(data: bytes, path:str)-> None:
        """
        load bytes into file

        :param data:
        :param path:
        :return None:
        """
        with open(path, 'wb') as file:
            file.write(data)

    @staticmethod
    def load_bytes_from(path:str)-> bytes:
        """
        load bytes from file

        :param path:
        :return file_data:
        """
        with open(path, 'rb') as file:
            data = file.read()
            return data