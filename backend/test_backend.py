"""Testes automatizados básicos das rotas de usuário e conversa."""
import os
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import models
from database import Base, get_db
from main import app


_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(bind=_test_engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=_test_engine)


def override_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


def test_usuario_conversa_e_validacao_fk():
    with TestClient(app) as client:
        usuario = client.post("/usuarios", json={
            "tipo_usuario": "familiar",
            "idade_faixa": "35-44",
            "objetivo_atendimento": "Buscar orientação",
            "consentimento_dados": "sim",
        })
        assert usuario.status_code == 201, usuario.text
        uid = usuario.json()["id_usuario"]

        conversa = client.post("/conversas", json={
            "id_usuario": uid,
            "data_hora": "2026-10-19T10:30:00",
            "pergunta_usuario": "Como posso apoiar meu familiar?",
            "categoria_pergunta": "orientacao_familiar",
            "nivel_de_urgencia": "baixo",
            "necessita_profissional": "sim",
            "encaminhamento_realizado": "nao",
        })
        assert conversa.status_code == 201, conversa.text
        assert conversa.json()["usuario_tipo"] == "familiar"

        lista = client.get("/conversas")
        assert lista.status_code == 200
        assert any(c["id_usuario"] == uid for c in lista.json())

        fk_invalida = client.post("/conversas", json={
            "id_usuario": 999999,
            "data_hora": "2026-10-19T10:30:00",
            "pergunta_usuario": "Teste de relacionamento",
            "categoria_pergunta": "teste",
        })
        assert fk_invalida.status_code == 404

        inexistente = client.get("/usuarios/999999")
        assert inexistente.status_code == 404


app.dependency_overrides.clear()
