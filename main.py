from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QRadioButton, QCheckBox
from PyQt5.QtGui import QPixmap
from PyQt5.Qt import Qt
import requests
import sys
import os
import json

SCREEN_SIZE = [600, 450]


class GeocoderAPI:
    _server = 'http://geocode-maps.yandex.ru/1.x/'
    __apikey = '40d1649f-0493-4b70-98ba-98533de7710b'

    @staticmethod
    def get_toponym(toponym_to_find):
        geocoder_params = {
            "apikey": GeocoderAPI.__apikey,
            "geocode": toponym_to_find,
            "format": "json"}

        response = requests.get(GeocoderAPI._server, params=geocoder_params)
        if response is None:
            raise Exception(response.reason)
        json_response = response.json()
        toponym = json_response["response"]["GeoObjectCollection"][
            "featureMember"][0]["GeoObject"]
        return toponym

    @staticmethod
    def get_spn(toponym_to_find=None, cornera=None, cornerb=None) -> list:
        if toponym_to_find is not None:
            toponym = GeocoderAPI.get_toponym(toponym_to_find)
            toponym_enevelope = toponym["boundedBy"]["Envelope"]
            toponym_lower_corner = list(map(float, toponym_enevelope["lowerCorner"].split()))
            toponym_upper_corner = list(map(float, toponym_enevelope["upperCorner"].split()))
            return [abs(toponym_upper_corner[0] - toponym_lower_corner[0]),
                    abs(toponym_upper_corner[1] - toponym_lower_corner[1])]
        else:
            toponym_lower_corner = list(map(float, cornera.split(',')))
            toponym_upper_corner = list(map(float, cornerb.split(',')))
            return [1.9 * abs(toponym_upper_corner[0] - toponym_lower_corner[0]),
                    1.9 * abs(toponym_upper_corner[1] - toponym_lower_corner[1])]

    @staticmethod
    def get_coordinates(toponym_to_find) -> str:
        toponym = GeocoderAPI.get_toponym(toponym_to_find)
        return toponym["Point"]["pos"]

    @staticmethod
    def get_longitude_and_lattitude(toponym_to_find) -> list:
        return list(map(float, GeocoderAPI.get_coordinates(toponym_to_find).split(" ")))


class StaticMapAPI:
    map_file = 'map.png'
    map_file_for_sat = 'map.jpg'
    _server = 'https://static-maps.yandex.ru/1.x/'
    ll = [37.620070, 55.753630]
    size = [600, 450]
    l = 'map'
    spn = [0.002, 0.002]
    MAX_SPN = 65.536
    MIN_SPN = 0.001
    pixmap = None
    pt = ''

    def set_params(self, **params):
        self.l = params.get('l', self.l)
        self.spn = params.get('spn', self.spn)
        self.size = params.get('size', self.size)
        self.ll = params.get('ll', self.ll)
        self.pt = params.get('pt', self.pt)

    def update_map(self):
        params = {
            'll': f'{self.ll[0]},{self.ll[1]}',
            'size': f'{self.size[0]},{self.size[1]}',
            'l': self.l,
            'spn': f'{self.spn[0]},{self.spn[1]}'
        }
        if self.pt:
            params['pt'] = self.pt
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
        self.spn[0] /= 2
        self.spn[1] /= 2
        if self.spn[0] < self.MIN_SPN:
            self.spn[0] = self.MIN_SPN
        if self.spn[1] < self.MIN_SPN:
            self.spn[1] = self.MIN_SPN

    def spn_out(self):
        self.spn[0] *= 2
        self.spn[1] *= 2
        if self.spn[0] > self.MAX_SPN:
            self.spn[0] = self.MAX_SPN
        if self.spn[1] > self.MAX_SPN:
            self.spn[1] = self.MAX_SPN

    def move(self, x=0, y=0):
        self.ll[0] += x * self.spn[0]
        self.ll[1] += y * self.spn[1]


class MapsAPI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.static_map_api = StaticMapAPI()
        self.initUI()

        [btn.clicked.connect(self.update_map) for btn in self.mode_buttons]
        self.btn_search_obj.clicked.connect(self.search_obj)
        self.btn_discharge_obj.clicked.connect(self.discharge_search)

    def initUI(self):
        self.setWindowTitle('Maps API')
        self.setFixedSize(*SCREEN_SIZE)
        self.label_map = QLabel(self)
        self.label_map.move(100, 0)
        self.mode_buttons = [QRadioButton(text, self) for text in ['map', 'sat', 'sat,skl']]
        self.mode_buttons[0].setChecked(True)
        [elem.move(10, 10 + 30 * i) for i, elem in enumerate(self.mode_buttons)]

        self.line_edit_search = QLineEdit(self)
        self.line_edit_search.move(0, 100)

        self.btn_search_obj = QPushButton('Искать', self)
        self.btn_search_obj.move(0, 130)

        self.btn_discharge_obj = QPushButton('Сброс', self)
        self.btn_discharge_obj.move(0, 160)

        self.check_box_postcode = QCheckBox('Postcode', self)
        self.check_box_postcode.move(10, 190)

        self.update_map()

    def update_map(self):
        self.static_map_api.set_params(l=[btn.text() for btn in self.mode_buttons if btn.isChecked()][0])
        self.label_map.setPixmap(self.static_map_api.get_pixmap(update=True))
        self.label_map.resize(*self.static_map_api.get_size())

    def search_obj(self):
        try:
            toponym_to_find = self.line_edit_search.text()
            toponym = GeocoderAPI.get_toponym(toponym_to_find)
            address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
            postcode = None
            try:
                # print(json.dumps(toponym, ensure_ascii=False, indent=4))
                postcode = toponym["metaDataProperty"]["GeocoderMetaData"]["AddressDetails"]["Country"][
                    "AdministrativeArea"]["Locality"]["Thoroughfare"]["Premise"]["PostalCode"]["PostalCodeNumber"]
            except Exception as E:
                # print(E.__class__.__name__, E)
                pass
            self.setWindowTitle(
                f'Адреc: {address}{f", {postcode}" if postcode and self.check_box_postcode.isChecked() else ""}')
            ll = GeocoderAPI.get_longitude_and_lattitude(toponym_to_find)
            spn = GeocoderAPI.get_spn(toponym_to_find)
            self.static_map_api.set_params(ll=ll, pt=f'{ll[0]},{ll[1]}', spn=spn)
        except IndexError as E:
            self.discharge_search()
            self.setWindowTitle('Не найдено ничего')
        except Exception as E:
            print(E)
        else:
            self.update_map()

    def discharge_search(self):
        self.setWindowTitle('MapsAPI')
        self.static_map_api.set_params(pt=None)
        self.line_edit_search.setText('')
        self.update_map()

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
