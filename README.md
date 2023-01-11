relation_from_modbus_addresses_with_database_colunms = {
'temperatura_enrolamento_r': 700,
'temperatura_enrolamento_s': 702,
'temperatura_enrolamento_t': 704,
'temperatura_carcaca': 706,
'frequencia_motor_rpm': 884,
'torque_ventilador_radial': 1422,
'torque_ventilador_axial': 1424,
'vazao_ar': 714,
'velocidade_ar': 712,
'temperatura_ar': 710,
'temperatura_tubo_azul': 1220,
'temperatura_tubo_vermelho': 1218,
}

Para rodar o projeto

Bibliotecas necessárias:
pip install kivy pyModbusTCP sqlalchemy pymodbus

Rodar no terminal:
python main.py
