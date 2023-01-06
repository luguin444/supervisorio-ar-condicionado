from supervisorio import Supervisorio
from kivy.app import App

class MainApp(App):
    def build(self):
        server_ip = '192.168.0.12'
        modbus_port = 502

        self._main_screen = Supervisorio(server_ip, modbus_port)

        return self._main_screen

if __name__ == '__main__':
    MainApp().run()
