"""Schemas Pydantic de entrada e saída da API."""
from pydantic import BaseModel, ConfigDict, Field


class UsuarioCreate(BaseModel):
    tipo_usuario: str = Field(min_length=2, max_length=80)
    idade_faixa: str | None = Field(default=None, max_length=40)
    objetivo_atendimento: str = Field(min_length=2, max_length=250)
    consentimento_dados: str = Field(default="pendente", max_length=30)


class UsuarioResponse(BaseModel):
    id_usuario: int
    tipo_usuario: str
    idade_faixa: str | None
    objetivo_atendimento: str
    consentimento_dados: str
    model_config = ConfigDict(from_attributes=True)


class ConversaCreate(BaseModel):
    id_usuario: int = Field(gt=0)
    data_hora: str = Field(min_length=1, max_length=40, description="Data/hora em texto, de preferência ISO 8601")
    pergunta_usuario: str = Field(min_length=1, max_length=4000)
    categoria_pergunta: str = Field(min_length=1, max_length=100)
    nivel_de_urgencia: str = Field(default="não informado", max_length=40)
    necessita_profissional: str = Field(default="não", max_length=10)
    encaminhamento_realizado: str = Field(default="não", max_length=10)


class ConversaResponse(BaseModel):
    id_conversa: int
    id_usuario: int
    data_hora: str
    pergunta_usuario: str
    categoria_pergunta: str
    nivel_de_urgencia: str
    necessita_profissional: str
    encaminhamento_realizado: str
    usuario_tipo: str


class ConversaBasicaResponse(BaseModel):
    id_conversa: int
    id_usuario: int
    data_hora: str
    pergunta_usuario: str
    categoria_pergunta: str
    nivel_de_urgencia: str
    necessita_profissional: str
    encaminhamento_realizado: str
    model_config = ConfigDict(from_attributes=True)
