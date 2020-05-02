from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.Qt import Qt
import requests
import sys
import os

SCREEN_SIZE = [600, 450]


class StaticMapAPI:
    map_file = 'map.png'
    map_file_for_sat = 'map.jpg'
    _server = 'https://static-maps.yandex.ru/1.x/'
    ll = [37.620070, 55.753630]
    size = [600, 450]
    l = 'map'
    spn = 0.002
    MAX_SPN = 65.536
    MIN_SPN = 0.001
    pixmap = None

    def set_params(self, **params):
        self.l = params.get('l', self.l)
        self.spn = params.get('spn', self.spn)
        self.size = params.get('size', self.size)
        self.ll = params.get('ll', self.ll)

    def update_map(self):
        params = {
            'll': f'{self.ll[0]},{self.ll[1]}',
            'size': f'{self.size[0]},{self.size[1]}',
            'l': self.l,
            'spn': f'{self.spn},{self.spn}'
        }
        response = requests.get(self._server, params=params)
        if not response:
            raise Exception(response.reason)

        if self.l == 'sat':
            with open(self.map_file_for_sat, "wb") as file:
                file.write(response.content)
            self.__pixmap = QPixmap(self.map_file_for_sat)
        else:
            with open(self.map_file, "wb") as file:
                file.write(response.content)
            self.__pixmap = QPixmap(self.map_file)

    def get_pixmap(self, update=False):
        if update:
            self.update_map()
        return self.__pixmap

    def get_size(self):
        return self.size

    def spn_in(self):
        self.spn /= 2
        if self.spn < self.MIN_SPN:
            self.spn = self.MIN_SPN

    def spn_out(self):
        self.spn *= 2
        if self.spn > self.MAX_SPN:
            self.spn = self.MAX_SPN

    def move(self, x=0, y=0):
        self.ll[0] += x * self.spn * 1 * 2.5
        self.ll[1] += y * self.spn * (85 / 180) * 2.5


class MapsAPI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.static_map_api = StaticMapAPI()
        self.initUI()

        self.btn_update_map.clicked.connect(self.update_map)
        # self.mode.currentTextChanged.connect(self.update_map)

    def initUI(self):
        self.setWindowTitle('Maps API')
        self.setFixedSize(*SCREEN_SIZE)
        self.label_map = QLabel(self)
        self.label_map.move(100, 0)
        self.mode = QComboBox(self)
        self.mode.addItems(['map', 'sat', 'skl'])
        self.btn_update_map = QPushButton('Обновить', self)
        self.btn_update_map.move(0, 100)
        self.update_map()

    def update_map(self):
        self.static_map_api.set_params(l=self.mode.currentText())
        self.label_map.setPixmap(self.static_map_api.get_pixmap(update=True))
        self.label_map.resize(*self.static_map_api.get_size())

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.static_map_api.spn_in()
        elif event.key() == Qt.Key_PageDown:
            self.static_map_api.spn_out()
        elif event.key() == Qt.Key_Up:
            self.static_map_api.move(x=0, y=1)
        elif event.key() == Qt.Key_Down:
            self.static_map_api.move(x=0, y=-1)
        elif event.key() == Qt.Key_Right:
            self.static_map_api.move(x=1, y=0)
        elif event.key() == Qt.Key_Left:
            self.static_map_api.move(x=-1, y=0)
        else:
            return
        self.update_map()

    def closeEvent(self, *args, **kwargs):
        if self.static_map_api.map_file in os.listdir():
            os.remove(self.static_map_api.map_file)
        if self.static_map_api.map_file_for_sat in os.listdir():
            os.remove(self.static_map_api.map_file_for_sat)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapsAPI()
    ex.show()
    sys.exit(app.exec_())
