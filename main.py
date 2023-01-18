from kivy.app import App
from kivy.core.window import Window
from kivy.lang import Builder
from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import encode_ieee, long_list_to_word
from threading import Thread
from time import sleep
from datetime import datetime
from pymodbus.payload import BinaryPayloadDecoder, Endian
from modelDataCLP import DadoCLP
from db import Base, Session, engine
from kivy.uix.screenmanager import ScreenManager, Screen

modbus_client = ModbusClient(host='192.168.0.12', port=502)


class Principal(Screen):
    _is_supervisorio_on = False
    _is_compressor_on = False

    def __init__(self, **kw):
        super().__init__(**kw)

        self._scan_time = 1
        self._real_time_data = {}
        self._session = Session()
        Base.metadata.create_all(engine)

    def turn_supervisorio_on(self):
        try:
            Window.set_system_cursor("wait")
            modbus_client.open()
            Window.set_system_cursor("arrow")

            if modbus_client.is_open:
                print("Conexao bem sucedida com o MODBUS")
                self._is_supervisorio_on = True

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
                # self.update_GUI()
                # self.insert_data_to_database()
                sleep(self._scan_time/1000)
        except Exception as e:
            print("Erro: ", e.args)

    def read_data_from_CLP(self):
        self._real_time_data['timestamp'] = datetime.now()
        self._real_time_data['temperatura_enrolamento_r'] = self.lerFloat(
            700, 0.1)
        self._real_time_data['temperatura_enrolamento_s'] = self.lerFloat(
            702, 0.1)
        self._real_time_data['temperatura_enrolamento_t'] = self.lerFloat(
            704, 0.1)
        self._real_time_data['temperatura_carcaca'] = self.lerFloat(706, 0.1)
        self._real_time_data['frequencia_motor_rpm'] = self.lerFloat(884)
        self._real_time_data['torque_ventilador_radial'] = self.lerFloat(1422)
        self._real_time_data['torque_ventilador_axial'] = self.lerFloat(1424)
        self._real_time_data['vazao_ar'] = self.lerFloat(714)
        self._real_time_data['velocidade_ar'] = self.lerFloat(712)
        self._real_time_data['temperatura_ar'] = self.lerFloat(710)
        self._real_time_data['temperatura_tubo_azul'] = self.lerFloat(
            1220, 0.1)
        self._real_time_data['temperatura_tubo_vermelho'] = self.lerFloat(
            1218, 0.1)

    def ligarMotor(self):
        tipo_partida = self.lerInteiro(1324)

        if tipo_partida == 1:  # soft
            self.escreverInteiro(1316, 1)  # ligar soft
        elif tipo_partida == 2:
            self.escreverInteiro(1312, 1)  # ligar inversor
        else:
            self.escreverInteiro(1319, 1)  # ligar direta

    def lerTipoCompressor(self):
        valor16bits = self.lerInteiro(1328)
        lista_de_bits = [int(i) for i in list('{0:016b}'.format(valor16bits))]

        bit_tipo_compressor = lista_de_bits[1]
        if bit_tipo_compressor == 0:
            return 'scroll'
        else:
            return 'hermetico'

    def is_compressor_on(self):
        return self._is_compressor_on

    def comutarCompressor(self):
        if self._is_compressor_on:
            self.desligar_compressor()
            self._is_compressor_on = False
        else:
            self.ligar_compressor()
            self._is_compressor_on = True

    def desligar_compressor(self):
        valor16bits = modbus_client.read_holding_register(1329, 1)[0]
        lista_de_bits = [int(i) for i in list('{0:016b}'.format(valor16bits))]

        lista_de_bits[0] = 0

        valor_a_ser_inserido = int("".join(str(i) for i in lista_de_bits), 2)
        modbus_client.write_single_register(1329, valor_a_ser_inserido)

    def ligar_compressor(self):
        valor16bits = modbus_client.read_holding_register(1328, 1)[0]
        lista_de_bits = [int(i) for i in list('{0:016b}'.format(valor16bits))]

        lista_de_bits[4] = 1

        valor_a_ser_inserido = int("".join(str(i) for i in lista_de_bits), 2)
        modbus_client.write_single_register(1328, valor_a_ser_inserido)

    def update_GUI(self):
        self.ids.temp_enrolamento_r.text = str(
            self._real_time_data['temperatura_enrolamento_r'])
        self.ids.temp_enrolamento_s.text = str(
            self._real_time_data['temperatura_enrolamento_s'])
        self.ids.temp_enrolamento_t.text = str(
            self._real_time_data['temperatura_enrolamento_t'])
        self.ids.temp_carcaca.text = str(
            self._real_time_data['temperatura_carcaca'])
        self.ids.freq_motor_rpm.text = str(
            self._real_time_data['frequencia_motor_rpm'])
        self.ids.torque_vent_radial.text = str(
            self._real_time_data['torque_ventilador_radial'])
        self.ids.vel_ar.text = str(
            self._real_time_data['velocidade_ar'])
        self.ids.temp_ar.text = str(
            self._real_time_data['temperatura_ar'])
        self.ids.temp_tub_azul.text = str(
            self._real_time_data['temperatura_tubo_azul'])
        self.ids.temp_tub_vermelho.text = str(
            self._real_time_data['temperatura_tubo_vermelho'])

        self.ids.freq_motor_rpm.text = str(
            self._real_time_data['torque_ventilador_axial'])
        self.ids.freq_motor_rpm.text = str(
            self._real_time_data['vazao_ar'])

    def insert_data_to_database(self):
        registro = DadoCLP(**self._real_time_data)

        self._session.add(registro)
        self._session.commit()

    def lerFloat(self, addr, multiplier=1):
        num_float = modbus_client.read_holding_registers(addr, 2)

        decorder = BinaryPayloadDecoder.fromRegisters(
            num_float, Endian.Big, Endian.Little)
        decoded_float = decorder.decode_32bit_float()
        return round(decoded_float * multiplier, 2)

    def lerInteiro(self, addr):
        return modbus_client.read_holding_registers(addr, 1)[0]

    def escreverInteiro(self, addr, valor):
        modbus_client.write_single_register(addr, valor)


class Configuracao(Screen):
    _config = {}

    # TODO: Deixar as configs pre setadas com oq ta escrito no CLP. Init n funciona. Precisaria ter a mesma função em todas as telas?

    def salvarConfiguracao(self):
        obteve_sucesso = self.pegar_e_validar_dados_tela()

        if not obteve_sucesso:
            print("entrei no nao sucesso")
            return

        print("Config", self._config)

        self.escrever_config_CLP()
        self.mudar_para_tela_principal()

    def pegar_e_validar_dados_tela(self):
        try:
            self._config['compressor_scroll_setado'] = self.ids.scroll.active
            self._config['compressor_hermetico_setado'] = self.ids.hermetico.active

            self._config['partida_direta_setada'] = self.ids.direta.active
            self._config['partida_soft_setada'] = self.ids.soft.active
            self._config['partida_inversor_setada'] = self.ids.inversor.active

            self._config['tempo_aceleracao'] = float(
                self.ids.temp_aceleracao.text)
            self._config['tempo_desaceleracao'] = float(
                self.ids.temp_desaceleracao.text)
            self._config['velocidade_inversor'] = float(
                self.ids.velocidade_inversor.text)

            if self._config['velocidade_inversor'] < 0 or self._config['velocidade_inversor'] > 60:
                # TODO: aparecer label de erro com escrito "Velocidade inversor deve ser um numero real entre 0 e 60"
                return False

            return True
        except Exception as e:
            # TODO: aparecer label de erro com escrito e.args
            return False

    def escrever_config_CLP(self):
        print("to escrevendo config no CLP")
        self.desligar_motores()
        sleep(1)

        self.escrever_config_partidas()
        self.escrever_tipo_compressores()

    def escrever_config_partidas(self):
        print("to escrevendo config das partidas")

        if self._config['partida_inversor_setada']:
            self.escrever_inteiro(1324, 2)
            self.escreverFloat(1314, self._config['tempo_aceleracao'])
            self.escreverFloat(1315, self._config['tempo_desaceleracao'])
            self.escreverFloat(1313, self._config['velocidade_inversor'])
        elif self._config['partida_soft_setada']:
            self.escrever_inteiro(1324, 1)
            self.escreverFloat(1317, self._config['tempo_aceleracao'])
            self.escreverFloat(1318, self._config['tempo_desaceleracao'])
        else:
            # A partida default vai ser a direta
            self.escrever_inteiro(1324, 3)

    def escrever_tipo_compressores(self):
        print("to escrevendo tipo dos compressores")
        valor16bits = modbus_client.read_holding_register(1328, 1)[0]
        lista_de_bits = [int(i) for i in list('{0:016b}'.format(valor16bits))]

        if self._config['compressor_scroll_setado']:
            lista_de_bits[1] = 0
        else:
            lista_de_bits[1] = 1  # default é o hermetico

        valor_a_ser_inserido = int("".join(str(i) for i in lista_de_bits), 2)
        modbus_client.write_single_register(1328, valor_a_ser_inserido)

    def desligar_motores(self):
        print("Desligando motores")
        self.escrever_inteiro(1312, 0)  # direta
        self.escrever_inteiro(1319, 0)  # inversor
        self.escrever_inteiro(1316, 0)  # soft

    def mudar_tela_principal(self):
        print("to mudando_tela_principal")
        # TODO: mudar de tela

    def escreverFloat(self, addr, valor):
        valor_tratado = encode_ieee(valor)

        return modbus_client.write_multiple_registers(addr, long_list_to_word([valor_tratado]))

    def escrever_inteiro(self, addr, valor):
        modbus_client.write_single_register(addr, valor)


class Graficos(Screen):
    pass


class Dados(Screen):
    pass


class GraficosTR(Screen):
    pass


class WindowManager(ScreenManager):
    pass


kv = Builder.load_file('supervisorio.kv')


class Supervisorio(App):
    def build(self):
        return kv


if __name__ == '__main__':
    Window.size = (1200, 600)
    Window.fullscreen = False
    Supervisorio().run()

# def get_data_from_database(self):
#     init = input(
#         "Digite o horario inicial para a busca (DD/MM/AAAA HH:MM:SS):")
#     final = input(
#         "Digite o horario final para a busca (DD/MM/AAAA HH:MM:SS):")
#     init = datetime.strptime(init, '%d/%m/%Y %H:%M:%S')
#     final = datetime.strptime(final, '%d/%m/%Y %H:%M:%S')
#     self._lock.acquire()
#     results = self._session.query(DadoCLP).filter(
#         DadoCLP.timestamp.between(init, final)).all()
#     self._lock.release()
#     results = self._session.query(DadoCLP).filter(
#         DadoCLP.timestamp.between(init, final)).all()
