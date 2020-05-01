from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
import requests
import sys
import os

SCREEN_SIZE = [600, 450]


class MapFuncs:
    map_file = 'map.jpg'


class MapsAPI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Maps API')
        self.setFixedSize(*SCREEN_SIZE)

        self.label_map = QLabel(self)
        map_request = "https://static-maps.yandex.ru/1.x/?ll=37.620070,55.753630&size=600,450&z=13&l=sat"
        response = requests.get(map_request)
        with open(MapFuncs.map_file, "wb") as file:
            file.write(response.content)

        self.pixmap_map = QPixmap(MapFuncs.map_file)
        self.label_map.setPixmap(self.pixmap_map)
        self.label_map.resize(self.label_map.sizeHint())

    def closeEvent(self, *args, **kwargs):
        os.remove(MapFuncs.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapsAPI()
    ex.show()
    sys.exit(app.exec_())
