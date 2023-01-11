from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from pyModbusTCP.client import ModbusClient
from threading import Thread
from time import sleep
from datetime import datetime
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder, Endian
# from modelDataCLP import DadoCLP
# from db import Session


class SupervisorioHandler(BoxLayout):
    pass

    _is_supervisorio_on = False

    def __init__(self, server_ip, modbus_port, scan_time=1):
        super().__init__()

        self._modbus_client = ModbusClient(host=server_ip, port=modbus_port)
        self._scan_time = scan_time
        self._real_time_data = {}

    def turn_supervisorio_on(self):
        self._is_supervisorio_on = self.ids.supervisorio.active

        try:
            Window.set_system_cursor("wait")
            self._modbus_client.open()
            Window.set_system_cursor("arrow")

            if self._modbus_client.is_open:
                print("Conexão bem sucedida com o MODBUS")
                self.update_in_real_time_thread = Thread(
                    target=self.updater)
                self.update_in_real_time_thread.start()

                print("Iniciou a thread")
            else:
                print("FALHA NA CONEXAO")
        except Exception as e:
            print("Erro: ", e.args)

    def updater(self):
        try:
            while self._is_supervisorio_on:
                self.read_data_from_CLP()
                self.update_GUI()
                self.insert_data_to_database()
                sleep(self._scan_time/1000)
        except Exception as e:
            print("Erro: ", e.args)

    def read_data_from_CLP(self):
        self._real_time_data['timestamp'] = datetime.now()
        self._real_time_data['temperatura_enrolamento_r'] = self.lerFloat(
            700) * 0.1
        self._real_time_data['temperatura_enrolamento_s'] = self.lerFloat(
            702) * 0.1
        self._real_time_data['temperatura_enrolamento_t'] = self.lerFloat(
            704) * 0.1
        self._real_time_data['temperatura_carcaca'] = self.lerFloat(
            706) * 0.1
        self._real_time_data['frequencia_motor_rpm'] = self.lerFloat(
            884)
        self._real_time_data['torque_ventilador_radial'] = self.lerFloat(
            1422)
        self._real_time_data['torque_ventilador_axial'] = self.lerFloat(
            1424)
        self._real_time_data['vazao_ar'] = self.lerFloat(
            714)
        self._real_time_data['velocidade_ar'] = self.lerFloat(
            712)
        self._real_time_data['temperatura_ar'] = self.lerFloat(
            710)
        self._real_time_data['temperatura_tubo_azul'] = self.lerFloat(
            1220) * 0.1
        self._real_time_data['temperatura_tubo_vermelho'] = self.lerFloat(
            1218) * 0.1

    def lerFloat(self, addr):
        num_float = self._modbus_client.read_holding_registers(addr, 2)

        decorder = BinaryPayloadDecoder.fromRegisters(
            num_float, Endian.Big, Endian.Little)
        decoded_float = decorder.decode_32bit_float()
        return decoded_float

    def update_GUI(self):
        self.ids.temp_enrolamento_r.text = str(
            self._real_time_data['temperatura_enrolamento_r'])

    def insert_data_to_database(self):
        pass
    #         # registro = DadoCLP(**self._real_time_data)
    #         # Session.add(registro)
    #         # Session.commit()
