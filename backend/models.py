"""Models ORM alinhados às entidades de usuários e conversas do ReViver."""
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    tipo_usuario = Column(String(80), nullable=False)
    idade_faixa = Column(String(40), nullable=True)
    objetivo_atendimento = Column(String(250), nullable=False)
    consentimento_dados = Column(String(30), nullable=False, default="pendente")

    conversas = relationship("Conversa", back_populates="usuario", cascade="all, delete-orphan")


class Conversa(Base):
    __tablename__ = "conversas"

    id_conversa = Column(Integer, primary_key=True, index=True)
    id_usuario = Column(Integer, ForeignKey("usuarios.id_usuario", ondelete="CASCADE"), nullable=False, index=True)
    data_hora = Column(String(40), nullable=False)
    pergunta_usuario = Column(Text, nullable=False)
    categoria_pergunta = Column(String(100), nullable=False)
    nivel_de_urgencia = Column(String(40), nullable=False, default="não informado")
    necessita_profissional = Column(String(10), nullable=False, default="não")
    encaminhamento_realizado = Column(String(10), nullable=False, default="não")

    usuario = relationship("Usuario", back_populates="conversas")
