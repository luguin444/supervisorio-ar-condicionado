from db import Base
from db import engine
from sqlalchemy import Column , Integer, DateTime, real
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class DadoCLP(Base):
    _tablename_ = 'dadosclp'

    id = Column(Integer,primary_key = True)
    timestamp = Column(DateTime) # /10
    temperatura_enrolamento_r = Column(real) # /10
    temperatura_enrolamento_s = Column(real) # /10
    temperatura_enrolamento_t = Column(real)  # float
    temperatura_carcaca = Column(real) # float
    frequencia_motor_rpm = Column(real)# float
    torque_ventilador_radial = Column(real)# float
    torque_ventilador_axial = Column(real) # float
    vazao_ar = Column(real) # float
    velocidade_ar = Column(real) # float
    temperatura_ar = Column(real) # float
    temperatura_tubo_azul = Column(real) # /10
    temperatura_tubo_vermelho = Column(real) # /10

    Base.metadata.create_all(engine)