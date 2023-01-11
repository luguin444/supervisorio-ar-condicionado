from supervisorioHandler import SupervisorioHandler
from kivy.app import App
from kivy.core.window import Window


class Supervisorio(App):
    def build(self):
        server_ip = '192.168.0.12'
        modbus_port = 502

        return SupervisorioHandler(server_ip, modbus_port)


if __name__ == '__main__':
    Window.size = (1000, 600)
    Window.fullscreen = False
    Supervisorio().run()
