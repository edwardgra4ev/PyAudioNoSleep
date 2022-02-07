import sys
import os
import time
from tkinter import CURRENT
import pyaudio
import wave
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QAction, QMenu, QSystemTrayIcon, qApp
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon
import gui
import config


audio = pyaudio.PyAudio()
All_OUTPUT_AUDIO_DEVICES = {}
All_AUDIO_FILES = {}

def get_output_audio_devices() -> None:
    """
    Получаем словарь всех устройств аудио выхода которые определены в системе как динамики.
    HostApi = 0 так как предположительно это центральный канал.
    """
    for index in range(audio.get_device_count()):
        devices = audio.get_device_info_by_index(index)
        devices_name = devices.get('name')
        if ("динамики" in devices_name.lower()) and devices.get('maxOutputChannels') > 0 and devices.get('hostApi') == 0:
            All_OUTPUT_AUDIO_DEVICES.update({devices_name: devices})

def get_audio_files() -> None:
    """
    Получить все аудио файлы
    """
    with os.scandir(path="audio") as scaner:
        for entry in scaner:
            if not entry.name.startswith('.') and entry.is_file():
                All_AUDIO_FILES.update({entry.name: entry.path})


class App(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.config = config.Config()
        self.read_config()
        self.set_output_devices()
        self.set_audio_files()
        self.set_second()
        self.button_save.clicked.connect(self.save_setting)
        self.button_tray.clicked.connect(self.hide)
        
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon('icon.ico'))
        setting_action = QAction("Setting", self)
        setting_action.triggered.connect(self.show)
        quit_action = QAction("Exit", self)
        quit_action.triggered.connect(qApp.quit)
        tray_menu = QMenu()
        tray_menu.addAction(setting_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        self.thread = QtCore.QThread()
        self.worker = SoudPlay()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()
    
    def set_output_devices(self) -> None:
        self.output_devices.addItems(All_OUTPUT_AUDIO_DEVICES.keys())
        if self.devices in All_OUTPUT_AUDIO_DEVICES.keys():
            self.output_devices.setCurrentText(self.devices)
        

    def set_audio_files(self) -> None:
        self.output_files.addItems(All_AUDIO_FILES.keys())
        if self.file in All_AUDIO_FILES.keys():
            self.output_files.setCurrentText(self.file)
    
    def set_second(self) -> None:
        self.spin_second.setValue(int(self.second))
        
    def save_setting(self) -> None:
        self.config.write_config(
            second=str(self.spin_second.value()),
            devices=self.output_devices.currentText(),
            file=self.output_files.currentText()
        )
        self.read_config()

    
    def read_config(self) -> None:
        self.second, self.devices, self.file = self.config.read_config()

         
class SoudPlay(QtCore.QObject):
    
    def run(self) -> None:
        try:
            count = 0
            while True:
                second, devices, file = config.Config().read_config()
                if count >= int(second):
                    self.play(devices, file)
                    count = 0
                else:
                    count += 1
                    time.sleep(1)
        except AttributeError:
            time.sleep(1)
    
    def play(self, devices, file) -> None:
        chunk = 1024
        wf = wave.open(All_AUDIO_FILES.get(file), 'rb')
        stream = audio.open(format=audio.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output_device_index=All_OUTPUT_AUDIO_DEVICES.get(devices).get("index"),
                        output=True)

        data = wf.readframes(chunk)
        while data != b'':
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()
    
def main():
    app = QtWidgets.QApplication(sys.argv)
    window = App()  
    # window.show() 
    app.exec_()
  

if __name__ == '__main__':
    get_output_audio_devices()
    get_audio_files()
    main()