"""Aplicação principal do ReViver: CRUD básico e análise dos CSVs."""
from contextlib import asynccontextmanager
from pathlib import Path
import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

import models
import schemas
from database import Base, engine, get_db
import analise_csv


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas se ainda não existirem. Não apaga dados existentes.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API ReViver — Backend e Análise de Dados",
    description="Cadastro e consulta de usuários e conversas, com relacionamento por chave estrangeira e rotas de análise dos CSVs.",
    version="2.0.0",
    lifespan=lifespan,
)


def conversation_output(conversa: models.Conversa) -> dict:
    return {
        "id_conversa": conversa.id_conversa,
        "id_usuario": conversa.id_usuario,
        "data_hora": conversa.data_hora,
        "pergunta_usuario": conversa.pergunta_usuario,
        "categoria_pergunta": conversa.categoria_pergunta,
        "nivel_de_urgencia": conversa.nivel_de_urgencia,
        "necessita_profissional": conversa.necessita_profissional,
        "encaminhamento_realizado": conversa.encaminhamento_realizado,
        "usuario_tipo": conversa.usuario.tipo_usuario,
    }


@app.get("/", tags=["Início"])
def inicio():
    return {"projeto": "ReViver", "status": "online", "documentacao": "/docs", "banco": "SQLAlchemy"}


# Entidade 1: Usuário (PK id_usuario)
@app.post("/usuarios", response_model=schemas.UsuarioResponse, status_code=201, tags=["Usuários"])
def criar_usuario(dados: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario = models.Usuario(**dados.model_dump())
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@app.get("/usuarios", response_model=list[schemas.UsuarioResponse], tags=["Usuários"])
def listar_usuarios(skip: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    return db.query(models.Usuario).order_by(models.Usuario.id_usuario).offset(skip).limit(limit).all()


@app.get("/usuarios/{id_usuario}", response_model=schemas.UsuarioResponse, tags=["Usuários"])
def consultar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


# Entidade 2: Conversa (FK id_usuario -> usuarios.id_usuario)
@app.post("/conversas", response_model=schemas.ConversaResponse, status_code=201, tags=["Conversas"])
def criar_conversa(dados: schemas.ConversaCreate, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == dados.id_usuario).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário informado não existe; cadastre o usuário antes da conversa.")
    conversa = models.Conversa(**dados.model_dump())
    db.add(conversa)
    db.commit()
    db.refresh(conversa)
    conversa = db.query(models.Conversa).options(joinedload(models.Conversa.usuario)).filter(models.Conversa.id_conversa == conversa.id_conversa).one()
    return conversation_output(conversa)


@app.get("/conversas", response_model=list[schemas.ConversaResponse], tags=["Conversas"])
def listar_conversas(id_usuario: int | None = Query(default=None, gt=0), skip: int = Query(default=0, ge=0), limit: int = Query(default=100, ge=1, le=500), db: Session = Depends(get_db)):
    consulta = db.query(models.Conversa).options(joinedload(models.Conversa.usuario))
    if id_usuario is not None:
        consulta = consulta.filter(models.Conversa.id_usuario == id_usuario)
    conversas = consulta.order_by(models.Conversa.id_conversa).offset(skip).limit(limit).all()
    return [conversation_output(c) for c in conversas]


@app.get("/conversas/{id_conversa}", response_model=schemas.ConversaResponse, tags=["Conversas"])
def consultar_conversa(id_conversa: int, db: Session = Depends(get_db)):
    conversa = db.query(models.Conversa).options(joinedload(models.Conversa.usuario)).filter(models.Conversa.id_conversa == id_conversa).first()
    if conversa is None:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return conversation_output(conversa)


# Rotas de análise CSV já existentes no projeto, mantidas na mesma API.
def executar_analise(funcao):
    try:
        return funcao()
    except FileNotFoundError as erro:
        raise HTTPException(status_code=503, detail=str(erro)) from erro
    except (ValueError, pd.errors.ParserError, UnicodeError) as erro:
        raise HTTPException(status_code=422, detail=str(erro)) from erro
    except OSError as erro:
        raise HTTPException(status_code=503, detail="Não foi possível ler a fonte CSV.") from erro


@app.get("/analise/resumo", tags=["Análise dos CSVs"])
def consultar_resumo(): return executar_analise(analise_csv.resumo_geral)

@app.get("/analise/qualidade", tags=["Análise dos CSVs"])
def consultar_qualidade(): return executar_analise(analise_csv.resumo_qualidade)

@app.get("/analise/usuarios", tags=["Análise dos CSVs"])
def analisar_usuarios(): return executar_analise(analise_csv.analise_usuarios)

@app.get("/analise/clinicas", tags=["Análise dos CSVs"])
def analisar_clinicas(): return executar_analise(analise_csv.analise_clinicas)

@app.get("/analise/conversas", tags=["Análise dos CSVs"])
def analisar_conversas(): return executar_analise(analise_csv.analise_conversas)

@app.get("/analise/substancias", tags=["Análise dos CSVs"])
def analisar_substancias(): return executar_analise(analise_csv.analise_substancias)

@app.get("/analise/indicadores", tags=["Análise dos CSVs"])
def analisar_indicadores(): return executar_analise(analise_csv.analise_indicadores)

@app.get("/analise/dicionario", tags=["Análise dos CSVs"])
def analisar_dicionario(): return executar_analise(analise_csv.dicionario_dados)
