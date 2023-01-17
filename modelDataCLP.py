from db import Base
from sqlalchemy import Column, Integer, DateTime, REAL


class DadoCLP(Base):
    __tablename__ = 'dados_clp'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)  # /10
    temperatura_enrolamento_r = Column(REAL)  # /10
    temperatura_enrolamento_s = Column(REAL)  # /10
    temperatura_enrolamento_t = Column(REAL)  # float
    temperatura_carcaca = Column(REAL)  # float
    frequencia_motor_rpm = Column(REAL)  # float
    torque_ventilador_radial = Column(REAL)  # float
    torque_ventilador_axial = Column(REAL)  # float
    vazao_ar = Column(REAL)  # float
    velocidade_ar = Column(REAL)  # float
    temperatura_ar = Column(REAL)  # float
    temperatura_tubo_azul = Column(REAL)  # /10
    temperatura_tubo_vermelho = Column(REAL)  # /10
