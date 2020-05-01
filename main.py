from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.Qt import Qt
import requests
import sys
import os

SCREEN_SIZE = [600, 450]


class StaticMapAPI:
    map_file = 'map.jpg'
    _server = 'https://static-maps.yandex.ru/1.x/'
    ll = [37.620070, 55.753630]
    size = [600, 450]
    l = 'sat'
    z = 1
    ZOOM_MAX = 20
    ZOOM_MIN = 1
    pixmap = None

    def set_params(self, **params):
        pass

    def update_map(self):
        params = {
            'll': f'{self.ll[0]},{self.ll[1]}',
            'size': f'{self.size[0]},{self.size[1]}',
            'l': self.l,
            'z': self.z
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
        return self.size

    def zoom_in(self, step):
        self.z += step
        if self.z > self.ZOOM_MAX:
            self.z = self.ZOOM_MAX

    def zoom_out(self, step):
        self.z -= step
        if self.z < self.ZOOM_MIN:
            self.z = self.ZOOM_MIN

    def move(self, x, y):
        pass


class MapsAPI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.static_map_api = StaticMapAPI()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Maps API')
        self.setFixedSize(*SCREEN_SIZE)
        self.label_map = QLabel(self)
        self.update_map()

    def update_map(self):
        self.label_map.setPixmap(self.static_map_api.get_pixmap(update=True))
        self.label_map.resize(*self.static_map_api.get_size())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.static_map_api.zoom_in(1)
        elif event.key() == Qt.Key_PageDown:
            self.static_map_api.zoom_out(1)
        elif event.key() == Qt.Key_Up:
            self.static_map_api.move(1)
        else:
            return
        self.update_map()

    def closeEvent(self, *args, **kwargs):
        os.remove(self.static_map_api.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapsAPI()
    ex.show()
    sys.exit(app.exec_())
