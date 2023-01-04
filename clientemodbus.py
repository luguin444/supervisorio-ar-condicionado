from pyModbusTCP.client import ModbusClient
from pyModbusTCP.utils import encode_ieee, long_list_to_word, word_list_to_long, decode_ieee
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from time import sleep
from pymodbus.payload import Endian


class ClienteMODBUS():
    def __init__(self, server_ip, porta, scan_time=1):
        self._cliente = ModbusClient(host=server_ip, port=porta)
        self._scan_time = scan_time

    def atendimento(self):
        self._cliente.open()
        try:
            atendimento = True
            while atendimento:
                sel = input(
                    "Deseja realizar uma leitura, escrita ou configuração? (1- Leitura | 2- Escrita | 3- Configuração |4- Sair): ")
                if sel == '1':
                    tipo = input(
                        """Qual tipo de dado deseja ler? (1- Holding Register) |2- Coil |3- Input Register |4- Discrete Input) :""")

                    addr = input(f"Digite o endereço da tabela MODBUS: ")
                    nvezes = input("Digite o número de vezes que deseja ler: ")
                    tipagem = "1"
                    if tipo == "1":
                        tipagem = input(
                            "Qual a tipagem do seu dado: (1- Inteiro |2-Float |3-String ): ")

                    for i in range(0, int(nvezes)):
                        if tipagem == "1":
                            print(
                                f"Leitura {i+1}: {self.lerDado(int(tipo), int(addr))}")
                        elif tipagem == "2":
                            print(
                                f"Leitura {i+1}: {self.lerFloat(int(addr))}")
                        elif tipagem == "3":
                            print(
                                f"Leitura {i+1}: {self.lerString(int(addr))}")

                        sleep(self._scan_time)
                elif sel == '2':
                    addr = input(f"Digite o endereço da tabela MODBUS: ")
                    tipagem = input(
                        f"Digite o tipagem do input: (1- inteiro |2- float |3- string): ")
                    if tipagem == '1':
                        tipo = input(
                            """Qual tipo de dado deseja escrever? (1- Holding Register) |2- Coil) :""")
                        valor = input(f"Digite o valor que deseja escrever: ")
                        self.escreveDado(int(tipo), int(addr), int(valor))
                    elif tipagem == '2':
                        valor = input(f"Digite o valor que deseja escrever: ")
                        self.escreveFloat(int(addr), float(valor))
                    elif tipagem == '3':
                        valor = input(f"Digite a string que deseja escrever: ")
                        self.escreveString(int(addr), valor)

                elif sel == '3':
                    scant = input("Digite o tempo de varredura desejado [s]: ")
                    self._scan_time = float(scant)

                elif sel == '4':
                    self._cliente.close()
                    atendimento = False
                else:
                    print("Seleção inválida")
        except Exception as e:
            print('Erro no atendimento: ', e)

    def lerDado(self, tipo, addr):
        if tipo == 1:
            return self._cliente.read_holding_registers(addr, 1)[0]

        if tipo == 2:
            return self._cliente.read_coils(addr, 1)[0]

        if tipo == 1:
            return self._cliente.read_input_registers(addr, 1)[0]

        if tipo == 1:
            return self._cliente.read_discrete_inputs(addr, 1)[0]

    def escreveDado(self, tipo, addr, valor):
        """
        Método para a escrita de dados na Tabela MODBUS
        """
        if tipo == 1:
            return self._cliente.write_single_register(addr, valor)

        if tipo == 2:
            return self._cliente.write_single_coil(addr, valor)

    def escreveFloat(self, addr, valor):
        valor_tratado = encode_ieee(valor)

        return self._cliente.write_multiple_registers(addr, long_list_to_word([valor_tratado]))

    def lerFloat(self, addr):
        num_float = self._cliente.read_holding_registers(addr, 2)

        decorder = BinaryPayloadDecoder.fromRegisters(
            num_float, Endian.Big, Endian.Little)
        decoded_float = decorder.decode_32bit_float()
        return decoded_float

    def escreveString(self, addr, valor):
        builder = BinaryPayloadBuilder()
        builder.add_string(valor)
        payload = builder.to_registers()

        return self._cliente.write_multiple_registers(addr, payload)

    def lerString(self, addr):
        list_string = self._cliente.read_holding_registers(addr, 2)

        decoder = BinaryPayloadDecoder.fromRegisters(list_string)
        string = str(decoder.decode_string(8))
        string_splitada = string.split("b")[1]

        return string_splitada
