from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
import requests
import sys
import os

SCREEN_SIZE = [600, 450]


class StaticMap:
    map_file = 'map.jpg'
    _server = 'https://static-maps.yandex.ru/1.x/'
    __ll = [37.620070, 55.753630]
    __size = [600, 450]
    __l = 'sat'
    __z = '13'
    __pixmap = None

    def set_params(self, **params):
        pass

    def update_map(self):
        params = {
            'll': f'{self.__ll[0]},{self.__ll[1]}',
            'size': f'{self.__size[0]},{self.__size[1]}',
            'l': self.__l,
            'z': self.__z
        }
        response = requests.get(self._server, params=params)
        if not response:
            raise Exception(response.reason)

        with open(self.map_file, "wb") as file:
            file.write(response.content)
        self.__pixmap = QPixmap(self.map_file)

    def get_pixmap(self, update=False):
        if update:
            self.update_map()
        return self.__pixmap

    def get_size(self):
        return self.__size


class MapsAPI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.static_map = StaticMap()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Maps API')
        self.setFixedSize(*SCREEN_SIZE)

        self.label_map = QLabel(self)
        self.label_map.setPixmap(self.static_map.get_pixmap(update=True))
        self.label_map.resize(*self.static_map.get_size())

    def closeEvent(self, *args, **kwargs):
        os.remove(StaticMap.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapsAPI()
    ex.show()
    sys.exit(app.exec_())
