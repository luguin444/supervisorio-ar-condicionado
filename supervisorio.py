from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from pyModbusTCP.client import ModbusClient
from threading import Thread
from time import sleep
from datetime import datetime
from modelDataCLP import DadoCLP
from db import Session

class Supervisorio(BoxLayout):

  _is_supervisorio_on = False

  def __init__(self, server_ip, modbus_port, scan_time=1):
    super().__init__()

    self._modbus_client = ModbusClient(host=server_ip, port=modbus_port)
    self._scan_time = scan_time
    self._real_time_data = {}

  def turn_supervisorio_on(self):
    try:
        Window.set_system_cursor("wait")
        self._modbus_client.open()
        Window.set_system_cursor("arrow")
        self._is_supervisorio_on = True
        if self._modbus_client.is_open():
          self.update_in_real_time_thread = Thread(target=self.updater)
          self.update_in_real_time_thread.start()
        else:
          print("FALHA NA CONEXÃO")
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
      self._real_time_data['temperatura_enrolamento_r'] = 10 * self._modbus_client.read_holding_registers(700, 1)[0]
      self._real_time_data['temperatura_enrolamento_s'] = 10 * self._modbus_client.read_holding_registers(702, 1)[0]
      self._real_time_data['temperatura_enrolamento_t'] = 10 * self._modbus_client.read_holding_registers(704, 1)[0]
      self._real_time_data['temperatura_carcaca'] = 10 * self._modbus_client.read_holding_registers(706, 1)[0]
      self._real_time_data['frequencia_motor_rpm'] = self._modbus_client.read_holding_registers(884, 1)[0]
      self._real_time_data['torque_ventilador_radial'] = self._modbus_client.read_holding_registers(1422, 1)[0]
      self._real_time_data['torque_ventilador_axial'] = self._modbus_client.read_holding_registers(1424, 1)[0]
      self._real_time_data['vazao_ar'] = self._modbus_client.read_holding_registers(714, 1)[0]
      self._real_time_data['velocidade_ar'] = self._modbus_client.read_holding_registers(712, 1)[0]
      self._real_time_data['temperatura_ar'] = self._modbus_client.read_holding_registers(710, 1)[0]
      self._real_time_data['temperatura_tubo_azul'] = 10 * self._modbus_client.read_holding_registers(1220, 1)[0]
      self._real_time_data['temperatura_tubo_vermelho'] = 10 * self._modbus_client.read_holding_registers(1218, 1)[0]

    def update_GUI(self):
      # atualizar a interface baseada nos IDs do .kv. Por exemplo atualizar a temperatura do tubo vermelho
      pass

    def insert_data_to_database(self):
      registro = DadoCLP(**self._real_time_data)
      Session.add(registro)
      Session.commit()