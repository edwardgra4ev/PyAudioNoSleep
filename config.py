import configparser

class Config(object):
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.conf_file = 'config.ini'
    
    def read_config(self) -> tuple:
        self.config.read(self.conf_file, encoding="utf-8")
        second = self.config["Setting"]["second"]
        devices = self.config["Setting"]["devices"]
        file = self.config["Setting"]["file"]
        return second, devices, file
    
    def write_config(self, second: str, devices: str, file: str) -> None:
        self.config.read(self.conf_file, encoding="utf-8")
        self.config["Setting"]["second"] = second
        self.config["Setting"]["devices"] = devices
        self.config["Setting"]["file"] = file
        with open('config.ini', 'w', encoding="utf-8") as config_file:
            self.config.write(config_file)
